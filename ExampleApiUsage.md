# Introduction #

The example here creates a graph visualization using [Gephi](http://gephi.org/) of a RDF class structure and the relations between different class instances. This might be of interest if you want to visualize the rich ontological structure of a [VIVO](http://vivoweb.org) site or another RDF graph.

# Details #

The source for this example is in the program [generate\_class\_instances\_graph.py](http://code.google.com/p/py-triple-simple/source/browse/trunk/src/generate_class_instances_graph.py)

First import the pyTripleSimple into pyt the namespace and the [GephiGexf](http://code.google.com/p/py-triple-simple/source/browse/trunk/src/lib/gexf.py) class.
```
import pyTripleSimple as pyt
from gexf import GephiGexf
```

Then initialize the triple store:
```
ts = pyt.SimpleTripleStore() #Create a triple store object
```
and load the N-triples file.
```
f = open(ntriples_file_name)
ts.load_ntriples(f)
```
The N-triples file is now in memory with indices on subjects, predicates, and objects for fast retrieval.

The next step is to get counts on the number of distinct classes using the simple\_pattern\_match method:
```
classes_result = ts.simple_pattern_match([('a','t','c')],[('t','in',[rdf_type])],['c'])
```
Here all triple which have predicate  rdf\_type = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" are matched.  By only asking to return the variable 'c' in the result set the method automatically groups and counts by 'c'.  The results are returned like this:
```
[[('<http://vivoweb.org/ontology/core#Authorship>',), 93779],
 [('<http://xmlns.com/foaf/0.1/Person>',), 31137],
 [('<http://vivoweb.org/ontology/core#Relationship>',), 18353],
 [('<http://vivoweb.org/ontology/core#InformationResource>',), 18274],
 [('<http://purl.org/ontology/bibo/Article>',), 15960],
 [('<http://purl.org/ontology/bibo/AcademicArticle>',), 15089],
 [('<http://purl.obolibrary.org/obo/ERO_0000595>',), 9197],
 [('<http://purl.org/ontology/bibo/Journal>',), 2327],
 [('<http://purl.org/ontology/bibo/Periodical>',), 2314],
 [('<http://purl.org/ontology/bibo/Collection>',), 2314]]
```

A more complicated match which finds the predicate 't' between classes 'ca' and 'cb'
```
property_class_results = ts.simple_pattern_match([('a','p','b'),('a','t','ca'),(('b','t','cb'))],[('t','in',[rdf_type]),('p','!=','t')],['p','ca','cb'])
```
is then used.

By looping through the matched result sets a weight is set to the nodes which represent instances of a class and different predicates which are the edges in the graph.  The final output in Gephi after applying the [Fruchterman-Reingold](http://en.wikipedia.org/wiki/Force-based_algorithms_%28graph_drawing%29) algorithm and some manual aesthetics is:
![http://dl.dropbox.com/u/21690634/reach-nolabels-small.png](http://dl.dropbox.com/u/21690634/reach-nolabels-small.png)
This visualization of the N-triples from a VIVO sites provides a high level overview of the instantiated ontological structure by showing the relative importance of different classes and predicate usage.