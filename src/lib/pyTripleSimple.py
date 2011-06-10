"""
Classes for processing and working with files that follow the ntriples format.
    
"""

import re
import shelve
import os

from gexf import GephiGexf

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
        "By default the callback function will just print the result"
        print(result)
        return result_obj
    
    def process(self):
        "Begin the process of a set of ntriples"
        for unparsed_statement in self.iterable_stream:
            matching_result = self.match_function(unparsed_statement)
            if matching_result:
                self.result_obj = self.call_back_function(matching_result,self.result_obj)
    
    def result_obj(self):
        "Returns result obj"
        return self.result_obj
    
    
class SimpleNtripleExtractor(object):
    """
        This is the simplest of ntriples extractor. It ignores language tags and 
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
        "Parse a line of ntriples text extracting"
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
                if (line[i] == '"' and line[i-1] != "\\"):
                    state = "LiteralEnd"
                    triples.append(line[start_state_position:i])
                    triple_types += "l"
                elif line[i] == '"' and line[i-1] == "\\" and line[i-2] == "\\":
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
    "A basic container for a triple"
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
        return (self.subject,self.predicate,self.object)
    def __repr__(self):
        return str(self.to_tuple())
 
    
class TripleEngine(object):
    """In memory model of a triple store uses native python dictionaries for 
    indexing."""
    
    def __init__(self):
        self.symbols = {}
        self.triples = {}
        self.objects = {}
        self.subjects_index = {}
        self.objects_index = {}
        self.predicates_index = {}
        
    def key_store(self, key_value):
        "Some persistent stores do not allow non-string keys so take a key and do something if needed"
        return key_value
    
    def key_retrieve(self, key_value):
        return key_value
    
    def triple_store(self,triple):
        "In case when storing triples we need to some processing this will define the behavior"
        return triple
    
    def triple_retrieve(self,triple):
        return triple
    
class ShelveTripleEngine(TripleEngine):
    """Shelve is a persistent store based on python shelve module.  
    Currently it does not scale very well"""
    
    def __init__(self, base_file_name=""):
        self.symbols = shelve.open(os.path.join(base_file_name + "_identities"))
        self.triples = shelve.open(os.path.join(base_file_name + "_triples"))
        self.objects = shelve.open(os.path.join(base_file_name + "_objects"))
        self.subjects_index = shelve.open(os.path.join(base_file_name + "_subjects_index"))
        self.predicates_index = shelve.open(os.path.join(base_file_name + "_predicates_index"))
        self.objects_index = shelve.open(os.path.join(base_file_name + "_objects_index"))
        
    def key_store(self,key_value):
        return str(key_value)
    def key_retrieve(self,key_value):
        return int(key_value)
        
class SimpleTripleStore(object):
    """A class for encapsulating triple store behavior.  The class does not provide SPARQL
        support or default graph, inferenceing but is designed for manipulating and processing data
        represented in a ntriples file."""
        
    def __init__(self,triple_engine=None):
        "By default use memory based backend"
        
        if triple_engine is None: #By default load native model in
            self.triple_engine = TripleEngine()
        else:
            self.triple_engine = triple_engine
        
        self.te = self.triple_engine # shortcut attribute
        
    def n_symbols(self):
        "Symbols are integers that map to a string."
        return len(self.te.symbols)
    
    def n_triples(self):
        "Returns the number of statements/triples in a store"
        return len(self.te.triples)
    
    def n_objects(self):
        "Number of distinct objects in the spo sense"
        return len(self.te.objects_index)
    
    def n_predicates(self):
        "Number of distinct predicates"
        return len(self.te.predicates_index)
    
    def n_subjects(self):
        "Number of dstinct subjects"
        return len(self.te.subjects_index)
    
    def add_triple(self,triple_object):
        "Add a triple to the store"
        
        triple = triple_object.to_tuple()
        
        t1 = triple[0]
        t2 = triple[1]
        t3 = triple[2]
        
        t1_symbol = self._add_symbol(t1)
        t2_symbol = self._add_symbol(t2)
        t3_symbol = self._add_symbol(t3)
                
        t1_addr = triple_object.subject_type() + str(t1_symbol)
        t2_addr = triple_object.predicate_type() + str(t2_symbol)
        t3_addr = triple_object.object_type() + str(t3_symbol)
        
        self.te.objects[t1_addr] = t1
        self.te.objects[t2_addr] = t2
        self.te.objects[t3_addr] = t3
        
        triple_address = self.n_triples() + 1
        self.te.triples[self.te.key_store(triple_address)] = self.te.triple_store((t1_addr,t2_addr,t3_addr))
        
        #Build indices for quicker retrieval
        
        if self.te.subjects_index.has_key(t1_addr):
            self.te.subjects_index[t1_addr].append(triple_address)
        else:
            self.te.subjects_index[t1_addr] = [triple_address]
            
        if self.te.predicates_index.has_key(t2_addr):
            self.te.predicates_index[t2_addr].append(triple_address)
        else:
            self.te.predicates_index[t2_addr] = [triple_address]
            
        if self.te.objects_index.has_key(t3_addr):
            self.te.objects_index[t3_addr].append(triple_address)
        else:
            self.te.objects_index[t3_addr] = [triple_address]
        
        return triple_address
        
    def load_ntriples(self,iterable_ntriples):
        "Load an ntriples iterable into the store"
        extractor = SimpleNtriplesParser()
        for ntriple in iterable_ntriples:
            extracted_results = extractor.parse(ntriple)
            for extracted_result in extracted_results: 
                self.add_triple(extracted_result)
                     
    def _add_symbol(self,item):
        "Add a symbol"
        if self.te.symbols.has_key(item):
            symbol_address = self.te.key_retrieve(self.te.symbols[item])
        else:
            symbol_address = self.n_symbols() + 1
            self.te.symbols[item] = self.te.key_store(symbol_address)
        return symbol_address
    
    def _decode_address(self,address):
        return self.te.objects[address]
    
    def _decode_triple_symbols(self,triple_address):
        triple = self.te.objects[triple_address]
        t1 = self._decode_address(triple[0])
        t2 = self._decode_address(triple[1])
        t3 = self._decode_address(triple[2])
        return (t1,t2,t3)
    
    def _decode_triple(self,triple_address):
        """Given an address to a triple decodes it without ntriples formatting,
        as an example the uri http://example.org is not shown as 
        <http://example.org>
        """
        triple = self.te.objects[triple_address]
        t1 = self._decode_address(triple[0])
        t2 = self._decode_address(triple[1])
        t3 = self._decode_address(triple[2])
        return (t1,t2,t3)
    
    def _format_symbol(self,symbol, object_type):
        if object_type == "u":
            return "<" +  symbol + ">"
        if object_type == "l":
            return '"' + symbol + '"'
        if object_type == "b":
            return symbol
        
    def _decode_address_formatted(self,object_address):
        "Pass in a reference to an object and decodes it"
        return self._format_symbol(self._decode_address(object_address),object_address[0]) 
    
    def _decode_triple_formatted(self, triple_address):
        "Formats triples into an address formatted"
        triple = self.te.triples[triple_address]
        t1 = self._decode_address_formatted(triple[0])
        t2 = self._decode_address_formatted(triple[1])
        t3 = self._decode_address_formatted(triple[2])
        return (t1,t2,t3)
    
    def _encode_uri(self,uri):
        "Encode a uri into a referencable address"
        if self.te.symbols.has_key(uri):
            sym_addr = self.te.symbols[uri]
            return 'u' + str(sym_addr)
        else:
            return 0
        
    def _encode_literal(self,literal):
        "Encode a literal into a referencable address"
        if self.symbol.has_key(literal):
            sym_addr = self.te.symbols[literal]
            return 'l' + sym_addr
        else:
            return 0
        
    def subjects(self,uri):
        "For a subject specifeid by a uri return all associated triples"
        if uri[0] == "<" and uri[-1] ==  ">":
            uri = uri[1:-1]
        uri_addr = self._encode_uri(uri)
        if uri_addr:
            if self.te.subjects_index.has_key(uri_addr):
                return [self._decode_triple_formatted(t) for t in self.te.subjects_index[uri_addr]]
            
    def objects(self,uri):
        "For an object specified by uri return all associated triples"
        if uri[0] == "<" and uri[-1] ==  ">":
            uri = uri[1:-1]
        uri_addr = self._encode_uri(uri)
        
        if uri_addr:
            if self.te.objects_index.has_key(uri_addr):
                return [self._decode_triple_formatted(t) for t in self.te.objects_index[uri_addr]]
        
    def predicates(self,uri):
        "For an object specified by uri return all associated tiples"
        if uri[0] == "<" and uri[-1] ==  ">":
            uri = uri[1:-1]
        uri_addr = self._encode_uri(uri)
        
        if uri_addr:
            if self.te.predicates_index.has_key(uri_addr):
                return [self._decode_triple_formatted(t) for t in self.te.predicates_index[uri_addr]]
            
    def export_to_ntriples_file(self,f):
        "For file object wirte the triples to file"
        for key in self.te.triples.keys():
            triple = self._decode_triple_formatted(key)
            f.write( "%s %s %s .\n" % triple)
        return f
        
    def export_to_ntriples_string(self):
        "Export ntriples to an memory string"
        nt = ""
        for key in self.te.triples.keys():
            triple = self._decode_triple_formatted(key)
            nt +=  "%s %s %s .\n" % triple
        return nt
        
    def n_literals(self):
        "Returns the number of literals in the store"
        i = 0
        for key in self.te.objects.keys():
            if key[0] == "l":
                i += 1
        return i
                 
    def _n_objects(self,hash_index):
        "Creates a reverse sorted list of addresses with keys"
        keys = hash_index.keys()
        keys_with_len = []
        for key in keys:
            keys_with_len.append((key,len(hash_index[key])))
            
        keys_with_len.sort(key=lambda x: x[1],reverse=True)
        
        return keys_with_len
    
    def _top_items(self,hash_index,top_n=None):
        "Private method for calculating a sorted list"
        keys_with_len = self._n_objects(hash_index)
        
        if top_n is not None:
            keys_with_len = keys_with_len[0:top_n]
            
        return [(self._decode_address_formatted(top_subject[0]),top_subject[1]) for top_subject in keys_with_len]
    
    def top_subjects(self,top_n = 25):
        "Returns a list of top referenced subjects"
        return self._top_items(self.te.subjects_index,top_n)
    
    def top_objects(self,top_n = 25):
        "Returns a list of of top referenced objects"
        return self._top_items(self.te.objects_index,top_n)
    
    def top_predicates(self, top_n=25):
        "Returns a list of top used predicates"
        return self._top_items(self.te.predicates_index,top_n)
    
    def export_to_gexml(self,gephi_xml_file_name):
        "Gexml is native format for the Gephi graphing program"
        f = open(gephi_xml_file_name,"w")
        gexf = GephiGexf()
        f.write(gexf.xml_header())
        f.write(gexf.metadata())
        f.write(gexf.open_graph())
        
#        f.write(gexf.open_attributes("nodes"))
#        f.write(gexf.open_attribute("0","uri","string"))
#        f.write(gexf.close_attribute())
#        f.write(gexf.close_attributes())
#        
#        f.write(gexf.open_attributes("edges"))
#        f.write(gexf.open_attribute("0","uri","string"))
#        f.write(gexf.close_attribute())
#        f.write(gexf.close_attributes())
        
        f.write(gexf.open_nodes())
        for object in self.te.objects.keys():
            value = self.te.objects[object]
            if object[0] == "l":
                associated_triples_address = self.te.objects_index[object]
                for triple_address in associated_triples_address:
                    f.write(gexf.open_node("t" + str(triple_address),value))
                    f.write(gexf.close_node())
            else:
                f.write(gexf.open_node(object,value))
                f.write(gexf.close_node())
        f.write(gexf.close_nodes())
        
        f.write(gexf.open_edges())
        
        for triple_addr in self.te.triples.keys():
            triple = self.te.triples[triple_addr]
            if triple[2][0] == "l":
                f.write(gexf.open_edge(triple_addr,triple[0],"t" + str(triple_addr)))
            else:
                f.write(gexf.open_edge(triple_addr,triple[0],triple[2]))
            f.write(gexf.close_edge())
        
        f.write(gexf.close_edges())
        
        f.write(gexf.close_graph())
        f.write(gexf.close_xml())
        
