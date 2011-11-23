# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="janos"
__date__ ="$Jun 7, 2011 11:10:39 AM$"

from xml.sax.saxutils import escape
import time

class GephiGexf(object):
    """A class for generating gephi xml graphs that are read by Gephi"""
    def __init__(self):
        pass
    
    def xml_header(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
        <gexf xmlns="http://www.gexf.net/1.2draft"
        xmlns:xsi="http://www.w3.org/2001/XMLSScehma-instance"
        xmlns:viz="http://www.gexf.net/1.2draft/viz"
        xsi:schemaLocation="http://www.gexf.net/1.2draft
                            http://www.gexf.net/1.2drfat/gexf.xsd"
        version="1.2">\n"""
        
    def metadata(self,creator="pyTripleSimple.py",description=""):
        return """\t<meta lastmodifieddate="%s">
\t\t<creator>%s</creator>
\t\t<description>%s</description>
\t</meta>\n""" % (escape(time.strftime("%Y-%m-%d")), escape(creator), escape(description))
    
    def open_graph(self,default_graph_type="directed"):
        return 2 * '\t' + '<graph defaultgetype="%s">' % escape(default_graph_type)
    
    def close_xml(self):
        return "</gexf>\n"
    
    def close_graph(self):
        return 2 * '\t' + "</graph>\n"
    
    def open_attributes(self,class_attr):
        return 3 * '\t' + '<attributes class="%s">\n' % escape(class_attr)
    
    def close_attributes(self):
        return 3 * '\t'+ '</attributes>\n'
    
    def open_attribute(self,id,title,attr_type="string"):
        return 4 * '\t' + '<attribute id="%s" title="%s" type="%s">\n' % (escape(id), escape(title), escape(attr_type))
    
    def close_attribute(self):
        return 4 * '\t' + '</attribute>\n'
    
    def default_value(self,default_value):
        return 5 * '\t' + 't<default>%s</default>\n' % default_value
    
    def open_nodes(self):
        return 5 * '\t' + '<nodes>\n'
    
    def close_nodes(self):
        return 5 * '\t' + '</nodes>\n'
    
    def open_node(self, id, label, size="1.0"):
        return 6 * '\t' + '<node id="%s" label="%s"><viz:size value="%s"/>\n' % (id,escape(label),size)
    
    def close_node(self):
        return 6 * '\t' +'</node>\n'
    
    def open_attvalues(self, for_class_id,value):
        return 7 * '\t' + '<attvalues for="%s" value="%s">\n' % (for_class_id,value)
    
    def close_attvalues(self):
        return '</attvalues>\n'
    
    def open_edges(self):
        return 5 * '\t' + "<edges>\n"
    
    def close_edges(self):
        return 5 * '\t' + "</edges>\n"
    
    def open_edge(self,id,source,target, weight=1):
        return 6 * '\t' + '<edge id="%s" source="%s" target="%s" weight="%s">\n' % (id,source,target,weight)
    
    def close_edge(self):
        return 6 * '\t' + '</edge>\n'

class GexfTriples(object):
    def export_to_gexml(self,gephi_xml_file_name):
        """Gexml is native format for the Gephi graphing program"""
        f = open(gephi_xml_file_name,"w")
        gexf = GephiGexf()
        f.write(gexf.xml_header())
        f.write(gexf.metadata())
        f.write(gexf.open_graph())

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