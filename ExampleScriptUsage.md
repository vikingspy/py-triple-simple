# Introduction #

The program/script "py\_triple\_simple.py" provides a command line interface into the pyTripleSimple.py module.
Examples are shown using an ABox dump of a [VIVO site](http://vivoweb.org/) and a free-text index built using the "generate\_free\_text\_triples.py". An automated dump of VIVO can be generated using the [sbu-mi-vivo-tools](http://code.google.com/p/sbu-mi-vivo-tools/) or as a site administrator.

# N-triple statistics #

The simplest usage of the script is to generate elementary statistics on a N-triples file.

```
pypy-c py_triple_simple.py -c statistics -f reach_abox_2011-11-13.nt.http%3A__www.w3.org_2000_01_rdf-schema%23label.nt -n 5
```

Produces output:

```
Loading "/home/janos/workspace/sbu-mi-vivo-tools/reach_abox_2011-11-13.nt.http%3A__www.w3.org_2000_01_rdf-schema%23label.nt"
Finished loading ntriples file
Number of triples 221149 loaded in 2.788174 seconds (79316.7858247 triples/second)
Number of distinct lexical symbols: 48660
Number of distinct subjects: 21575
Number of distinct predicates: 1
Number of distinct objects including literals: 27084
Number of literals: 27084
Fraction of objects that are literals: 1.0

Top subjects are:
[('<http://reach.suny.edu/individual/a17010819>', 66),
 ('<http://reach.suny.edu/individual/a18760147>', 50),
 ('<http://reach.suny.edu/individual/a21297512>', 49),
 ('<http://reach.suny.edu/individual/a15862441>', 49),
 ('<http://reach.suny.edu/individual/a15766815>', 45)]

Top objects are:
[('"of"', 12778),
 ('"in"', 9127),
 ('"and"', 8455),
 ('"the"', 5111),
 ('"with"', 3150)]

Top predicates are:
[('<http://vivoweb.org/ontology/core#freetextKeyword>', 221149)]
```

The script can be run with standard Python but PyPy is 4.3 times faster:
```
python -V
Python 2.7.2+
python ~/workspace/py-triple-simple/src/py_triple_simple.py -c statistics -f reach_abox_2011-11-13.nt.http%3A__www.w3.org_2000_01_rdf-schema%23label.nt -n 5
Loading "/home/janos/workspace/sbu-mi-vivo-tools/reach_abox_2011-11-13.nt.http%3A__www.w3.org_2000_01_rdf-schema%23label.nt"
Finished loading ntriples file
Number of triples 221149 loaded in 12.12 seconds (18246.6171617 triples/second)
```

# Pattern matching/querying #

```
pypy-c py_triple_simple.py -f reach_abox_2011-11-13.nt \
-q "[('a','p1','b'),('a','p2','c')]"  \
-r "[('p1','in',['<http://xmlns.com/foaf/0.1/lastName>']),('p2','in',['<http://xmlns.com/foaf/0.1/firstName>'])]" \
-v "['a','b','c']" -c query -n All
```

Produces output:
```
[[('<http://example.com/individual/John_Stephen>',
   '"John"',
   '"Stephen"'),
  1],
 [('<http://example.com/individual/Lily_Catherine>',
   '"Lily"',
   '"Catherine"'),
  1]]
```

An example of a simple co-occurrence analysis is:

```
pypy-c py_triple_simple.py -f reach_abox_2011-11-13.nt.http%3A__www.w3.org_2000_01_rdf-schema%23label.nt \
-c query -q "[('a','p','b'),('a','p','c')]"  \
-v "['b','c']" \
-r "[('p', 'in', ['<http://vivoweb.org/ontology/core#freetextKeyword>']),('b','!=','c'),('b','not in', ['a','the','of','on','in','and','to','with','for','by','The','A','an']),('c','not in', ['a','the','of','on','in','and','to','with','for','by','The','A','an'])]"\
-n 10
```

Produces output:

```
[[('"Faculty"', '"University"'), 449],
 [('"University"', '"Faculty"'), 449],
 [('"sclerosis"', '"multiple"'), 343],
 [('"multiple"', '"sclerosis"'), 343],
 [('"University"', '"Medical"'), 308],
 [('"Medical"', '"University"'), 308],
 [('"Downstate"', '"Medical"'), 302],
 [('"Medical"', '"Downstate"'), 302],
 [('"Downstate"', '"University"'), 301],
 [('"University"', '"Downstate"'), 301]]
```

# Output formats #

The script supports a diagnostic output, delimited output (tab delimited), and JSON based output formats. The script output can be written to a console or to a text file.

Here I am querying to get all PubMed Ids back from a VIVO dump
```
janos@janosworkstation:~/workspace/sbu-mi-vivo-tools$ pypy-c py_triple_simple.py -f reach_abox_2011-11-13.nt -c query \
-q "[('a','p','c')]" \n
-r "[('p','in',['<http://purl.org/ontology/bibo/pmid>'])]" \
-v "['c']" -o delimited -n 10
```
Produces output:
```
c	count
"17258161"	2
"19716077"	2
"15597812"	2
"11041443"	1
"8203638"	1
"21248674"	1
"15246464"	1
"18254103"	1
"16513665"	1
"5440675"	1
```

```
pypy-c py_triple_simple.py -f reach_abox_2011-11-13.nt \
-c query -q "[('a','p','c')]" \
-r "[('p','in',['<http://purl.org/ontology/bibo/pmid>'])]" \
-v "['a','c']" -o delimited -n 10 --clean=1
```
Produces output:
```
a	c	count
http://example.org/individual/a11740726	11740726	1
http://example.org/individual/a17502569	17502569	1
http://example.org/individual/a14988635	14988635	1
http://example.org/individual/a11292642	11292642	1
http://example.org/individual/a20513327	20513327	1
http://example.org/individual/a9802626	9802626	1
http://example.org/individual/a9607513	9607513	1
http://example.org/individual/a20935045	20935045	1
http://example.org/individual/a8304260	8304260	1
http://example.org/individual/a11940547	11940547	1
```