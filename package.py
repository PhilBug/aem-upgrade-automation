import requests
import os
import xmltodict
import zipfile

'''Constants'''
SUCCESS = 0
FAILURE = 1

class AEMPackage:
    def __init__(self, file_path):
        self.name = None
        self.version = None
        self.group = None
        self.url_path = None
        self.file_path = file_path

    def print_info(self):
        print("##########################################")
        print(f"Name: {self.name}\nVersion: {self.version}\nGroup: {self.group}\nPath: {self.url_path}")
        print("##########################################")

    def _get_path(self):
        if None in (self.group, self.name, self.version):
            raise ValueError('Cannot create path, group or version undefined.')
        self.url_path = f"/etc/packages/{self.group}/{self.name}-{self.version}.zip"


    def get_xml(self):
        zip_file = zipfile.ZipFile(self.file_path)
        with zipfile.ZipFile(self.file_path) as z:
            with z.open('META-INF/vault/properties.xml') as xml_file:
                decoded = xml_file.read().decode('UTF-8')
                return decoded

    def get_manifest_attr(self):
        xml_file = self.get_xml()
        xml_parsed = xmltodict.parse(xml_file)
        for line in xml_parsed['properties']['entry']:
            if line['@key'] == 'group':
                self.group = line['#text']
                continue
            elif line['@key'] == 'version':
                self.version = line['#text']
                continue
            elif line['@key'] == 'name':
                self.name = line['#text']
        if None in (self.version, self.group):
            print("Package properties.xml parsing error")
            exit(1)
        self._get_path()
