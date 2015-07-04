# Introduction #

At the lowest level the semantic Web is built on the [Resource Description Framework](http://en.wikipedia.org/wiki/Resource_Description_Framework) (RDF). RDF is a graph model. It would be expected that a wide range of network analytical tools could be directly applied to a RDF data set. However, most network algorithms assume that a graph does not have parallel edges which the RDF model allows. A graph which has parallel edges is known as a [multigraph](http://en.wikipedia.org/wiki/Multigraph). The challenge is to pull out simpler graphs from the RDF "[hairball](http://eagereyes.org/techniques/graphs-hairball)" for analysis. [Py-Triple-Simple](http://code.google.com/p/py-triple-simple), an experimental pure Python library, can generate a GraphML file from a N-triples file. [GraphML](http://graphml.graphdrawing.org/), an XML based format, is a standard for graph interchange. In this example we will generate a publication co-authorship network from an RDF dump of a [VIVO site](http://vivoweb.org/).

# Details #

To understand how to go from an RDF N-triples file to a GraphML file the code in [generate\_coauthor\_graph.py ](http://code.google.com/p/sbu-mi-vivo-tools/source/browse/trunk/generate_coauthor_graph.py) will be a guide.  The first step will be to open and load the N-triples file into memory.
```
from pyTripleSimple import SimpleTripleStore
ts = SimpleTripleStore()
f = open(file_name)
print("Loading triples")
ts.load_ntriples(f)
f.close()
```
The next step is to initialize the class for converting a SimpleTripleStore instance to a graph model.
```
graph_obj = ExtractGraphFromSimpleTripleStore(ts)
graph_obj.register_label()
```

In order to accurately model information the VIVO ontology is more nuanced than one initially expects. It is not always the case that a single link needs to be traversed but a longer path will need to be followed. To generate a network of faculty who share authorship on  publications we need to traverse several triples and condense the multiple steps into a single leap.
![http://dl.dropbox.com/u/21690634/vivo-authorship-link.png](http://dl.dropbox.com/u/21690634/vivo-authorship-link.png)
In SPARQL this type of construction can be done with a construct statement but we still have the difficulty when we want to analyze the graph using standard tools for network/graph analysis.

The following simple patterns can be used to connect two authors ("a1","a2"):
```
base_patterns = [("a1","p1","c1"),("a1","t","f"),("c1","p2","ar1"),("c2","p2","ar1"),("a2","p1","c2")]
base_restrictions = [("p1","in",["<http://vivoweb.org/ontology/core#authorInAuthorship>"]),
        ("p2", "in", ["<http://vivoweb.org/ontology/core#linkedInformationResource>"]),
        ("c1","!=","c2")]
```
The complete co-author network can get rather large for a well populated VIVO installation, such as, [SUNY REACH](http://reach.suny.edu/). Additional restrictions can be added to reduce the size of the network by excluding authors who are not part of the VIVO site. This is done easily in py-triple-simple because the simple triple patterns are based on Python lists so it is easy to programatically modify the pattern.
```
membership_pattern = ("a2","t","f")
membership_restriction = ("t","in", ["<http://vivoweb.org/ontology/core#hasMemberRole>"])
base_patterns.append(membership_pattern)
base_restrictions.append(membership_restriction)
```
Finally we add the restrictions and pattern to the instance of ExtractGraphFromSimpleTripleStore and call the method for generating the GraphML
```
graph_obj.add_pattern_for_links(base_patterns,base_restrictions,["a1","a2"],"coauthors")
fo = open(graphml_file_name,"w")
graph_obj.translate_into_graphml_file(fo)
```
Now we can import the generated file into software for analyzing graphs.  Mathematica 8 has added a [rich set of functions for analyzing graphs/networks](http://www.wolfram.com/mathematica/new-in-8/graph-and-network-analysis/). The examples below uses some Mathematica library code that I am developing: http://code.google.com/p/network-exploration-analytical-tools/source/browse/trunk/mathematica/neat.m

![http://dl.dropbox.com/u/21690634/neat1.png](http://dl.dropbox.com/u/21690634/neat1.png)
![http://dl.dropbox.com/u/21690634/neat2.png](http://dl.dropbox.com/u/21690634/neat2.png)
![http://dl.dropbox.com/u/21690634/neat3.png](http://dl.dropbox.com/u/21690634/neat3.png)
![http://dl.dropbox.com/u/21690634/neat4.png](http://dl.dropbox.com/u/21690634/neat4.png)

If Mathematica, is not your cup of tea, the GraphML file can be analyzed in [NetworkX](http://networkx.lanl.gov/):

![http://24.media.tumblr.com/tumblr_m2t40gQFAP1r6jx3qo1_1280.png](http://24.media.tumblr.com/tumblr_m2t40gQFAP1r6jx3qo1_1280.png)

...Or if a more interactive environment is preferred [Gephi](http://gephi.org) can be used:
![http://dl.dropbox.com/u/21690634/gephigraph.png](http://dl.dropbox.com/u/21690634/gephigraph.png)