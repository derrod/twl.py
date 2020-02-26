import xml.dom.minidom


class HashV1:
    def __init__(self, xml_obj):
        hex_hash = xml_obj.getAttribute('data')
        algorithm = xml_obj.getAttribute('alg')
        if algorithm == 'SHA-256':
            algorithm = 'sha256'
            if len(hex_hash) < 64:
                hex_hash = "0" * (64 - len(hex_hash)) + hex_hash
        self.algorithm = algorithm
        self.value = hex_hash


class FileV1:
    def __init__(self, xml_obj):
        file_info = xml_obj.getElementsByTagName('local')[0]
        self.path = file_info.getAttribute('path')
        self.filename = file_info.getAttribute('name')
        self.size = int(xml_obj.getElementsByTagName('content')[0].getAttribute('length'))
        self.hash = HashV1(xml_obj.getElementsByTagName('verification')[0])
        self.urls = [s.getAttribute('url') for s in xml_obj.getElementsByTagName('signed-url')]


class ManifestV1:
    """
    Version 1 Manifest
    """

    def __init__(self):
        self._xml = None
        self.files = []

    def read(self, content):
        self._xml = content
        domtree = xml.dom.minidom.parseString(self._xml)
        root = domtree.documentElement
        files = root.getElementsByTagName("file")
        self.files = [FileV1(xml_obj) for xml_obj in files]

    @classmethod
    def create(cls, content):
        c = cls()
        c.read(content)
        return c
