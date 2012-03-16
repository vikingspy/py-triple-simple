"""
    Creates a Gephi - gexf formatted XML file that visualizes the relationship between instances of different classes
    and the properties that interconnect the instances.

    Known limitations: If an instance has multiple rdf:type (an instance with class) the instance
    will be counted multiple times for each class.

    Written by: Janos G. Hajagos 2011
"""

import pyTripleSimple as pyt
from gexf import GephiGexf
import sys
import os
import pprint

def main(ntriples_file_name):
    ts = pyt.SimpleTripleStore() #Create a triple store object

    try:
        f = open(ntriples_file_name)
    except IOError:
        print("File '%s' could not be read" % os.path.abspath(ntriple_file_name))
        raise

    ts.load_ntriples(f)

    rdf_type = "<" + pyt.common_prefixes["rdf"] + 'type>'

    # Get all classes defined with counts
    classes_result = ts.simple_pattern_match([('a','t','c')],[('t','in',[rdf_type])],['c'])
    class_count = len(classes_result)
    class_sizes = [class_result[1] for class_result in classes_result]
    class_mean = (sum(class_sizes) * 1.0) / class_count
    class_count_normalized = [class_size / class_mean for class_size in class_sizes] # normalize the count by the mean

    # Get all definitions from typed objects
    property_class_results = ts.simple_pattern_match([('a','p','b'),('a','t','ca'),(('b','t','cb'))],[('t','in',[rdf_type]),('p','!=','t')],['p','ca','cb'])
    property_class_relations_count = len(property_class_results)
    property_class_relations_sizes = [property_class_result[1] for property_class_result in property_class_results]
    property_class_mean = (1.0 * sum(property_class_relations_sizes)) / property_class_relations_count
    property_class_count_normalized = [property_class_size / property_class_mean for property_class_size in property_class_relations_sizes]

    gexf_string = ""
    gexf = GephiGexf()
    gexf_string += gexf.xml_header()
    gexf_string += gexf.metadata()
    gexf_string += gexf.open_graph()
    gexf_string += gexf.open_nodes()
    
    class_dict = {}
    for i in range(class_count): # Create nodes
        class_name = classes_result[i][0][0][1:-1]
        class_dict[class_name] = i
        gexf_string += gexf.open_node(i,classes_result[i][0][0][1:-1], size=class_count_normalized[i])
        gexf_string += gexf.close_node()
    gexf_string += gexf.close_nodes()

    property_dict_normalized = {}
    for i in range(property_class_relations_count): # Define edges - Gephi does not support parallel edges
        subject, object = (property_class_results[i][0][1][1:-1], property_class_results[i][0][2][1:-1])
        subject_id = class_dict[subject]
        object_id = class_dict[object]
        relation_pair = (subject_id,object_id)
        if relation_pair in property_dict_normalized:
            property_dict_normalized[relation_pair] += property_class_count_normalized[i] # Cumulate weights
        else:
            property_dict_normalized[relation_pair] = property_class_count_normalized[i]

    gexf_string += gexf.open_edges()
    i = 0
    for relation_pair in property_dict_normalized.keys(): # Output edges
        gexf_string += gexf.open_edge(i,relation_pair[0], relation_pair[1], property_dict_normalized[relation_pair])
        gexf_string += gexf.close_edge()
        i += 1

    gexf_string += gexf.close_edges()
    gexf_string += gexf.close_graph()
    gexf_string += gexf.close_xml()

    # Write out Gephi file
    try:
        gexf_file_name = ntriples_file_name + ".gexf"
        fg = open(gexf_file_name,"w")
    except IOError:
        print("File %s'' could not be written" % os.path.abspath(gexf_file_name))
        raise
    fg.write(gexf_string)
    fg.close()

    #Write out predicate counts to standard output
    print("count\tclass1\tpredicate\tclass2\tclass1Count\tclass2Count")
    for property_class_result in property_class_results:
        count = property_class_result[1]
        property_class_pair = property_class_result[0]
        class_1 = property_class_pair[1][1:-1]
        class_1i = class_dict[class_1]
        predicate = property_class_pair[0][1:-1]
        class_2 = property_class_pair[2][1:-1]
        class_2i = class_dict[class_2]
        class_1n = class_sizes[class_1i]
        class_2n = class_sizes[class_2i]
        print(str(count) + '\t' + class_1 + '\t' + predicate + '\t' + class_2 + '\t' + str(class_1n) + '\t' + str(class_2n))

if __name__ == "__main__":
    main(sys.argv[1])