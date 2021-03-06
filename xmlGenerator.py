import os
import json
import copy

from xmlStructure import xmlElement, xmlAttribute, fileObject, dlog, textElement, savedState
from xmlExtensions import xmlFilesExtenstionModule, inlineExtenstionModule

#TODO
# 1. add allowempty flag for elements with attrivutes only
# 2. Warn for empty required elements

# HELPER Methods

def pretty_print_string(level):
    """
    Print some tabs to give the xml output a better structure
    """
    res = ''
    for idx in xrange(level):
        res += '   '
    return res

class xmlGenerator(object):

    def __init__(self, input_data):
        self.filesToCreate = input_data['filesToCreate']
        self.json_data = input_data['data']
        self.extensions = []
        self.createdFiles = []
        self.numberOfFiles = 0
        self.currentFileID = None
        self.currentFob = None
        self.remainingParts = {}

    def addExtension(self, extension):
        self.extensions.append(extension)

    def resolveVar(self, var_name, local_data={}):
        parts = var_name.split('.')
        if len(parts) == 1:
            if parts[0] in self.json_data:
                return self.json_data[parts[0]]
            else:
                print 'MISSING var: ' + var_name + ' in json_data'
                return ''
        elif len(parts) <= 0:
            print 'ERROR: var can\'t be empty.'
        else:
            if parts[0] in local_data:
                temp = local_data[parts[0]]
                if parts[1] in temp:
                    return temp[parts[1]]
                else:
                    print 'MISSING var: ' + var_name + ' in localdata[' + parts[0] + ']'
                    return ''
            elif parts[0] in self.json_data:
                temp = self.json_data[parts[0]]
                if parts[1] in temp:
                    return temp[parts[1]]
                else:
                    print 'MISSING var: ' + var_name + ' in json_data[' + parts[0] + ']'
                    return ''
            else:
                print 'MISSING var: ' + var_name + ' in json_data'
                return ''

    def resolveContent(self, content, local_data={}):
        text = ''
        for textType in content:
            if 'type' in textType and textType['type'] == 'var':
                    # resolve var
                    text += self.resolveVar(textType['data'], local_data)
            else:
                #append text
                text += textType['data']
        return text

    def createXMLElement(self, template, level=0, namespace='', local_data={}, passed_print=''):
        if 'extension' in template:
            extension_name = template['extension']
            foundExtension = False
            for extension in self.extensions:
                if extension.selector == extension_name:
                    foundExtension = True
                    if extension.requiresOneRunOnly:
                        os.write(self.currentFileID, passed_print);
                        # Save this state for final one run parsing
                        state = savedState(local_data, template, level, namespace, self.currentFileID)
                        if extension.selector in self.remainingParts:
                            self.remainingParts[extension.selector].append(state)
                        else:
                            self.remainingParts[extension.selector] = [state]

                        # Create new fid for further parsing
                        fileName = 'temp' + str(self.numberOfFiles) + '.txt'
                        self.currentFileID = os.open(fileName,os.O_RDWR|os.O_CREAT)
                        self.currentFob.files.append(fileName)
                        self.numberOfFiles += 1

                    else:
                        # execute now
                        if extension.executeExtension(template, level, namespace, local_data):
                            haveChild = False
                            if 'children' in template:
                                for child in template['children']:
                                    if self.createXMLElement(child, level, namespace, local_data, passed_print):
                                        haveChild = True
                                        passed_print = ''
                            if not haveChild:
                                return False
                        pass
                    break
            if not foundExtension:
                print "ERROR: Extension \"" + extension_name + "\" is not loaded"
                return False
            return True
        if 'name' not in template:
            if 'content' in template:
                text = self.resolveContent(template['content'], local_data)
                if text != '':
                    os.write(self.currentFileID, passed_print + pretty_print_string(level) + text + '\n')
                    # print pretty_print_string(level) + text
                    return True
            else:
                print 'FATAL ERROR: missing name on xml Element'
            return False

        tagName = template['name']

        if 'namespace' in template:
            namespace = template['namespace']

        if namespace != '':
            tagName = namespace + ':' + tagName

        attributes = ''
        newElement = xmlElement(template['name'], namespace)
        if 'attributes' in template:
            #parse attribute
            for attribute in template['attributes']:
                if 'name' not in attribute:
                    print 'FATAL ERROR: missing name on xml attribute'
                    return False
                # solve text content
                if 'content' in attribute:
                    attributes += ' ' + attribute['name'] + '=\"' + self.resolveContent(attribute['content'], local_data) + '\"'

        haveChild = False
        if 'children' in template:
            # os.write(self.currentFileID, pretty_print_string(level) + '<' + tagName + attributes + '>\n')
            tempString = passed_print + pretty_print_string(level) + '<' + tagName + attributes + '>\n'
            for child in template['children']:
                if 'repeat' in child:
                    repeat = child['repeat'].split(' ')
                    var_name = repeat[1]
                    array_name = repeat[3]
                    array = self.resolveVar(array_name, local_data)
                    if isinstance(array, list):
                        i = 0
                        for o in array:
                            temp = dict(o)
                            temp['_index'] = i
                            local = dict(local_data)
                            if var_name not in local:
                                local[var_name] = temp
                            else:
                                print 'FATAL ERROR: Duplicate variable name in nested loops'
                                return False
                            if self.createXMLElement(child, level+1, namespace, local, tempString):
                                haveChild = True
                                tempString = ''

                            i += 1
                    else:
                        print 'FATAL ERROR: array not found'
                        return False
                else:
                    if self.createXMLElement(child, level+1, namespace, local_data, tempString):
                        haveChild = True
                        tempString = ''
            if haveChild:
                os.write(self.currentFileID, pretty_print_string(level) + '</' + tagName + '>\n')
        if haveChild == False:
            if attributes != '':
                os.write(self.currentFileID, passed_print + pretty_print_string(level) + '<' + tagName + attributes + '/>\n')
                return True
            else:
                return False
                print 'no attributes and no content in element: ' + tagName

        #return true if has content
        return True



    def createXML(self):
        """
        The task method for executing the xmlGenerator and completing the xml files
        This is also the TASK to be run in the background.
        """
        self.numberOfFiles = 1
        for item in self.filesToCreate:
            xmlFileName = item['xmlFileName']
            jsonTemplateName = item['templateFileName']
            json_template_file=open(jsonTemplateName).read()
            try:
                template = json.loads(json_template_file)#, object_pairs_hook=OrderedDict)
            except ValueError as err:
                print err # implement logger
                return  False
            name, rootE = template.items()[0] # root element
            self.currentFileID = os.open(xmlFileName,os.O_RDWR|os.O_CREAT)
            self.currentFob = fileObject(template, self.currentFileID, xmlFileName)
            self.createdFiles.append(self.currentFob)
            self.createXMLElement(template)

        for extensionName, states in self.remainingParts.iteritems():
            extention = None
            for ext in self.extensions:
                if ext.selector == extensionName:
                    extension = ext
                    break
            if extension != None:
                extension.executeExtensionOnce(self, states, self.json_data)


        for fob in self.createdFiles:
            for f in fob.files:
                fid = os.open(f, os.O_RDONLY)
                while True:
                    data = os.read(fid, 65536)
                    if data:
                        os.write(fob.fid, data)
                    else:
                        break
                os.close(fid)
                os.remove(f)
