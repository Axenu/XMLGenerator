import sys


debug = True
eol_ = '\n'

def dlog(string):
    if debug:
        print string


def pretty_print(fd, level, pretty):
    """
    Print some tabs to give the xml output a better structure
    """
    if pretty:
        for idx in range(level):
            os.write(fd, '    ')
def pretty_print_string(level, pretty):
    """
    Print some tabs to give the xml output a better structure
    """
    if pretty:
        for idx in range(level):
            sys.stdout.write('   ')

class xmlAttribute(object):
    '''
    A class to contain and handle each attribute of a XML element
    '''
    attrName = ''
    req = False
    value = ''

    def __init__(self, attrName, value=''):
        self.attrName = attrName
        self.value = value

    def printXML(self):
        """
        Print out the attribute
        """
        if self.value is not '':
            sys.stdout.write(' ' + self.attrName + '="' + self.value + '"')
            # os.write(fd, ' ' + self.attrName + '="' + self.value + '"')

    def XMLToString(self):
        """
        Print out the attribute
        """
        if self.value is not '':
            print ' ' + self.attrName + '="' + self.value + '"',

class textElement(object):
    '''
    A class conatining a single string
    '''
    def __init__(self, value):
        self.value = value

    def printXML(self, level=0, pretty=True):
        if self.value is not '':
            pretty_print_string(level, pretty)
            sys.stdout.write(self.value + eol_)

class xmlElement(object):
    '''
    A class containing a complete XML element, a list of attributes and a list of children
    '''

    def __init__(self, tagName='', namespace=''):
        self.tagName = tagName
        self.children = []
        self.attributes = []
        self.karMin = 0
        self.karMax = -1
        self.namespace = namespace
        self.completeTagName = ''
        self.extension = None
        self.printed = 0
        if self.namespace != '':
            self.completeTagName += self.namespace + ':'
        self.completeTagName += str(self.tagName)

    def setNamespace(self, namespace):
        """
        Changes the namespace of the element and updates the combined string
        """
        self.namespace = namespace
        self.completeTagName = ''
        if self.namespace != '':
            self.completeTagName += self.namespace + ':'
        self.completeTagName += self.tagName

    def printXML(self, level=0, pretty=True):
        """
        Print out the complete element.
        """
        if self.printed == 2:
            return False
        if self.printed == 0:
            # pretty_print(fd, level, pretty)
            pretty_print_string(level, pretty)
            sys.stdout.write('<' + self.completeTagName)
            # os.write(fd, '<' + self.completeTagName)
            for attribute in self.attributes:
                attribute.printXML()
        if self.children or self.containsFiles:
            if self.printed == 0:
                sys.stdout.write('>' + eol_)
                # os.write(fd, '>' + eol_)
            if not self.containsFiles or self.printed == 1:
                for child in self.children:
                    if child.printXML(level + 1, pretty):
                        self.printed = 1
                        return True
                    # pretty_print(fd, level + 1, pretty)
                    # os.write(fd, self.value + eol_)
                pretty_print_string(level, pretty)
                sys.stdout.write('</' + self.completeTagName + '>' + eol_)
                # pretty_print(fd, level, pretty)
                # os.write(fd, '</' + self.completeTagName + '>' + eol_)
                self.printed = 2
            else:
                self.printed = 1
                return True
        else:
            sys.stdout.write('/>' + eol_)
            # os.write(fd, '/>' + eol_)
            self.printed = 2

    def XMLToString(self, level=0, pretty=True):
        """
        Print out the complete element.
        """
        if self.printed == 2:
            return False
        if self.printed == 0:
            pretty_print_string(level, pretty)
            print '<' + self.completeTagName,
            for a in self.attributes:
                a.XMLToString()
        if self.children or self.value is not '' or self.containsFiles:
            if self.printed == 0:
                print '>' + eol_,
            if not self.containsFiles or self.printed == 1:
                for child in self.children:
                    if child.XMLToString(level + 1, pretty):
                        self.printed = 1
                        return True
                if self.value is not '':
                    pretty_print_string(level + 1, pretty)
                    print self.value + eol_,
                pretty_print_string(level, pretty)
                print '</' + self.completeTagName + '>' + eol_,
                self.printed = 2
            else:
                self.printed = 1
                return True
        else:
            print '/>' + eol_,
            self.printed = 2

    def isEmpty(self):
        """
        Simple helper function to check if the tag sould have any contents
        """
        if self.value != '' or self.children or self.containsFiles:
            return False
        else:
            return True

    def printDebug(self):
        """
        Method for debugging only, prints out the name of the element and all children
        """
        print self.tagName
        for child in self.children:
            child.printDebug()

    def addAttribute(self, attribute):
        """
        Add an attribute to the element
        """
        self.attributes.append(attribute)

    def addChild(self, el):
        """
        Add a child to the element and test if it should have the same namespace
        """
        # if el.namespace == '':
        #     el.setNamespace(self.namespace)
        self.children.append(el)


class xmlExtensionModule(object):

    def __init__(self):
        self.selector = ''
        self.requiresOneRunOnly = False

    def executeExtension(self, template, level, namespace, local_data):
        # to be overitten
        return True

    def executeExtensionOnce(self, xmlGenerator, states, json_data):
        # to be overitten
        return

class savedState(object):

    def __init__(self, local_data, template, level, namespace, fileID):
        self.local_data = local_data
        self.template = template
        self.level = level
        self.namespace = namespace
        self.fid = fileID

class fileObject():
    """
    A container class for all the files in the xml
    """
    def __init__(self, template, fid, fileName, local_data={}):
        self.template = template
        self.fid = fid
        self.local_data = local_data
        self.fileName = fileName
        self.files = []
        # self.rootElement = None
