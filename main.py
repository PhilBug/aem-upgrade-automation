from git import Repo, cmd

import subprocess as sp
import os
import yaml
import bs4 as bs
import requests

'''Constants'''
SUCCESS = 0
FAILURE = 1

toolkit_path = f"{os.getcwd()}CQ-Unix-Toolkit"
'''CQ-Unix-Toolkit shortcuts'''
cqls = f"{toolkit_path}/cqls"


# TODO: add logger
# think whether installation logic should be inside CQInstance or CQPackage class

with open('config.yaml') as config_data:
    config = yaml.full_load(config_data)

if os.path.exists(toolkit_path):
    # print("CQ-Unix-Toolkit directory already exists. Running 'git pull'")
    try:
        cmd.Git(toolkit_path).pull()
    except Exception as e:
        print(f"Failed to run 'git pull': {str(e)}")
else:
    print('cloning...')
    Repo.clone_from(config['toolkit_url'], toolkit_path)

class CQInstance:
    def __init__(self, protocol, ip, port, user='admin', password='admin'):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.url = f"{protocol}://{ip}:{port}"
        self.user = user
        self.password = password
        self.package_dict = {}
        self.refferer = f"{self.url}/crx/packmgr"

    def auth(self):
        '''Return default auth format for requests'''
        return self.user, self.password

    # def package_list_gen_cqls(self):
    #     '''Lists all of the packages installed on the instance using cqls'''
    #     package_list = sp.Popen([cqls, '-i', self.url],
    #             stdout=sp.PIPE,
    #             stderr=sp.STDOUT)
    #     self.package_list = package_list.communicate()
    
    def package_dict_gen(self):
        '''Creates a dictionary of all of the packages installed on the instance and its versions'''
        headers = {'Referrer': self.refferer}
        form_data = {'cmd': (None, 'ls')}
        response = requests.post(f"{self.url}/crx/packmgr/service.jsp",
                headers=headers,
                files=form_data,
                auth=self.auth())

        package_list = [i.text for i in bs.BeautifulSoup(response.text, 'xml').find_all(['name', 'version'])]
        for i in range(0, len(package_list), 2):
            self.package_dict[package_list[i]] = package_list[i+1]

    def package_upload(self, file_path):
        '''Uploads package to a server, doesn't install it, returns xml in response'''
        # TODO: should be using package as an argument?
        headers = {
            'Referrer': self.refferer
        }
        form_data = {
            'file' : (file_path, open(file_path, 'rb'), 'appliation/zip', {}),
            'name': os.path.basename(file_path).rstrip('.zip'),
            'install': 'false'
        }
        response = requests.post(f"{self.url}/crx/packmgr/service.jsp",
                headers=headers,
                files=form_data,
                auth=self.auth())
        return response.text
    
    def package_install(self, cq_package):
        '''Installs an existing package'''
        headers = { 'Referrer': self.refferer }
        form_data = { 'cmd': (None, 'install') }
        response = requests.post(
                f"{self.url}/crx/packmgr/service/script.html{cq_package.path}",
                files=form_data,
                auth=self.auth())

        if "no package" in response.text:
            print(f"Package: {cq_package.name}, version: {cq_package.version} not found")
            return FAILURE
        else:
            print(f"Package: {cq_package.name}, version: {cq_package.version} installed")
            return SUCCESS
    
    def package_rebuild(self, cq_package):
        '''Rebuild an existing package in CQ'''
        headers = { 'Referrer': self.refferer }
        form_data = { 'cmd': (None, 'build') }
        response = requests.post(
                f"{self.url}/crx/packmgr/service/script.html{cq_package.path}",
                files=form_data,
                auth=self.auth())
        
        if "no package" in response.text:
            print(f"Package: {cq_package.name}, version: {cq_package.version} not found")
            return FAILURE
        else:
            print(f"Package: {cq_package.name}, version: {cq_package.version} installed")
            return SUCCESS

    def package_download(self, cq_package):
        '''Download package from server'''
        # TODO: add destination dir as parameter, version as part of downloaded file name

        if os.path.isfile(f"{cq_package.name}.zip"):
            print(f"File already exists, please remove it from the {os.getcwd()} directory.")
            return
        
        response = requests.get(self.url + cq_package.path, auth=self.auth())

        with open(f"{cq_package.name}.zip", 'wb') as f:
            if response.status_code == 200:
                f.write(response.content)
                return SUCCESS
            else:
                print(f"Download of a package: {cq_package.name} failed with an error code {response.status_code}")
                return FAILURE

    def package_uninstall(self, cq_package):
        '''Uninstall package from server'''
        headers = {
            'Referrer': self.refferer
        }
        form_data = {
            'cmd': (None, 'rm'),
            'name': (None, cq_package.name)
        }
        response = requests.post(f"{self.url}/crx/packmgr/service.jsp",
                headers=headers,
                files=form_data,
                auth=self.auth())
        print(response.status_code, response.text)

class CQPackage:
    def __init__(self, name, version, group):
        self.name = name
        self.version = version
        self.group = group
        self.path = f"/etc/packages/{group}/{name}-{version}.zip"

if __name__ == "__main__":
    instances = config['instances']
    author_instance = CQInstance(instances['protocol'], instances['author']['ip'], instances['author']['port'])
    publish_instance = CQInstance(instances['protocol'], instances['publish']['ip'], instances['publish']['port'])

    author_instance.package_dict_gen()

    bridge_hotfix_PES_285 = CQPackage('bridge-hotfix-PES-285', '1.0.1', 'com.cognifide.zg')

    author_instance.package_upload('./bridge-hotfix-PES-285-1.0.1.zip')
    author_instance.package_rebuild(bridge_hotfix_PES_285)

    bridge_core = CQPackage('bridge-core', '6.5.0.0', 'com.cognifide.bridge')

    #publish_instance.package_download(bridge_core)
    #publish_instance.package_uninstall(bridge_core)