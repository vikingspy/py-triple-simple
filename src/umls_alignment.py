#! /usr/bin/python

import time
import sys
import os
import pyTripleSimple
import urllib2
import httplib
import json
import re
from xml.sax.saxutils import unescape
import pprint

def umls_align(phrase):
    
    base_server = "link.informatics.stonybrook.edu" 
    base_app = "/MeaningLookup/"
    search_uri = "MlServiceServlet?textToProcess=%s&format=json" % urllib2.quote(phrase)
    conn = httplib.HTTPConnection(base_server)
    conn.request("GET",base_app + search_uri)
    
    resp = conn.getresponse()
    result_set = []
    if str(resp.status)[0] =="2":
        response = resp.read()

        umls_search_result = json.loads(response)
        if umls_search_result.has_key(u"Best Match"):
            best_matches = umls_search_result[u"Best Match"]
            for best_match in best_matches:
                umls_cui =  best_match[u"CUI"]
                umls_label = best_match[u"label"]
                result_set.append((umls_cui,umls_label))
        
        return result_set
    else:
        print("Call to server timed out")
        return []
            

def main(ntriples_file_name,alignment_ntriples_file_name,class_uri = "http://vivoweb.org/ontology/core#SubjectArea",predicate_to_align = "<http://www.w3.org/2000/01/rdf-schema#label>"):
    f = open(ntriples_file_name,"r")
    ts = pyTripleSimple.SimpleTripleStore()
    results_ts = pyTripleSimple.SimpleTripleStore()
    
    print('Loading "%s"' % os.path.abspath(ntriples_file_name))
    start_time = time.clock()
    ts.load_ntriples(f)
    end_time = time.clock()
    print("Finished loading ntriples file in %s seconds" % (end_time - start_time,))
    
    uris_to_align = [triple[0] for triple in ts.objects(class_uri)]

    umls_cuis = {}
    number_of_uris_to_align = len(uris_to_align)
    i = 1
    for uri_to_align in uris_to_align:
        for uri_to_align_triples in ts.subjects(uri_to_align):
            if uri_to_align_triples[1] == predicate_to_align:
                original_phrase = unescape(uri_to_align_triples[2][1:-1])
                phrases = re.split(r'(, |\. |; | and | or )', original_phrase)
                ntriples_results = ""
                print("Aligning: '%s' (%s/%s)" % (original_phrase,i,number_of_uris_to_align))
                ntriples_results += '%s <%s> "%s" .\n' %  (uri_to_align,"http://www.w3.org/2000/01/rdf-schema#label",original_phrase)
                for phrase in phrases:
                    if not(phrase == ', ' or phrase == '; ' or phrase == '. ' or phrase == ' and ' or phrase == ' or '):
                        umls_align_results = umls_align(phrase)
                        for umls_alignment in umls_align_results:
                            [umls_cui,umls_label] = umls_alignment
                            umls_cui_uri = "http://link.informatics.stonybrook.edu/umls/CUI/" + umls_cui
                            ntriples_results += "%s <%s> <%s> .\n" % (uri_to_align,"http://link.informatics.stonybrook.edu/MeaningLookup/mappedResearchConcept",umls_cui_uri)
                            if umls_cuis.has_key(umls_cui):
                                temp_list = umls_cuis[umls_cui]
                                n_cui = temp_list[0]
                                umls_cuis[umls_cui] = [n_cui + 1,temp_list[1]]
                            else:
                                umls_cuis[umls_cui] = (1,umls_label)
                                ntriples_results += '<%s> <%s> "%s"\n' % (umls_cui_uri,"http://www.w3.org/2000/01/rdf-schema#label",umls_label)
                                
                print(ntriples_results)
                results_ts.load_ntriples(ntriples_results.split("\n"))
        i = i + 1
    f.close()
    fw = open(alignment_ntriples_file_name,"w")
    fw.write(results_ts.export_to_ntriples_string())
    fw.close()
    
    pprint.pprint(umls_cuis)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main("reach.nt","subject_areas_aligned.nt")
    else:
        main(sys.argv[1],sys.argv[2])
    
