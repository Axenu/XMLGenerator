import os, re, sys
import hashlib
import uuid
import json
import copy
from collections import OrderedDict
import fileinput

from xmlStructure import xmlElement, xmlAttribute, fileObject, dlog, textElement, savedState

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
        self.sortedFiles = []
        self.numberOfFiles = 0
        self.currentFileID = None
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
        else:
            if len(parts) > 0 and parts[0] in local_data:
                temp = local_data[parts[0]]
                if parts[1] in temp:
                    return temp[parts[1]]
                else:
                    print 'MISSING var: ' + var_name + ' in json_data'
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

    def createXMLElement(self, template, level=0, namespace='', local_data={}):
        if 'extension' in template:
            extension_name = template['extension']
            foundExtension = False
            for extension in self.extensions:
                if extension.selector == extension_name:
                    foundExtension = True
                    # print 'found Extension'
                    if extension.requiresOneRunOnly:
                        # Save current state for later processing
                        # create new file to write further data to

                        #detail:
                        # 1. Save this state for final one run parsing
                        # save: local_data, template, level, namespace, fileID
                        state = savedState(local_data, template, level, namespace, self.currentFileID)
                        if extension.selector in self.remainingParts:
                            self.remainingParts[extension.selector].append(state)
                        else:
                            self.remainingParts[extension.selector] = [state]

                        # 2. Create new fid for further parsing
                        self.currentFileID = os.open('temp' + str(self.numberOfFiles) + '.txt',os.O_RDWR|os.O_CREAT)
                        fob = fileObject(template, self.currentFileID, 'temp' + str(self.numberOfFiles) + '.txt', local_data)
                        self.numberOfFiles += 1
                        self.sortedFiles.append(fob)

                    else:
                        # run now
                        if extension.executeExtension(template, level, namespace, local_data):
                            if 'children' in template:
                                for child in template['children']:
                                    self.createXMLElement(child, level, namespace, local_data)
                        pass
                    break
            if not foundExtension:
                print "ERROR: Extension \"" + extension_name + "\" is not loaded"
            return
        if 'name' not in template:
            if 'content' in template:
                text = self.resolveContent(template['content'], local_data)
                if text != '':
                    os.write(self.currentFileID, pretty_print_string(level) + text + '\n')
                    print pretty_print_string(level) + text
                return
            else:
                print 'FATAL ERROR: missing name on xml Element'
                return

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
                    return
                # solve text content
                if 'content' in attribute:
                    attributes += ' ' + attribute['name'] + '=\"' + self.resolveContent(attribute['content'], local_data) + '\"'
        if 'children' in template:
            os.write(self.currentFileID, pretty_print_string(level) + '<' + tagName + attributes + '>\n')
            print pretty_print_string(level) + '<' + tagName + attributes + '>'
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
                                return
                            self.createXMLElement(child, level+1, namespace, local)
                            i += 1
                    else:
                        print 'FATAL ERROR: array not found'
                        return
                else:
                    self.createXMLElement(child, level+1, namespace, local_data)
            os.write(self.currentFileID, pretty_print_string(level) + '</' + tagName + '>\n')
            print pretty_print_string(level) + '</' + tagName + '>'
        else:
            os.write(self.currentFileID, pretty_print_string(level) + '<' + tagName + attributes + '/>\n')
            print pretty_print_string(level) + '<' + tagName + attributes + '/>'




    def createXML(self):
        """
        The task method for executing the xmlGenerator and completing the xml files
        This is also the TASK to be run in the background.
        """
        for xmlFileName, jsonTemplateName in self.filesToCreate.iteritems():
            json_template_file=open(jsonTemplateName).read()
            try:
                template = json.loads(json_template_file)#, object_pairs_hook=OrderedDict)
            except ValueError as err:
                print err # implement logger
                return  False
            name, rootE = template.items()[0] # root element
            self.currentFileID = os.open(xmlFileName,os.O_RDWR|os.O_CREAT)
            fob = fileObject(template, self.currentFileID, xmlFileName)
            self.sortedFiles.append(fob)
            self.numberOfFiles = 1
            print rootE
            self.createXMLElement(template)
        # rootEl.printDebug()
        # fob.rootElement = rootEl

        for extensionName, states in self.remainingParts.iteritems():
            extention = None
            for ext in self.extensions:
                if ext.selector == extensionName:
                    extension = ext
                    break
            if extension != None:
                extension.executeExtensionOnce(self, states, self.json_data)

        outputFile = self.sortedFiles[0].fid
        for i in xrange(1, len(self.sortedFiles)):
            fob = self.sortedFiles[i]
            fid = os.open(fob.fileName, os.O_RDONLY)
            while True:
                data = os.read(fid, 65536)
                if data:
                    os.write(outputFile, data)
                else:
                    break
            os.close(fid)
            os.remove(fob.fileName)


    # parseFiles(inputData['folderToParse'])
    #
    # # add the tmp files to the bottom of the appropriate file and write out the next section of xml until it's done
    # for fob in sortedFiles:
    #     for fin in fob.files:
    #         f = os.open(fin.filename, os.O_RDONLY)
    #         while True:
    #             data = os.read(f, 65536)
                # if data:
                #     os.write(fob.fid, data)
                # else:
                #     break
    #         # print more XML
    #         fob.rootElement.printXML(fob.fid)
            # os.close(f)
            # os.remove(fin.filename)

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

class xmlFilesExtenstionModule(xmlExtensionModule):

    def __init__(self):
        self.selector = 'ContainsFilesExtension'
        self.requiresOneRunOnly = True

    def executeExtensionOnce(self, xmlGenerator, states, json_data):
        temp = {"name":"kite.pdf"}
        temp["uuid"] = uuid.uuid4().__str__()

        for state in states:
            state.local_data['file'] = temp
            xmlGenerator.currentFileID = state.fid
            if 'children' in state.template:
                for child in state.template['children']:
                    xmlGenerator.createXMLElement(child, state.level, state.namespace, state.local_data)
                    pass
        return


class inlineExtenstionModule(xmlExtensionModule):

    def __init__(self):
        self.selector = 'inlineExtension'
        self.requiresOneRunOnly = False

    def executeExtension(self, template, level, namespace, local_data):
        # create
        # print 'executeExtension'
        temp = {"name":"Beam.pdf"}
        temp["uuid"] = uuid.uuid4().__str__()
        if 'file' not in local_data:
            local_data['file'] = temp
        return True


# Example of inputData:

inputData = {
    "data": {
        "var1": "Demo var",
        "var2": "Demo var2",
        "array": [{
                "name": "Hello"
            }, {
                "name": "world"
            }],
        "array2": [{
                "name": "Hello2"
            }, {
                "name": "world2"
            }]
    },
    "filesToCreate": {
        "sip.txt":"templates/test1.json"
    },
    "folderToParse":"/SIP/"
}

# createXML(inputData)
c = xmlGenerator(inputData)
c.addExtension(xmlFilesExtenstionModule())
c.addExtension(inlineExtenstionModule())
c.createXML()
