import urllib2
import re

class CTDFormParser:
    def __init__(self,domain="http://dmauldin.gdxbase.org/", script="page/DotHome"):
        self.domain = domain
        self.script = script
        self.species_filter = {}
        self.input_types = {}
        self.output_types = {}
        self.ourForm = {}
        self.out_types_meta = [] 
        self.parse(domain+script)

    def setStatic(self):
        self.ourForm['id_list'] = ""
        self.ourForm['submit'] = 'Search'
        self.ourForm['collapse_results'] = False 
        self.ourForm['collapse_separator'] = ' ,'
        self.ourForm['limit_num'] = "5000"
        self.ourForm['group_results'] = True
        self.ourForm['orthologs'] = True
        self.ourForm['limit'] = True

    def parse(self, url="http://dmauldin.gdxbase.org/page/DotHome"):
        f = urllib2.urlopen(url) 
        for line in f.readlines():
            for re_obj, pFunc in self.getMatchers():
                match_obj = re_obj.search(line)
                if match_obj:
                    pFunc(match_obj)
                    break

    def parseInputTypes(self, m_input_types):
        option_dict =  m_input_types.groupdict()
        if option_dict['selected'] == 'yes':
            self.ourForm['input_type'] = option_dict['val']
        self.input_types[option_dict['val']] = option_dict['desc']
 
    def parseOutputTypes(self, m_output_type):
        temp_dict = m_output_type.groupdict()
        self.output_types[temp_dict['value']] = False
        self.out_types_meta.append((temp_dict['type'],temp_dict['value'], temp_dict['desc']))

    def parseSpecies(self, m_species):
        s_dict = m_species.groupdict()
        self.species_filter[s_dict['species']] = s_dict['checked']

    def parseSubmitURL(self, m_submit_url):
        su_dict = m_submit_url.groupdict()
        self.ourForm['submit_script'] = su_dict['submit_script']

    def getMatchers(self):
        #TODO: read these from file?
        re_output_types = re.compile(r'<input type="checkbox" name="output_type" value="(?P<value>\w+)" id="ot_\d+" class="(?P<type>\w+)_cb" /><label for="ot_\d+">(?P<desc>[\w\s]+)</label>' )
        re_species = re.compile('<input type="checkbox" name="species" value="(?P<species>\w+)" id="\w+" checked="(?P<checked>\w+)" />')
        re_input_types = re.compile(r'value="(?P<val>\w+)"[\w\s=]*"?(?P<selected>[\w]*)"?>(?P<desc>[\s\w]+)<')
        re_submit_url = re.compile(r'<form id=\'ctd_input_form\' method=\'POST\' action=\'(?P<submit_url>[\w/:\.]+)\'')
        matcher = []
        matcher.append((re_submit_url, self.parseSubmitURL))
        matcher.append((re_input_types, self.parseInputTypes))
        matcher.append((re_output_types, self.parseOutputTypes))
        matcher.append((re_species, self.parseSpecies))
        return matcher
    def test(self, url):
        f = urllib2.urlopen(url) 
        re_obj = re.compile(r'<form id=\'ctd_input_form\' method=\'POST\' action=\'(?P<submit_url>[\w/:\.]+)\'')
        for line in f.readlines():
                match_obj = re_obj.search(line)
                if match_obj:
                    print "*" * 25

        
if __name__ == "__main__":
    from SOFTParser import SOFTParser
    sp = SOFTParser("GDS2545.soft.gz")
    probes = sp.getID_REF()
    probes_str = '\n'.join(probes[:5000])
    print probes_str
    p = CTDFormParser()
    print "*" * 25
    print p.species_filter
    print "*" * 25
    print p.input_types
    print "*" * 25
    print p.input_types
    print "*" * 25
    print p.ourForm["input_type"]
    print "*" * 25
    print p.output_types
    print "*" * 25
    print p.out_types_meta
    print p.ourForm["submit_url"]
