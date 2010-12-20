class SOFTParser:
    """A parser for SOFT formatted datasets GEO SOFT format is documented here:
http://www.ncbi.nlm.nih.gov/projects/geo/info/soft2.html#SOFTformat
Note the docs do not describe everything.
    """
    def __init__(self, filename):
        """
        filename is the name of the file you wish to parse.
        Should handle .soft and .soft.gz
        """
        self.filename = filename
        self.lock = []  #this locks the table if another class has edited it
        if(filename.endswith('.gz')):
            #if its zipped, lets unzip
            import gzip 
            f = gzip.open(filename,'rb')
            self.raw_content = f.readlines()
            f.close()
        else:
            f = open(filename,'r')
            self.raw_content = f.readlines()
            f.close()
        self.getData()


    def getData(s):
        """
        This is a private helper method that actually breaks the data up into manageable chunks.
        Truly it is the primary worker/parser
        NOTE: this should be broken up into subfunctions
        """
        s.entities = [] 
        s.column_heading = []
        s.column_heading_info = []
        s.row_heading = []
        s.row_heading_index = []
        s.id_ref_column = None
        s.identifier_column = None
        
        s.tables = []
        for line in s.raw_content:
            if line[0] == '^':
                ent = line[1:].split('=',1)
                s.entities.append(entity(ent[0].strip(),ent[1].strip()))
                state = 1
            elif line[0] == '!':
                att = line[1:].split('=',1)
                if(len(att) == 2):
                    if att[0].strip() not in s.entities[-1].attributes:
                        s.entities[-1].attributes[att[0].strip()] = [att[1].strip()]
                    else:
                        s.entities[-1].attributes[att[0].strip()].append(att[1].strip())
                    state = 2
                    
            elif line[0] == '#':
                if state != 3:
                    #these get set and created in getRowHeading and setRowHeading
                    #s.row_heading.append([])
                    #s.row_heading_index.append(None)
                    s.column_heading.append([])
                    s.column_heading_info.append([])
                head = line[1:].split('=', 1)
                s.column_heading[-1].append(head[0].strip())
                s.column_heading_info[-1].append((head[0].strip(), head[1].strip()))
                state = 3
            else:
                if state != 4:
                    s.lock.append(False)
                    s.tables.append([])
                row = line.strip().split('\t') 
                if row != s.column_heading[-1]:#dont add header column
                    s.tables[-1].append(row)
                state = 4
    

    def getEntities(self):
        """
        Returns a list of entities
        Entities are meta-data objects.
        they have a type, value and a dict of attributes
        """
        return self.entities

    def getNumTables(self):
        """
        Returns the number of tables in the SOFTParser object
        At this point, this class cannot handle multiple tables, or at least
        I should say that I have not tested it on multiple tables.

        When I find a SOFT file that contains multiple tables I will get it working.
        """        
        return len(self.tables)

    def getTable(self, tableNum=0, lock=False):
        """
        Returns the data table at index tableNum, defaults to the first table
        """
        if self.lock[tableNum]:
            raise Exception, "The parser has given up control of the table"
        self.lock[tableNum] = lock
        return self.tables[tableNum]

    def getColumnHeadings(self, tableNum=0):
        """
        Returns a list of all column headings
        """
        return self.column_heading[tableNum]

    def getColumnHeadingsInfo(self,tableNum = 0):
        """
        Returns a list of tuples containing (column heading, column description)
        """
        return self.column_heading_info[tableNum]

    def setRowHeadings(self, colNum, tableNum=0):
        """
        This lets the user set the column that contains the row classifications.
        In this case that means the gene names.
        """
        raise Exception, "SOFTParser.setRowHeadings is deprecated"
        self.row_heading_index[tableNum] = colNum;

    def getRowHeadings(self, tableNum = 0 ):
        """
        ************DEPRECATED*********************
        use getID_REF and getIDENTIFIER as row labels
This returns list of the row headings in the order they
exist in the table"""
        raise Exception, "SOFTParser.getRowHeadings is deprecated"
        if self.row_heading_index[tableNum] and len(self.row_heading[tableNum]) == 0:
            self.row_heading[tableNum]
            rh_index = self.row_heading_index[tableNum]
            
            for row in self.tables[tableNum]:
                self.row_heading[tableNum].append(row[rh_index])
        elif not self.row_heading_index[tableNum]:
            raise Exception, "You must set the column of the row heading."
        
        return self.row_heading[tableNum]

    def getID_REF(self, id_ref='ID_REF', tableNum=0):
        """
        It appears that this is a required column in SOFT data tables.
        It is required to correspond to the probes.  This in general should be our key
        It will probably be the first column, but we can't really be sure
        This function returns the ordered values of this column for mapping
        back to the rows.
        Each value should be unique
        """
        
        if self.id_ref_column is None:
            column_heading_index = None
            counter = 0
            for column_heading in self.getColumnHeadings():
                if column_heading == id_ref:
                    column_heading_index = counter
                counter += 1
            if column_heading_index is None:
                raise Exception, "This SOFT file has no ID_REF column"
            self.id_ref_column = [ row[column_heading_index] for row in self.tables[tableNum] ]
        return self.id_ref_column

    def getIDENTIFIER(self,identifier_label='IDENTIFIER',tableNum = 0):
        """
        This is not guaranteed to be there, but so far it has been.
        If it is not available we will have to handle it somehow
        This should map to genes and each value will not be unique.
        """
        if self.identifier_column is None:
            column_heading_index = None
            counter = 0
            for column_heading in self.getColumnHeadings():
                if column_heading == identifier_label:
                    column_heading_index = counter
                counter += 1
            if column_heading_index is None:
                raise Exception, "This SOFT file has no IDENTIFIER column"
            self.identifier_column = [ row[column_heading_index] for row in self.tables[tableNum] ]
        return self.identifier_column
 

    def getDataColumnHeadings(self):
        """
        Using the subset entities, this function returns the data column names.
        This is actually the union of the subsets.
        """
        dch = []
        for entity in self.getSubsets():
            for sample in self.getSubsetSamples(entity):
                dch.append(sample)
        return dch
    
    def getKeyColumnHeadings(self):
        """
        Returns any non data column headers.
        i.e. COLUMN_HEADINGS - getDataColumnHeadings()
        """
        dch = self.getDataColumnHeadings()
        kch = []
        for h in self.getColumnHeadings():
             if h not in dch:
                kch.append(h)
        return kch

    def getSubsets(self):
        """
        Returns a list of all entities that are marked as subsets
        """
        subsets = []
        for entity in self.entities:
            if entity.type == 'SUBSET':
                subsets.append(entity)
        return subsets
        
    def getSubsetSamples(self, subset):
        """
        Returns a list of the subset sample id's found in subset entity
        """
        samples = subset.attributes['subset_sample_id'][0]
        return [x.strip() for x in samples.split(',')]

    def getNumTables(self):
        return len(self.tables)

    def printTable(self):
        for table in self.tables:
            for row in table:
                for value in row:
                    print value,
                    print ",",
                print
 
class entity:
    """
    A container for meta-data provided by the soft file.
    Type: the type of entity (Database, subset, etc)
    Value: usually a unique id
    attributes: a dict with related attributes where each key points to a list if provided values
    """
    def __init__(self, type, value):
        self.type = type
        self.value = value
        self.attributes = {}

    def __repr__(self):
        retstr = "<entity type:%s value:%s "%(self.type, self.value)
        for key, value in self.attributes.iteritems():
            retstr += " attributes[%s] : %s"% (key, value)
        retstr += ">"
        return retstr



if __name__ == "__main__":
    sp = SOFTParser("../data/GDS2545.soft.gz")
    for e in sp.entities:
        print e
        print
    """
    for info in sp.column_heading_info[0]:
        print info[0]
        print info[1]
    sp.printTable()
    for h in     sp.table_headings :
        for key in h.keys():
            print key
            print h[key][0]

    for h in sp.table_headings_ordered:
        for head in h:
            print head
    #sp.printTable()
"""
