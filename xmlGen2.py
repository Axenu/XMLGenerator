import os, re, sys
import hashlib
import uuid
import json
import copy
from collections import OrderedDict
import fileinput

from xmlStructure import xmlElement, xmlAttribute, fileInfo, fileObject, dlog, textElement


def resolveVar(var_name, json_data, local_data={}):
    parts = var_name.split('.')
    if len(parts) == 1:
        if parts[0] in json_data:
            return json_data[parts[0]]
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

def resolveContent(content, json_data, local_data):
    text = ''
    for textType in content:
        if 'type' in textType:
            if textType['type'] == 'var':
                # resolve var
                text += resolveVar(textType['data'], json_data, local_data)
            else:
                #append text
                text += textType['data']
        else:
            #append text
            text += textType['data']
    return text

def createXMLElement(template, json_data, namespace='', local_data={}):
    if 'name' not in template:
        if 'content' in template:
            text = resolveContent(template['content'], json_data, local_data)
            if text != '':
                return textElement(text)
            else:
                return None
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
                newAttr.value = resolveContent(attribute['content'], json_data, local_data)
                newElement.addAttribute(newAttr)
    if 'children' in template:
        for child in template['children']:
            if 'repeat' in child:
                repeat = child['repeat'].split(' ')
                var_name = repeat[1]
                array_name = repeat[3]
                array = resolveVar(array_name, json_data)
                if isinstance(array, list):
                    i = 0
                    for o in array:
                        temp = dict(o)
                        temp['_index'] = i
                        local = dict(local_data)
                        if var_name not in local:
                            local[var_name] = temp
                        else:
                            print 'FATAL ERROR: Duplicate varname in nested loops'
                        el = createXMLElement(child, json_data, namespace, local)
                        if el != None:
                            newElement.addChild(el)
                        i += 1
                else:
                    print 'FATAL ERROR: array not found'
            else:
                el = createXMLElement(child, json_data, namespace, local_data)
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

createXML(inputData)
