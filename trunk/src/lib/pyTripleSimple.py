"""
Classes for processing and working with files that follow the ntriples format.
    
"""

import re
from xml.sax.saxutils import escape as xml_escape

common_prefixes = {"rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#"}

class SimpleNTriplesLineReactor(object):
    """
        A skeleton class for writing simple triple action reactor.  
        When a particular pattern/condition is met a call back function is triggered
    """
    
    def __init__(self,iterable_stream,matching_function,call_back_function = None,result_obj = None):
        self.matching_function = matching_function
        self.iterable_stream = iterable_stream        
        self.result_obj = result_obj
        if call_back_function is None:
            self.call_back_function = self.default_call_back_function
        else:
            self.call_back_function = call_back_function
            
    def default_call_back_function(self,result,result_obj=None):
        """By default the callback function will just print the result"""
        print(result)
        return result_obj
    
    def process(self):
        """Begin the processing a set of ntriples"""
        for unread_statement in self.iterable_stream:
            matching_result = self.matching_function(unread_statement)
            if matching_result:
                self.result_obj = self.call_back_function(matching_result, self.result_obj)
    
    def result_obj(self):
        """Returns result obj"""
        return self.result_obj
    
    
class SimpleNtripleExtractor(object):
    """
        This is the simplest of a N-Triples extractor. It ignores language tags and
        XML data typed tags and extracts information from triples
    """
    
    def __init__(self):
        """
           uuu: subject, predicate, object
           uul: subject, predicate, literal
           buu: blank, predicate, object
           bul: blank node, predicate, literal
           uub: subject, predicate, blank node
           c: comment
           e: empty line
           x: error
        """
        
        self.regex_patterns = {"uuu": re.compile(r'<(.+)>[ \t]+<(.+)>[ \t]+<(.+)>'),
        "uul" : re.compile(r'<(.+)>[ \t]+<(.+)>[ \t]+"(.*)"'),
        "buu" : re.compile(r'(\_\:.+)[ \t]+<(.+)>[ \t]+<(.+)>'), 
        "uub" : re.compile(r'<(.+)>[ \t]+<(.+)>[ \t]+(\_\:.+)'), 
        "bul" : re.compile(r'(\_\:.+)[ \t]+<(.+)>[ \t]+"(.*)"'), 
        "c" : re.compile("^\#.+")}
        
    
    def parse(self,line):
        """Parse a line of ntriples text extracting"""
        line = line.strip()
        if line == "":
            return "e"
        elif line[0] == "#":
            return "c"
        
        for triple_pattern in self.regex_patterns.keys():
            regex_triple_pattern = self.regex_patterns[triple_pattern]
            pattern_match = regex_triple_pattern.search(line)
            if pattern_match:
                triple_pattern_group = pattern_match.groups()
                if len(triple_pattern_group) == 3:
                    return SimpleTriple(triple_pattern_group[0], triple_pattern_group[1], triple_pattern_group[2],triple_pattern)
                else:
                    return "x" # Error

class SimpleNtriplesParser(SimpleNtripleExtractor):
    def parse(self,line):
        line = line.strip()
        state = "TripleStart"
        i = 0
        start_state_position = 0
        triples = []
        triple_types = ""
        triples_parsed = []

        while i < len(line) or (i == len(line) and state =="TripleEnd"):

            if state == "TripleStart":
                if line[i] == "<":
                    state = "UriStart"
                    start_state_position = i + 1
                elif line[i] == "_":
                    state = "BlankNodeStart"
                    start_state_position = i

                elif line[i] == "#":
                    state = "Comment"
                    triple_types += "c"

            elif state == "UriStart":
                if line[i] == ">":
                    state = "UriEnd"
                    triples.append(line[start_state_position:i])
                    triple_types += "u"

            elif state == "UriEnd":
                if line[i] == '"':
                    state = "LiteralStart"
                    start_state_position = i + 1
                elif line[i] == ".":
                    state = "TripleEnd"
                elif line[i] == "<":
                    state = "UriStart"
                    start_state_position = i + 1
                elif line[i] == "_":
                    state = "BlankNodeStart"
                    start_state_position = i

            elif state == "BlankNodeStart":
                if line[i] == " " or line[i] == "\t": # a blank node is terminated by white space or an end
                    state = "BlankNodeEnd"
                    triples.append(line[start_state_position:i])
                    triple_types += "b"
                elif line[i] == ".":
                    state = "TripleEnd"
                    triples.append(line[start_state_position:i])
                    triple_types += "b"

            elif state == "LiteralStart":
                if line[i] == '"' and line[i-1] != "\\":
                    state = "LiteralEnd"
                    triples.append(line[start_state_position:i])
                    triple_types += "l"
                elif line[i] == '"' and line[i-1] == "\\" and line[i-2] == "\\":
                    scorer = 0
                    for j in range(len(line[i:]) - 1):
                        if line[i + 1 + j] == " ":
                            scorer += 0
                        elif line[i + 1 + j] == "\t":
                            scorer += 0
                        elif line[i+ 1 + j] == ".":
                            scorer += 0
                        elif line[i + 1 + j] == "\n":
                            scorer += 0
                        else:
                            scorer += 1

                    if scorer == 0:
                        state = "LiteralEnd"
                        triples.append(line[start_state_position:i])
                        triple_types += "l"

            elif state == "LiteralEnd":
                if line[i] == ".":
                    state = "TripleEnd"

            elif state == "BlankNodeEnd":
                if line[i] == ".":
                    state = "TripleEnd"
                elif line[i] == "<":
                    state = "UriStart"
                    start_state_position = i + 1

            elif state == "TripleEnd":
                if triple_types in ["uuu","uul","buu","uub", "bul"]:
                    triples_parsed.append(SimpleTriple(triples[0], triples[1], triples[2],triple_types))
                    triples = []
                    triple_types = ""
                elif "x" in triple_types:
                    raise RuntimeError, "Error parsing file"

                if i < len(line):
                    if line[i] == '\r' or line[i] == '\n':
                        state="TripleStart"
            i += 1

        return triples_parsed

class SimpleTriple(object):
    """A basic container for a triple"""
    def __init__(self,subject,predicate,object,triple_type="uuu"):
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.triple_type = triple_type
    def triple_type(self):
        return self.triple_type
    def subject_type(self):
        return self.triple_type[0]
    def predicate_type(self):
        return self.triple_type[1]
    def object_type(self):
        return self.triple_type[2]
    def to_tuple(self):
        return (self.subject, self.predicate, self.object)
    def __repr__(self):
        return str(self.to_tuple())
    
    def to_ntriple(self):
        ntriple_string = ""
        if self.subject_type() == 'u':
            ntriple_string = "<%s> " % self.subject
        else:
            ntriple_string = "%s " % self.subject

        ntriple_string += "<%s> " % self.predicate

        if self.object_type() == 'u':
            ntriple_string += "<%s> " % self.object
        elif self.object_type() == 'l':
            ntriple_string += '"%s"' % self.object
        else:
            ntriple_string += self.object
        ntriple_string += " .\n"
        return ntriple_string

class TripleEngine(object):
    """Abstract class for native triple store in Python"""
    
    def __init__(self):
        self.symbols = {}
        self.triples = {}
        self.objects = {}
        self.subjects_index = {}
        self.objects_index = {}
        self.predicates_index = {}
        
    def key_store(self, key_value):
        """Some persistent stores do not allow non-string keys so take a key and do something if needed"""
        return key_value
    
    def key_retrieve(self, key_value):
        return key_value
    
    def triple_store(self,triple):
        """In case when storing triples we need to some processing this will define the behavior"""
        return triple
    
    def triple_retrieve(self,triple):
        return triple
        
class SimpleTripleStore(object):
    """A class for encapsulating triple store behavior.  The class does not provide SPARQL
        support or default graph but it is designed for manipulating and processing data
        represented in a ntriples text file. """
        
    def __init__(self,triple_engine=None):
        """By default it uses the in-memory based backend"""

        if triple_engine is None: #By default load native model
            self.triple_engine = TripleEngine()
        else:
            self.triple_engine = triple_engine
        
        self.te = self.triple_engine # shortcut attribute

    def n_symbols(self):
        """Symbols are integers that map to a string."""
        return len(self.te.symbols)
    
    def n_triples(self):
        """Returns the number of statements/triples in a store"""
        return len(self.te.triples)
    
    def n_objects(self):
        """Number of distinct objects in the SPO sense"""
        return len(self.te.objects_index)
    
    def n_predicates(self):
        """Number of distinct predicates"""
        return len(self.te.predicates_index)
    
    def n_subjects(self):
        """Number of distinct subjects"""
        return len(self.te.subjects_index)
    
    def add_triple(self,triple_object):
        """Add a triple to the store"""
        triple = triple_object.to_tuple()
        
        t1 = triple[0]
        t2 = triple[1]
        t3 = triple[2]
        
        t1_symbol = self._add_symbol(t1)
        t2_symbol = self._add_symbol(t2)
        t3_symbol = self._add_symbol(t3)
                
        t1_address = triple_object.subject_type() + str(t1_symbol)
        t2_address = triple_object.predicate_type() + str(t2_symbol)
        t3_address = triple_object.object_type() + str(t3_symbol)
        
        self.te.objects[t1_address] = t1
        self.te.objects[t2_address] = t2
        self.te.objects[t3_address] = t3
        
        triple_address = self.n_triples() + 1
        self.te.triples[self.te.key_store(triple_address)] = self.te.triple_store((t1_address,t2_address,t3_address))
        
        #Build indices for quicker retrieval
        if self.te.subjects_index.has_key(t1_address):
            self.te.subjects_index[t1_address].append(triple_address)
        else:
            self.te.subjects_index[t1_address] = [triple_address]
            
        if self.te.predicates_index.has_key(t2_address):
            self.te.predicates_index[t2_address].append(triple_address)
        else:
            self.te.predicates_index[t2_address] = [triple_address]
            
        if self.te.objects_index.has_key(t3_address):
            self.te.objects_index[t3_address].append(triple_address)
        else:
            self.te.objects_index[t3_address] = [triple_address]
        
        return triple_address
        
    def load_ntriples(self,iterable_ntriples):
        """Load an ntriples iterable into the store"""
        extractor = SimpleNtriplesParser()
        for ntriple in iterable_ntriples:
            extracted_results = extractor.parse(ntriple)
            for extracted_result in extracted_results: 
                self.add_triple(extracted_result)

    def _add_symbol(self,item):
        """Add a symbol"""
        if self.te.symbols.has_key(item):
            symbol_address = self.te.key_retrieve(self.te.symbols[item])
        else:
            symbol_address = self.n_symbols() + 1
            self.te.symbols[item] = self.te.key_store(symbol_address)
        return symbol_address
    
    def _decode_address(self,address):
        return self.te.objects[address]
    
    def _decode_triple(self,triple_address):
        """Given an address to a triple decodes it without ntriples formatting,
        as an example the uri http://example.org is not shown as 
        <http://example.org>
        """
        triple = self.te.triples[triple_address]
        t1 = self._decode_address(triple[0])
        t2 = self._decode_address(triple[1])
        t3 = self._decode_address(triple[2])
        return (t1,t2,t3)

    def triple_address_to_simple_triple(self,triple_address):
        """Given an address to a triple returns a triple Simple Object"""
        triple = self.te.triples[triple_address]

        triple_type = ""
        for x in triple:
            triple_type += x[0:1]

        t1 = self._decode_address(triple[0])
        t2 = self._decode_address(triple[1])
        t3 = self._decode_address(triple[2])

        return SimpleTriple(t1, t2, t3, triple_type)
    
    def _format_symbol(self,symbol, object_type):
        if object_type == "u":
            return "<" +  symbol + ">"
        if object_type == "l":
            return '"' + symbol + '"'
        if object_type == "b":
            return symbol
        
    def _decode_address_formatted(self,object_address):
        """Pass in a reference to an object and decodes it"""
        return self._format_symbol(self._decode_address(object_address),object_address[0]) 
    
    def _decode_triple_formatted(self, triple_address):
        """Formats triples into an address formatted"""
        triple = self.te.triples[triple_address]
        t1 = self._decode_address_formatted(triple[0])
        t2 = self._decode_address_formatted(triple[1])
        t3 = self._decode_address_formatted(triple[2])
        return (t1,t2,t3)
    
    def _encode_uri(self,uri):
        """Encode a uri into a referenceable address"""
        if self.te.symbols.has_key(uri):
            sym_addr = self.te.symbols[uri]
            return 'u' + str(sym_addr)
        else:
            return 0
        
    def _encode_literal(self,literal):
        """Encode a literal into a referenceable address"""
        if self.te.symbols.has_key(literal):
            sym_addr = self.te.symbols[literal]
            return 'l' + str(sym_addr)
        else:
            return 0

    def _uri_check(self,uri):
        if uri[0] == "<" and uri[-1] ==  ">":
            uri = uri[1:-1]
        return uri
        
    def subjects(self,uri):
        """For a subject specified by a uri return all associated triples"""
        uri = self._uri_check(uri)
        uri_addr = self._encode_uri(uri)
        if uri_addr:
            if self.te.subjects_index.has_key(uri_addr):
                return [self._decode_triple_formatted(t) for t in self.te.subjects_index[uri_addr]]
            
    def objects(self,uri):
        """For an object specified by uri return all associated triples"""
        uri = self._uri_check(uri)
        uri_addr = self._encode_uri(uri)
        
        if uri_addr:
            if self.te.objects_index.has_key(uri_addr):
                return [self._decode_triple_formatted(t) for t in self.te.objects_index[uri_addr]]
        
    def predicates(self,uri):
        """For an object specified by uri return all associated triples"""
        uri = self._uri_check(uri)
        uri_address = self._encode_uri(uri)
        
        if uri_address:
            if self.te.predicates_index.has_key(uri_address):
                return [self._decode_triple_formatted(t) for t in self.te.predicates_index[uri_address]]
            
    def export_to_ntriples_file(self,f):
        """For file object write the triples to file"""
        for key in self.te.triples.iterkeys():
            triple = self._decode_triple_formatted(key)
            f.write( "%s %s %s .\n" % triple)
        return f
        
    def export_to_ntriples_string(self):
        """Export ntriples to an in memory string"""
        nt = ""
        for key in self.te.triples.iterkeys():
            triple = self._decode_triple_formatted(key)
            nt +=  "%s %s %s .\n" % triple
        return nt
        
    def n_literals(self):
        """Returns the number of literals in the store"""
        i = 0
        for key in self.te.objects.iterkeys():
            if key[0] == "l":
                i += 1
        return i
                 
    def _n_objects(self,hash_index):
        """Creates a reverse sorted list of addresses with keys"""
        keys = hash_index.iterkeys()
        keys_with_len = []
        for key in keys:
            keys_with_len.append((key,len(hash_index[key])))
            
        keys_with_len.sort(key=lambda x: x[1],reverse=True)
        return keys_with_len
    
    def _top_items(self,hash_index,top_n=None):
        """Private method for calculating a sorted list"""
        keys_with_len = self._n_objects(hash_index)
        
        if top_n is not None:
            keys_with_len = keys_with_len[0:top_n]
            
        return [(self._decode_address_formatted(top_subject[0]),top_subject[1]) for top_subject in keys_with_len]
    
    def top_subjects(self,top_n = 25):
        """Returns a list of top referenced subjects"""
        return self._top_items(self.te.subjects_index,top_n)
    
    def top_objects(self,top_n = 25):
        """Returns a list of of top referenced objects"""
        return self._top_items(self.te.objects_index,top_n)
    
    def top_predicates(self, top_n=25):
        """Returns a list of top used predicates"""
        return self._top_items(self.te.predicates_index,top_n)

    def iterator_triples(self):
        return IteratorTripleStore(self)

    def iterator_ntriples(self):
        return IteratorTripleStoreNtriple(self)

    def _raw_find_triples(self,subjects_address,predicates_address,objects_address):
        n_subjects = len(subjects_address)
        n_objects = len(objects_address)
        n_predicates = len(predicates_address)
        subject_address = None
        predicate_address = None
        object_address = None
        triples_set = set([])

        if n_subjects + n_predicates + n_objects == 0:
            triples_set = set(self.te.triples.keys())
        elif (n_subjects == 1 or n_subjects == 0) and (n_predicates == 1 or n_predicates == 0) and (n_objects == 1 or n_objects == 0):
            if n_subjects:
                if subjects_address[0] in self.te.subjects_index:
                    subject_address = subjects_address[0]
                    n_subjects_triples = len(self.te.subjects_index[subject_address])
                else:
                    n_subjects_triples = 0
            else:
                n_subjects_triples = None

            if n_predicates:
                if predicates_address[0] in self.te.predicates_index:
                    predicate_address = predicates_address[0]
                    n_predicates_triples = len(self.te.predicates_index[predicate_address])
                else:
                    n_predicates_triples = 0
            else:
                n_predicates_triples = None

            if n_objects:
                if objects_address[0] in self.te.objects_index:
                    object_address = objects_address[0]
                    n_objects_triples = len(self.te.objects_index[object_address])
                else:
                    n_objects_triples = 0
            else:
                n_objects_triples = None

            if n_subjects_triples == 0 or n_predicates_triples == 0 or n_objects_triples == 0:
                triples_set = set([])
            else: # We know there are solutions
                triples = []
                if n_subjects_triples is not None and n_predicates_triples is not None and n_objects_triples is not None: #(spo)
                    min_n_triples = min(n_subjects_triples,n_predicates_triples,n_objects_triples)
                    if n_subjects_triples == min_n_triples:
                        triples_to_evaluate = self.te.subjects_index[subject_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[1] == predicate_address:
                                if triple_to_evaluate[2] == object_address:
                                    triples.append(triples_address_to_evaluate)
                    elif n_predicates_triples == min_n_triples:
                        triples_to_evaluate = self.te.predicates_index[predicate_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[0] == subject_address:
                                if triple_to_evaluate[2] == object_address:
                                    triples.append(triples_address_to_evaluate)
                    elif n_objects_triples == min_n_triples:
                        triples_to_evaluate = self.te.predicates_index[predicate_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[0] == subject_address:
                                if triple_to_evaluate[1] == predicate_address:
                                    triples.append(triples_address_to_evaluate)
                elif n_subjects_triples is not None and n_predicates_triples is not None and n_objects_triples is None: #(sp.)
                    if n_subjects_triples <= n_predicates_triples:
                        triples_to_evaluate = self.te.subjects_index[subject_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[1] == predicate_address:
                                triples.append(triples_address_to_evaluate)
                    else:
                        triples_to_evaluate = self.te.predicates_index[predicate_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[0] == subject_address:
                                triples.append(triples_address_to_evaluate)
                elif n_subjects_triples is not None and n_predicates_triples is None and n_objects_triples is not None: #(s.o)
                    if n_subjects_triples <= n_objects_triples:
                        triples_to_evaluate = self.te.subjects_index[subject_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[2] == object_address:
                                triples.append(triples_address_to_evaluate)
                    else:
                        triples_to_evaluate = self.te.objects_index[object_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[0] == subject_address:
                                triples.append(triples_address_to_evaluate)
                                
                elif n_subjects_triples is None and n_predicates_triples is not None and n_objects_triples is not None: #(.po)
                    if n_predicates_triples <= n_objects_triples:
                        triples_to_evaluate = self.te.predicates_index[predicate_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[2] == object_address:
                                triples.append(triples_address_to_evaluate)
                    else:
                        triples_to_evaluate = self.te.objects_index[object_address]
                        for triples_address_to_evaluate in triples_to_evaluate:
                            triple_to_evaluate = self.te.triples[triples_address_to_evaluate]
                            if triple_to_evaluate[1] == predicate_address:
                                triples.append(triples_address_to_evaluate)
                                
                elif n_subjects_triples is not None and n_predicates_triples is None and n_objects_triples is None: #(s..)
                    triples = self.te.subjects_index[subject_address]
                elif n_subjects_triples is None and n_predicates_triples is not None and n_objects_triples is None: #(.p.)
                    triples = self.te.predicates_index[predicate_address]
                elif n_subjects_triples is None and n_predicates_triples is None and n_objects_triples is not None: #(..p)
                    triples = self.te.objects_index[object_address]
            triples_set = set(triples)
        else: # If you pass in a list of subjects uses a pure set based approach
            if n_subjects:
                subjects_set = set()
                for subject_address in subjects_address:
                    subjects_set = subjects_set.union(set(self.te.subjects_index[subject_address]))
                triples_set = subjects_set

            if n_predicates:
                predicates_set = set()
                for predicate_address in predicates_address:
                    predicates_set = predicates_set.union(set(self.te.predicates_index[predicate_address]))
                if n_subjects:
                    triples_set = triples_set.intersection(predicates_set)
                else:
                    triples_set = predicates_set

            if n_objects:
                objects_set = set()
                for object_address in objects_address:
                    objects_set = objects_set.union(set(self.te.objects_index[object_address]))
                if n_predicates + n_subjects > 0:
                    triples_set = triples_set.intersection(objects_set)
                else:
                    triples_set = objects_set
                    
        return triples_set


    def _encode_subjects(self,subjects):
        subjects_encoded = []
        if subjects is not None:
            for subject in subjects:
                subject = self._uri_check(subject)
                subject_address = self._encode_uri(subject)
                if subject_address:
                    if self.te.subjects_index.has_key(subject_address):
                        subjects_encoded.append(subject_address)
        return subjects_encoded

    def _encode_objects(self,objects):
        objects_encoded = []
        if objects is not None:
                for object in objects:
                    object = self._uri_check(object)
                    object_address = self._encode_uri(object)
                    if object_address:
                        if self.te.objects_index.has_key(object_address):
                            objects_encoded.append(object_address)
        return objects_encoded

    def _encode_predicates(self,predicates):
        predicates_encoded = []
        if predicates is not None:
            for predicate in predicates:
                predicate = self._uri_check(predicate)
                predicate_address = self._encode_uri(predicate)
                if predicate_address:
                    if self.te.predicates_index.has_key(predicate_address):
                        predicates_encoded.append(predicate_address)
        return predicates_encoded


    def _encode_literals(self,literals):
        literals_encoded = []
        if literals is not None:
            for literal in literals:
                literal_address = self._encode_literal(literal)
                if literal_address:
                    if self.te.objects_index.has_key(literal_address):
                        literals_encoded.append(literal_address)
        return literals_encoded


    def find_triples(self,subjects=None, predicates = None, objects = None, literals = None, return_type="raw"):
        """Find triples which match criteria: If nothing is given will return None.
            The input parameters for subjects, predicates, and objects can either be a string or an iterable"""

        if type(subjects) == type(""):
            subjects = [subjects]

        if type(predicates) == type(""):
            predicates = [predicates]

        if type(objects) == type(""):
            objects = [objects]

        if type(literals) == type(""):
            literals = [literals]

        if subjects is None and objects is None and predicates is None and literals is None:
            return None

        subjects_encoded = self._encode_subjects(subjects)
        objects_encoded = self._encode_objects(objects)
        predicates_encoded = self._encode_predicates(predicates)
        literals_encoded = self._encode_literals(literals)
            
        if (len(subjects_encoded) + len(objects_encoded) + len(predicates_encoded) + len(literals_encoded))  == 0:
            return set([])
        elif subjects is not None and len(subjects) > 0 and len(subjects_encoded) == 0:
            return set([])
        elif predicates is not None and len(predicates) > 0 and len(predicates_encoded) == 0:
            return set([])
        elif objects is not None or literals is not None:
            if objects is not None and literals is None:
                if len(objects) > 0 and len(objects_encoded) == 0:
                    return set([])
            elif literals is not None and objects is None:
                if len(literals) > 0 and len(literals_encoded) == 0:
                    return set([])
            else:
                if len(literals + objects) > 0 and len(literals_encoded + objects_encoded) == 0:
                    return set([])

        raw_results = self._raw_find_triples(subjects_encoded, predicates_encoded, objects_encoded + literals_encoded)

        if return_type == "raw":
            return raw_results
        elif return_type == "triples":
            return [self.triple_address_to_simple_triple(triple_address) for triple_address in raw_results]
        elif return_type == "ntriples":
            pass

    def simple_pattern_match(self, patterns, restrictions = [], solution_variables = []):
        """
        Patterns are simple Python structures which have the form:
            [('a1','p1','a2'),('a2','p2','a1')]
        this pattern would find all triples which have links in both direction.

        Additional patterns include:
        [('a','b','c','d','e')] or the equivalent [('a','b','c'),('c','d','e')]

        Another pattern:
        [('a','b','c'),('a','b','d')]
        This would return a result for all triples because of a self match. We need to specify a restriction.

        Restrictions are specified in a list:

        ('c','!=','d')
        ('c','==','d',string.lower, string.lower)
        ('e','in',[<http://example.org/property1>','<http://example.org/property2>'])
        ('g','not in',[str(x) for x in range(5)]) => ['g','not in',['0','1','2','3',4'])

        Restrictions on variables currently support '==' and '!=' .
        Restrictions on literals and URIs are support 'in', and 'not in'

        Dictionaries with lists are used to specify filtering of the pattern.
        Restrictions are applied in the order that they are received and are applied only once.

        Output variables are specified in a list ['p1','p2']. By default answers will be aggregated and returned as list
        descending occurrence [[['<http://example.org/property/1>','<http://example.org/property/2>'], 50)]]
        """

        functions_to_apply = {}

        processed_solution_variables = [] # Process solution variables in case a solution variable is a result modifier
        for solution_variable in solution_variables:
            if hasattr(solution_variable, "variable"):
                variable = solution_variable.variable
                functions_to_apply[variable] = solution_variable
                processed_solution_variables.append(variable)
            else:
                processed_solution_variables.append(solution_variable)

        solution_variables = processed_solution_variables

        patterns_obj = TriplePatterns(patterns)
        restrictions_obj = TripleRestrictions(restrictions, patterns_obj.variables())

        potential_solution_list = [[]] # seed potential solution list with empty list
        solution_length = 0

        i = 0
        for pattern in patterns_obj.patterns():
            variable1 = pattern[0]
            variable2 = pattern[1]
            variable3 = pattern[2]

            variable1_position = patterns_obj.variables()[variable1]
            variable2_position = patterns_obj.variables()[variable2]
            variable3_position = patterns_obj.variables()[variable3]

            extended_solution_length = max([variable1_position + 1, variable2_position + 1, variable3_position + 1])

            #Include solutions that have the following URIs and literals
            if variable1 in restrictions_obj.uri_inclusions():
                subjects = restrictions_obj.uri_inclusions()[variable1]

            else:
                subjects = None
            if variable2 in restrictions_obj.uri_inclusions():
                predicates = restrictions_obj.uri_inclusions()[variable2]
            else:
                predicates = None
            if variable3 in restrictions_obj.uri_inclusions():
                objects = restrictions_obj.uri_inclusions()[variable3]
            else:
                objects = None
            if variable3 in restrictions_obj.literal_inclusions():
                literals = restrictions_obj.literal_inclusions()[variable3]
            else:
                literals = None

            restrictions_to_apply = []
            for variable in [variable1, variable2, variable3]:
                if variable in restrictions_obj.variable_restrictions():
                    for potential_restriction in restrictions_obj.variable_restrictions()[variable]:
                        if potential_restriction not in restrictions_to_apply:
                            restrictions_to_apply.append(potential_restriction)

            exclusions_to_apply = {}
            for variable in [variable1, variable2, variable3]:
                if variable in restrictions_obj.uri_exclusions():

                    for uri in restrictions_obj.uri_exclusions()[variable]:
                        uri = self._uri_check(uri)
                        uri_address = self._encode_uri(uri)
                        if uri_address:
                            if variable not in exclusions_to_apply:
                                exclusions_to_apply[variable] = [uri_address]
                            else:
                                exclusions_to_apply[variable].append(uri_address)
            for variable in [variable1,variable2, variable3]:
                if variable in restrictions_obj.literal_exclusions():
                    for literal in restrictions_obj.literal_exclusions()[variable]:
                        literal_address = self._encode_literal(literal)
                        if literal_address:
                            if variable not in exclusions_to_apply:
                                exclusions_to_apply[variable] = [literal_address]
                            else:
                                exclusions_to_apply[variable].append(literal_address)

            updated_solution_list = []
            if subjects is not None and variable1_position >= solution_length:
                original_subjects_length = len(subjects)
                subjects = self._encode_subjects(subjects)
            else:
                original_subjects_length = 0
                subjects = []
            if objects is not None and variable3_position >= solution_length:
                original_objects_length = len(objects)
                objects = self._encode_objects(objects)
            else:
                objects = []
                original_objects_length = 0
            if predicates is not None and variable2_position >= solution_length:
                original_predicates_length = len(predicates)
                predicates = self._encode_predicates(predicates)
            else:
                original_predicates_length = 0
                predicates = []
            if literals is not None and variable3_position >= solution_length:
                original_literals_length = len(literals)
                literals = self._encode_literals(literals)
            else:
                original_literals_length = 0
                literals = []

            for potential_solution in potential_solution_list:
                execute_find = 1

                if variable1_position + 1 <= solution_length:
                    if self.te.subjects_index.has_key(potential_solution[variable1_position]):
                        subjects = [potential_solution[variable1_position]]
                    else:
                        execute_find = 0
                if variable2_position + 1 <= solution_length:
                    if self.te.predicates_index.has_key(potential_solution[variable2_position]):
                        predicates = [potential_solution[variable2_position]]
                    else:
                        execute_find = 0
                if variable3_position + 1 <= solution_length:
                    if self.te.objects_index.has_key(potential_solution[variable3_position]):
                        objects = [potential_solution[variable3_position]]
                    else:
                        execute_find = 0

                if len(subjects) == 0 and original_subjects_length > 0:
                    execute_find = 0
                elif len(predicates) == 0 and original_predicates_length > 0:
                    execute_find = 0
                elif len(objects + literals) == 0 and original_objects_length + original_literals_length > 0:
                    execute_find = 0

                if execute_find:
                    solutions = self._raw_find_triples(subjects,predicates,objects + literals)
                else:
                    solutions = []
                
                if len(solutions): # Check if we have any solution
                    for solution_address in solutions:
                        local_solution_length = solution_length

                        solution = self.te.triples[solution_address]
                        new_solution = list(potential_solution[:])
                        if variable1_position + 1 > local_solution_length:
                            new_solution.append(solution[0])
                            local_solution_length += 1
                        if variable2_position + 1 > local_solution_length:
                            new_solution.append(solution[1])
                            local_solution_length += 1
                        if variable3_position + 1 > local_solution_length:
                            new_solution.append(solution[2])
                            local_solution_length += 1

                        is_solution = 1 #explicitly a solution unless otherwise shown
                        # handle internal patterns {(a,a,b),(a,b,a),(b,a,a)}
                        if variable1 == variable2 == variable3:
                            if solution[0] == solution[1] == solution[2]:
                                pass
                            else:
                                is_solution = 0
                        elif variable1 == variable2:
                            if solution[0] != solution[1]:
                                is_solution = 0
                        elif variable1 == variable3:
                            if solution[1] != solution[2]:
                                is_solution = 0
                        if variable2 == variable3:
                            if solution[1] != solution[3]:
                                is_solution = 0

                        for restriction in restrictions_to_apply:
                            restriction_statement = restrictions_obj.restrictions()[restriction]
                            restriction_variable1 = restriction_statement[0]
                            restriction_variable2 = restriction_statement[2]
                            restriction_rule = restriction_statement[1]
                            restriction_variable1_position = patterns_obj.variables()[restriction_variable1]
                            restriction_variable2_position = patterns_obj.variables()[restriction_variable2]
                            if max([restriction_variable1_position,restriction_variable2_position]) < len(new_solution):

                                if restriction_rule == '!=':
                                    if new_solution[restriction_variable1_position] == new_solution[restriction_variable2_position]:
                                        is_solution = 0
                                elif restriction_rule == '==':
                                    if new_solution[restriction_variable1_position] != new_solution[restriction_variable2_position]:
                                        is_solution = 0

                        for variable in [variable1, variable2, variable3]:
                            if variable in exclusions_to_apply:
                                exclusions = exclusions_to_apply[variable]
                                variable_position = patterns_obj.variables()[variable]
                                for exclusion in exclusions:
                                    if exclusion == new_solution[variable_position]:
                                        is_solution = 0

                        if is_solution:
                            updated_solution_list.append(new_solution)
            solution_length = extended_solution_length
            potential_solution_list = updated_solution_list
            i += 0

        #Process solution
        solution_variables_position = []
        solution_dict = {}
        for solution_variable in solution_variables:
            solution_variables_position.append(patterns_obj.variables()[solution_variable])

        for solution in potential_solution_list:
            solution_key_list = []

            for position in solution_variables_position:
                solution_key_list.append(solution[position])
            solution_key = tuple(solution_key_list)
            if solution_key in solution_dict:
                solution_dict[solution_key] += 1
            else:
                solution_dict[solution_key] = 1

        solutions_list = []
        for solution_key in solution_dict.keys():
            solutions = []

            for solution_encoded in solution_key:
                solution_decoded = self._decode_address_formatted(solution_encoded)
                solutions.append(solution_decoded)

            if len(functions_to_apply.keys()): # if we are doing some function application
                for modified_variable in functions_to_apply.keys():
                    modified_variable_position = solution_variables.index(modified_variable)
                    solutions[modified_variable_position] = functions_to_apply[modified_variable].evaluate(solutions[modified_variable_position])
            solutions_list.append([tuple(solutions),solution_dict[solution_key]])


        if len(functions_to_apply.keys()): # The solution_list needs to reprocessed because the applied function might have changed the result
            new_solutions = {}
            for solution in solutions_list:
                if solution[0] in new_solutions:
                    new_solutions[solution[0]] += solution[1]
                else:
                    new_solutions[solution[0]] = solution[1]

            new_solution_list = []
            for new_solution in new_solutions.keys():
                new_solution_list.append([new_solution,new_solutions[new_solution]])
            solutions_list = new_solution_list

        solutions_list.sort(key=lambda x: x[1],reverse=True)
        
        return solutions_list

    def union_pattern_match_result_set(self, result_set1, result_set2):
        """Union two result sets"""
        new_result_dict = {}
        for result_set in [result_set1, result_set2]:
            for result in result_set:
                result_tuple = result[0]
                if result_tuple in new_result_dict:
                    new_result_dict[result_tuple] += result[1]
                else:
                    new_result_dict[result_tuple] = result[1]
        new_result_list = []
        for new_result in new_result_dict.keys():
            new_result_list.append([new_result,new_result_dict[new_result]])

        new_result_list.sort(key=lambda x: x[1],reverse=True)
        return new_result_list

class TriplePatterns(object):
    def __init__(self,patterns):
        self.original_patterns = patterns
        self.checked_patterns = self.check_patterns()
        self.variables_dict = {}
        self._process_variables()
        
    def check_patterns(self):
        if type(self.original_patterns) != type([]):
            raise RuntimeError, 'Patterns must be in a list'

        checked_patterns = []
        for pattern in self.original_patterns:

            if len(pattern) < 3:
                raise RuntimeError, 'Pattern must have a minimum length of 3'
            elif len(pattern) == 3:
                checked_patterns.append(pattern)
            else:
                aligned_i = 1
                start_i = 0
                for i in range(len(pattern)):
                    if i > 0 and (aligned_i % 3) == 0:
                        checked_patterns.append(tuple(pattern[start_i:(i+1)]))
                        start_i = i
                        aligned_i += 1
                    aligned_i += 1
        for checked_pattern in checked_patterns:
            if len(checked_pattern) == 3:
                
                if type(checked_pattern[0]) == type(""):
                    pass
                else:
                    raise RuntimeError, "variable in pattern must be a string"

                if type(checked_pattern[1]) == type(""):
                    pass
                else:
                    raise RuntimeError, "variable in pattern must be a string"
                if type(checked_pattern[2]) == type(""):
                    pass
                else:
                    raise RuntimeError, "variable in pattern must be a string"
            else:
                raise RuntimeError, "Pattern length is not correct"

        return checked_patterns

    def _process_variables(self):
        variable_position = 0
        for pattern in self.checked_patterns:
            for variable in pattern:
                if variable in self.variables_dict:
                    pass
                else:
                    self.variables_dict[variable] = variable_position
                    variable_position += 1
    def patterns(self):
        return self.checked_patterns

    def variables(self):
        return self.variables_dict
    
class TripleRestrictions(object):
    def __init__(self, restrictions, variables = None):
        self.variables = variables
        self.original_restrictions = restrictions
        self.processed_restrictions = ""
        self._check_restrictions()
        self.restrictions_variables = {}
        self.uris_inclusions = {}
        self.literals_inclusions = {}
        self.uris_exclusions = {}
        self.literals_exclusions = {}
        self._process_restrictions()

    def restrictions(self):
        return self.original_restrictions

    def _check_restrictions(self):
        if type(self.original_restrictions) != type([]):
            raise RuntimeError, "Restrictions must be in a list"
        for restriction in self.original_restrictions:
            if len(restriction) == 3 or len(restriction) == 4 or len(restriction) == 5:
                pass
            else:
                raise RuntimeError, "Restriction is of wrong length"
            if restriction[1] not in ("==","!=","in", "not in"):
                raise RuntimeError, "Unsupported restriction type '%s'" % restriction[1]

    def _process_restrictions(self):
        i = 0
        for restriction in self.original_restrictions:
            variable1 = restriction[0]
            if restriction[1] in ["==", "!="]:
                if variable1 not in self.restrictions_variables:
                    self.restrictions_variables[variable1] = [i]
                else:
                    self.restrictions_variables[variable1].append(i)
                variable2 = restriction[2]
                if variable2 not in self.restrictions_variables:
                    self.restrictions_variables[variable2] = [i]
                else:
                    self.restrictions_variables[variable2].append(i)
            elif restriction[1] == "in":
                literals = []
                uris = []
                for element in restriction[2]:
                    if len(element):
                        if element[0] == "<" and element[-1] == ">":
                            uris.append(element)
                        else:
                            literals.append(element)
                    else:
                        literals.append(element)
                if len(uris):
                    if variable1 not in self.uris_inclusions:
                        self.uris_inclusions[variable1] = uris
                    else:
                        self.uris_inclusions[variable1] += uris
                if len(literals):
                    if variable1 not in self.literals_inclusions:
                        self.literals_inclusions[variable1] = literals
                    else:
                        self.literals_inclusions[variable1] += literals
            elif restriction[1] == "not in":
                literals = []
                uris = []
                for element in restriction[2]:
                    if element[0] == "<" and element[-1] == ">":
                        uris.append(element)
                    else:
                        literals.append(element)
                if len(uris):
                    if variable1 not in self.uris_inclusions:
                        self.uris_exclusions[variable1] = uris
                    else:
                        self.uris_exclusions[variable1] += uris
                if len(literals):
                    if variable1 not in self.literals_inclusions:
                        self.literals_exclusions[variable1] = literals
                    else:
                        self.literals_exclusions[variable1] += literals
            i += 1
            
    def literal_inclusions(self):
        return self.literals_inclusions

    def uri_inclusions(self):
        return self.uris_inclusions

    def variable_restrictions(self):
        return self.restrictions_variables

    def uri_exclusions(self):
        return self.uris_exclusions

    def literal_exclusions(self):
        return self.literals_exclusions


class ResultFormatter(object):
    def __init__(self,variable):
        self.variable = variable
    def evaluate(self,value):
        return value

class is_literal(ResultFormatter):
    def evaluate(self, value):
        if value[0] == '"' and value[-1] == '"':
            return '"1"'
        else:
            return '"0"'

class IteratorTripleStore(object):
    def __init__(self,triple_engine):
        self.triple_engine = triple_engine
        self.triple_address_iterator = self.triple_engine.te.triples.iterkeys()
    def __iter__(self):
        return self

    def next(self):
        triple_address = self.triple_address_iterator.next()
        return self.triple_engine.triple_address_to_simple_triple(triple_address)

class IteratorTripleStoreNtriple(IteratorTripleStore):
    def next(self):
        triple_address = self.triple_address_iterator.next()
        return self.triple_engine.triple_address_to_simple_triple(triple_address).to_ntriple()


class ExtractGraphFromSimpleTripleStore(object):
    """
        Extract a subgraph from a SimpleTripleStore and translate
        it into a GraphML compliant format for graph analysis.
    """

    def __init__(self, triple_store_object):
        self.ts = triple_store_object
        self.node_predicate_mappings = {}
        self.node_reverse_predicate_mappings = {}
        self.patterns_for_links = []
        self.referenced_uris = {}
        self.global_id = 1
        self.patterns_result_sets = []
        self.uri_label = "uri"
        self.publish_uri = 1

    def add_pattern_for_links(self, pattern, restrictions=[], variables = ('a','b'), link_name=None):
        self.patterns_for_links.append((pattern, restrictions, variables, link_name))

    def register_node_predicate(self,uri,mapped_name):
        self.node_predicate_mappings[mapped_name] = uri
        self.node_reverse_predicate_mappings[uri] = mapped_name

    def register_label(self, uri="<http://www.w3.org/2000/01/rdf-schema#label>"):
        self.register_node_predicate(uri,"Label")

    def publish_uri(self):
        self.publish_uri = 1

    def register_class(self, uri="<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"):
        self.register_node_predicate(uri,"Class")

    def populate_referenced_nodes(self, pattern_match_results):
        for pm_result in pattern_match_results:
            if pm_result[0][0] in self.referenced_uris:
                pass
            else:
                self.global_id += 1
                self.referenced_uris[pm_result[0][0]] = self.global_id

            if pm_result[0][1] in self.referenced_uris:
                pass
            else:
                self.global_id += 1
                self.referenced_uris[pm_result[0][1]] = self.global_id

    def translate_into_graphml_file(self,fileout=None):
        from graph import GraphML
        import StringIO

        if fileout is None:
            fo = StringIO.StringIO()
        else:
            fo = fileout

        for pattern in self.patterns_for_links:
            pattern_results = self.ts.simple_pattern_match(pattern[0], pattern[1], pattern[2])
            self.populate_referenced_nodes(pattern_results)
            self.patterns_result_sets.append(pattern_results)

        graphml_obj = GraphML()
        xml_string = ""
        xml_string += graphml_obj.open_xml()
        n_node_keys = 1

        node_key_map = {}
        for node_key in self.node_predicate_mappings.keys():
            key_identifier = "nodeKey" + str(n_node_keys)
            xml_string += graphml_obj.define_key(key_identifier, "node", node_key, "string")
            node_key_map[node_key] = key_identifier
            n_node_keys += 1

        if self.publish_uri:
            uri_node_key = "nodeKey" + str(n_node_keys)
            xml_string += graphml_obj.define_key(uri_node_key, "node", self.uri_label, "string")

        edge_key_map = {}
        xml_string += graphml_obj.weight_key()
        edge_key_map["weight"] = graphml_obj.weight_key_id
        xml_string += graphml_obj.define_key("EdgeKey1","edge","Label","string")
        edge_key_map["Label"] = "EdgeKey1"

        xml_string += graphml_obj.open_graph("g0","directed")
        fo.write(xml_string)
        xml_string = ""

        print("Publishing nodes")
        for node in self.referenced_uris.keys():
            node_id = self.referenced_uris[node]
            xml_string += graphml_obj.open_node(node_id)
            associated_subject_triples = self.ts.subjects(node)

            predicate_map = {}

            if associated_subject_triples:
                for triple in associated_subject_triples:
                    predicate_map[triple[1]] = triple[2]

                for uri in self.node_reverse_predicate_mappings.keys():
                    if uri in predicate_map:
                        key_identifier = node_key_map[self.node_reverse_predicate_mappings[uri]]
                        if len(predicate_map):
                            data_string = predicate_map[uri][1:-1]
                        xml_string += graphml_obj.data(key_identifier, xml_escape(data_string))
            if self.publish_uri:
                xml_string += graphml_obj.data(uri_node_key, xml_escape(node[1:-1]))

            xml_string += graphml_obj.close_node()
            fo.write(xml_string)
            xml_string = ""

        print("Publishing edges")
        i = 0

        for pattern_result_set in self.patterns_result_sets:
            j = 0

            for pattern_result in pattern_result_set:
                uri1 = pattern_result[0][0]
                uri2 = pattern_result[0][1]
                weight = pattern_result[1]

                uri1_id = self.referenced_uris[uri1]
                uri2_id = self.referenced_uris[uri2]

                xml_string += graphml_obj.open_edge(j,uri1_id, uri2_id)
                xml_string += graphml_obj.data(edge_key_map["weight"],weight)
                xml_string += graphml_obj.data(edge_key_map["Label"],self.patterns_for_links[i][-1])
                xml_string += graphml_obj.close_edge()

                fo.write(xml_string)
                xml_string = ""

                j += 1
            i+= 1

        xml_string += graphml_obj.close_graph()
        xml_string += graphml_obj.close_xml()
        fo.write(xml_string)

        if fileout:
            return fo
        else:
            return fo.getvalue()