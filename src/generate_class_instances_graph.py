"""

    Creates a Gephi - gexf formatted XML file that visualizes the relationship between instances of different classes
    and the properties that interconnect the instances.

"""

import pyTripleSimple as pyt
from gexf import GephiGexf
import sys
import pprint


def main(ntriples_file_name):
    ts = pyt.SimpleTripleStore()
    f = open(ntriples_file_name)

    ts.load_ntriples(f)

    rdf_type = "<" + pyt.common_prefixes["rdf"] + 'type>'

    classes_result = ts.simple_pattern_match([('a','t','c')],[('t','in',[rdf_type])],['c'])
    class_count = len(classes_result)
    class_sizes = [class_result[1] for class_result in classes_result]
    class_mean = (sum(class_sizes) * 1.0) / class_count
    class_count_normalized = [class_size/class_mean for class_size in class_sizes]


    property_class_results = ts.simple_pattern_match([('a','p','b'),('a','t','ca'),(('a','t','cb'))],[('t','in',[rdf_type]),('p','!=','t')],['p','ca','cb'])
    property_class_relations_count = len(property_class_results)
    property_class_relations_sizes = [property_class_result[1] for property_class_result in property_class_results]
    property_class_mean = (1.0 * sum(property_class_relations_sizes)) / property_class_relations_count
    property_class_count_normalized = [property_class_size/property_class_mean for property_class_size in property_class_relations_sizes]



    gexf_string = ""
    gexf = GephiGexf()
    gexf_string += gexf.xml_header()
    gexf_string += gexf.metadata()
    gexf_string += gexf.open_graph()


    gexf_string += gexf.open_nodes()
    for i in range(class_count):
        gexf_string += gexf.open_node(classes_result[i][0][0][1:-1],classes_result[i][0][0][1:-1],size=class_count_normalized[i])
        gexf_string += gexf.close_node()
    gexf_string += gexf.close_nodes()

    gexf_string += gexf.open_edges()
    for i in range(property_class_relations_count):
        #print(property_class_result[i][0])
        gexf_string += gexf.open_edge(i,property_class_results[i][0][1][1:-1],property_class_results[i][0][2][1:-1])
        gexf_string += gexf.close_edge()
    gexf_string += gexf.close_edges()

    gexf_string += gexf.close_graph()
    gexf_string += gexf.close_xml()

    print(gexf_string)


def convert_pattern_match_result_to_dict(pattern_result_list):
    converted_dict = {}
    for pattern_result in pattern_result_list:
        converted_dict[pattern_result[0]] = pattern_result[1]
    return converted_dict

if __name__ == "__main__":
    #main("/home/janos/workspace/sbu-mi-vivo-tools/reach_abox_2011-11-13.nt")
    #main("/home/janos/Desktop/rdf/acme.nt")
    main(sys.argv[1])