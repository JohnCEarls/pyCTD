import urllib2
import re

class CTDFormParser:
    def __init__(self,url="http://dmauldin.gdxbase.org/page/DotHome"):
        self.species_filter = {}
        self.input_types = {}
        self.output_types = {}
        self.ourForm = {}
        self.out_types_meta = [] 
        self.parse(url)

    def setStatic(self):
        self.ourForm['id_list'] = ""
        self.ourForm['submit'] = 'Search'
        self.ourForm['collapse_results'] = False 
        self.ourForm['collapse_separator'] = ' ,'
        self.ourForm['limit_num'] = "5000"
        self.ourForm['group_results'] = True
        self.ourForm['orthologs'] = True
        self.ourForm['limit'] = True

    def parse(self, url):
        f = urllib2.urlopen("http://dmauldin.gdxbase.org/page/DotHome") 
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

    def getMatchers(self):
        #TODO: read these from file?
        re_output_types = re.compile(r'<input type="checkbox" name="output_type" value="(?P<value>\w+)" id="ot_\d+" class="(?P<type>\w+)_cb" /><label for="ot_\d+">(?P<desc>[\w\s]+)</label>' )
        re_species = re.compile('<input type="checkbox" name="species" value="(?P<species>\w+)" id="\w+" checked="(?P<checked>\w+)" />')
        re_input_types = re.compile(r'value="(?P<val>\w+)"[\w\s=]*"?(?P<selected>[\w]*)"?>(?P<desc>[\s\w]+)<')
        matcher = []
        matcher.append((re_input_types, self.parseInputTypes))
        matcher.append((re_output_types, self.parseOutputTypes))
        matcher.append((re_species, self.parseSpecies))
        return matcher

if __name__ == "__main__":
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
    
