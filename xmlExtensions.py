import uuid, os, hashlib

from xmlStructure import xmlExtensionModule


class xmlFilesExtenstionModule(xmlExtensionModule):

    def __init__(self):
        self.selector = 'ContainsFilesExtension'
        self.requiresOneRunOnly = True
        self.folder = '/SIP'

    def executeExtensionOnce(self, xmlGenerator, states, json_data):

        fileInfo = {}
        numberOfFiles = 0
        totalSize = 0
        for dirname, dirnames, filenames in os.walk(self.folder):
            # print dirname
            # print dirnames
            # print filenames
            for file in filenames:
                numberOfFiles += 1
                fileInfo['name'] = dirname+'/'+file
                fileInfo['checksum'] = self.calculateChecksum(dirname+'/'+file)
                fileInfo['uuid'] = uuid.uuid4().__str__()
                fileInfo['mimetype'] = 'application/msword'
                fileInfo['created'] = '2016-02-21T11:18:44+01:00'
                fileInfo['formatName'] = 'MS word'
                size = os.path.getsize(dirname+'/'+file)
                totalSize += size
                fileInfo['size'] = str(size)
                fileInfo['use'] = 'DataFile'
                fileInfo['checksumType'] = 'SHA-256'
                fileInfo['locType'] = 'URL'
                fileInfo['linkType'] = 'simple'
                fileInfo['checksumLib'] = 'hashlib'
                fileInfo['locationType'] = 'URI'
                fileInfo['idType'] = 'UUID'
                # temp = {"name":"kite.pdf"}
                # temp["uuid"] = uuid.uuid4().__str__()

                for state in states:
                    state.local_data['file'] = fileInfo
                    xmlGenerator.currentFileID = state.fid
                    if 'children' in state.template:
                        for child in state.template['children']:
                            xmlGenerator.createXMLElement(child, state.level, state.namespace, state.local_data)
        print 'xmlFIlesExtension parsed ' + str(numberOfFiles)
        print 'xmlFIlesExtension parsed ' + str(totalSize) + ' bytes'
        return

    def calculateChecksum(self, filename):
        """
        calculate the checksum for the selected file, one chunk at a time
        """
        fd = os.open(filename, os.O_RDONLY)
        hashSHA = hashlib.sha256()
        while True:
            data = os.read(fd, 65536)
            if data:
                hashSHA.update(data)
            else:
                break
        os.close(fd)
        return hashSHA.hexdigest()


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
