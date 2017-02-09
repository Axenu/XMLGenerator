from xmlGenerator import *

# Example of inputData:

inputData = {
    "data": {
        "var1": "Demo var",
        "var2": "Demo var2",
        "xmlns": {
            "mets":"http://www.loc.gov/METS/",
            "xlink":"http://www.w3.org/1999/xlink",
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "schemaLocation":"http://www.loc.gov/METS/ http://xml.essarch.org/METS/info.xsd"
        },
        "mets":{
            "ID":"55f04f06-21d6-4c15-ba5b-92fad56c8ba2",
            "objid":"55f04f06-21d6-4c15-ba5b-92fad56c8ba2",
            "label":"mets_label",
            "type":"mets_type",
            "profile":"mets_profile"
        },
        "agents":[
            {
                "role":"IPOWNER",
                "type":"ORGANIZATION",
                "name":"the ip owner",
                "note":"the ip owner note"
            }
        ],
        "archivist_organization_name":"Sydarkivera",
        # "archivist_organization_note":"Sydarkivera note",
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
    "filesToCreate": [
        {
            "xmlFileName":"sip.txt",
            "templateFileName":"templates/test1.json"
        }
        ,{
            "xmlFileName":"sip2.txt",
            "templateFileName":"templates/test2.json"
        }
    ],
    "folderToParse":"/SIP/"
}

# createXML(inputData)
c = xmlGenerator(inputData)
c.addExtension(xmlFilesExtenstionModule())
c.addExtension(inlineExtenstionModule())
c.createXML()
