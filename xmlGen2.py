import os, re, sys
import hashlib
import uuid
import json
import copy
from collections import OrderedDict
import fileinput

from xmlStructure import xmlElement, xmlAttribute, fileInfo, fileObject, dlog, textElement


def resolveVar(var_name):

    return 'var'

def resolveContent(content):
    text = ''
    for textType in content:
        if 'type' in textType:
            if textType['type'] == 'var':
                # resolve var
                text += resolveVar(textType['data'])
            else:
                #append text
                text += textType['data']
        else:
            #append text
            text += textType['data']
    return text

def createXMLElement(template, json_data, namespace=''):
    if 'name' not in template:
        if 'content' in template:
            return textElement(resolveContent(template['content']))
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
                newAttr.value = resolveContent(attribute['content'])
                newElement.addAttribute(newAttr)
    if 'children' in template:
        for child in template['children']:
            el = createXMLElement(child, json_data, namespace)
            if el != None:
                newElement.addChild(el)


    return newElement




def createXML(inputData):
    """
    The task method for executing the xmlGenerator and completing the xml files
    This is also the TASK to be run in the background.
    """
    for key, value in inputData['filesToCreate'].iteritems():
        json_data=open(value).read()
        try:
            data = json.loads(json_data)#, object_pairs_hook=OrderedDict)
        except ValueError as err:
            print err # implement logger
            return  False
        name, rootE = data.items()[0] # root element
        # xmlFile = os.open(key,os.O_RDWR|os.O_CREAT)
        # fob = fileObject(key, value, xmlFile)
        # sortedFiles.append(fob)
        print rootE
        rootEl = createXMLElement(data, inputData['data'])
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

# Example of inputData:

inputData = {
    "data": {
    },
    "filesToCreate": {
        "sip.txt":"templates/test1.json"
    },
    "folderToParse":"/SIP/"
}

createXML(inputData)
