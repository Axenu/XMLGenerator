import os, re, sys
import hashlib
import uuid
import json
import copy
from collections import OrderedDict
import fileinput

from xmlStructure import xmlElement, xmlAttribute, fileInfo, fileObject, dlog, textElement

class xmlGenerator(object):

    def __init__(self, input_data):
        self.filesToCreate = input_data['filesToCreate']
        self.json_data = input_data['data']
        self.extensions = []

    def addExtension(self, extension):
        self.extensions.append(extension)

    def resolveVar(self, var_name, local_data={}):
        parts = var_name.split('.')
        if len(parts) == 1:
            if parts[0] in self.json_data:
                return self.json_data[parts[0]]
            else:
                print 'MISSIN var: ' + var_name + ' in json_data'
                return ''
        else:
            if len(parts) > 0 and parts[0] in local_data:
                temp = local_data[parts[0]]
                if parts[1] in temp:
                    return temp[parts[1]]
                else:
                    print 'MISSIN var: ' + var_name + ' in json_data'
                    return ''
            else:
                print 'MISSIN var: ' + var_name + ' in json_data'
                return ''

    def resolveContent(self, content, local_data={}):
        text = ''
        for textType in content:
            if 'type' in textType:
                if textType['type'] == 'var':
                    # resolve var
                    text += self.resolveVar(textType['data'], local_data)
                else:
                    #append text
                    text += textType['data']
            else:
                #append text
                text += textType['data']
        return text

    def createXMLElement(self, template, namespace='', local_data={}):
        if 'name' not in template:
            if 'content' in template:
                text = self.resolveContent(template['content'], local_data)
                if text != '':
                    return textElement(text)
                else:
                    return None
            elif 'extension' in template:
                extension_name = template['extension']
                for extension in self.extensions:
                    if extension.selector == extension_name:
                        print 'found Extension'
                return
            else:
                print 'FATAL ERROR: missing name on xml Element'
                return None
        if 'namespace' in template:
            namespace = template['namespace']
        newElement = xmlElement(template['name'], namespace)
        if 'attributes' in template:
            #parse attribute
            for attribute in template['attributes']:
                if 'name' not in attribute:
                    print 'FATAL ERROR: missing name on xml attribute'
                    return None
                newAttr = xmlAttribute(attribute['name'])
                # solve text content
                if 'content' in attribute:
                    newAttr.value = self.resolveContent(attribute['content'], local_data)
                    newElement.addAttribute(newAttr)
        if 'children' in template:
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
                            el = self.createXMLElement(child, namespace, local)
                            if el != None:
                                newElement.addChild(el)
                            i += 1
                    else:
                        print 'FATAL ERROR: array not found'
                else:
                    el = self.createXMLElement(child, namespace, local_data)
                    if el != None:
                        newElement.addChild(el)


        return newElement




    def createXML(self):
        """
        The task method for executing the xmlGenerator and completing the xml files
        This is also the TASK to be run in the background.
        """
        for key, value in self.filesToCreate.iteritems():
            json_template_file=open(value).read()
            try:
                data = json.loads(json_template_file)#, object_pairs_hook=OrderedDict)
            except ValueError as err:
                print err # implement logger
                return  False
            name, rootE = data.items()[0] # root element
            # xmlFile = os.open(key,os.O_RDWR|os.O_CREAT)
            # fob = fileObject(key, value, xmlFile)
            # sortedFiles.append(fob)
            print rootE
            rootEl = self.createXMLElement(data)
            rootEl.printXML()
        # rootEl.printDebug()
        # fob.rootElement = rootEl

    # parseFiles(inputData['folderToParse'])
    #
    # # add the tmp files to the bottom of the appropriate file and write out the next section of xml until it's done
    # for fob in sortedFiles:
    #     for fin in fob.files:
    #         f = os.open(fin.filename, os.O_RDONLY)
    #         while True:
    #             data = os.read(f, 65536)
    #             if data:
    #                 os.write(fob.fid, data)
    #             else:
    #                 break
    #         # print more XML
    #         fob.rootElement.printXML(fob.fid)
    #         os.close(f)
    #         os.remove(fin.filename)

class xmlExtensionModule(object):

    def __init__(self):
        self.selector = ''

class xmlFilesExtenstionModule(xmlExtensionModule):

    def __init__(self):
        self.selector = 'ContainsFilesExtension'

    # def handle


# Example of inputData:

inputData = {
    "data": {
        "var1": "Demo var",
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
c.createXML()
