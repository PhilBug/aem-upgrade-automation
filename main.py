from git import Repo, cmd

import subprocess as sp
import os
import yaml
import bs4 as bs
import requests

toolkit_path = f"{os.getcwd()}CQ-Unix-Toolkit"
'''CQ-Unix-Toolkit shortcuts'''
cqls = f"{toolkit_path}/cqls"

with open('config.yaml') as config_data:
    config = yaml.full_load(config_data)

if os.path.exists(toolkit_path):
    print("CQ-Unix-Toolkit directory already exists. Running 'git pull'")
    try:
        cmd.Git(toolkit_path).pull()
    except Exception as e:
        print(f"Failed to run 'git pull': {str(e)}")
else:
    print('cloning...')
    Repo.clone_from(config['toolkit_url'], toolkit_path)

class CQInstance:
    def __init__(self, protocol, ip, port):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.url = f"{protocol}://{ip}:{port}"
        self.package_list = ['Run gen_package_list() to generate the list']

    def gen_package_list_with_cqls(self):
        '''Lists all of the packages installed on the instance using cqls'''
        package_list = sp.Popen([cqls, '-i', self.url],
                stdout=sp.PIPE,
                stderr=sp.STDOUT)
        self.package_list = package_list.communicate()
    
    def gen_package_list(self):
        '''Lists all of the packages installed on the instance'''
        headers = {
            'Referrer': 'http://192.168.2.254:4503/crx/packmgr'
        }
        files = {
            'cmd': (None, 'ls')
        }
        response = requests.post('http://192.168.2.254:4503/crx/packmgr/service.jsp',
                headers=headers,
                files=files,
                auth=('admin', 'admin'))
        self.package_list = [name.string for name in bs.BeautifulSoup(response.text, 'xml').find_all('name')]

class CQPackage:
    def __init__(self, name, version, path):
        self.name = name
        self.version = version
        self.path = path


if __name__ == "__main__":
    instances = config['instances']
    author_instance = CQInstance(instances['protocol'], instances['author']['ip'], instances['author']['port'])
    publish_instance = CQInstance(instances['protocol'], instances['author']['ip'], instances['author']['port'])

    author_instance.gen_package_list()
    for package in author_instance.package_list:
        print(package)