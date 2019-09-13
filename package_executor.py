from interfaces import IExecutable
import package
import requests
import os

'''Constants'''
SUCCESS = 0
FAILURE = 1

class PackageExecutor(IExecutable):
    def __init__(self, aem_instance):
        self.aem_instance = aem_instance

    def find(self, package):
        '''Look for a package info xml on the instance, generate the package dictionary if it doesnt already exist'''
        if not self.aem_instance.package_dict:
            self.aem_instance.package_dict_gen()
        for p in self.aem_instance.package_dict:
            if p['name'] == package.name:
                return p

    def install(self, package):
        #TODO add retry mechanism
        '''Install an existing package'''
        headers = { 'Referrer': self.aem_instance.refferer} 
        form_data = { 'cmd': (None, 'install') }
        if 'unset' in (package.group, package.version):
            print(f"Cannot install {package.name} package. Group: {package.group} ver: {package.version}")
            return FAILURE

        response = requests.post(
                f"{self.aem_instance.url}/crx/packmgr/service/script.html{package.url_path}",
                files=form_data,
                auth=self.aem_instance.auth())

        if "no package" in response.text:
            print(f"Package: {package.name}, version: {package.version} not found")
            return FAILURE
        else:
            print(f"Package: {package.name}, version: {package.version} installed")
            return SUCCESS

    def upload(self, package):
        '''Read version and group info, upload package to a server, doesn't install it, return xml in response'''
        # TODO: should be using package as an argument?
        package.get_manifest_attr()

        headers = { 'Referrer': self.aem_instance.refferer }
        form_data = {
            'file' : (package.file_path, open(package.file_path, 'rb'), 'appliation/zip', {}),
            'name': os.path.basename(package.file_path).rstrip('.zip'),
            'install': 'false'
        }
        response = requests.post(f"{self.aem_instance.url}/crx/packmgr/service.jsp",
                headers=headers,
                files=form_data,
                auth=self.aem_instance.auth())
        return response.text

    def execute(self, package):
        return package.install(self.aem_instance)

    def uninstall(self, package):
        '''Uninstall package from server'''
        headers = {
            'Referrer': self.aem_instance.refferer
        }
        form_data = {
            'cmd': (None, 'rm'),
            'name': (None, package.name)
        }
        response = requests.post(f"{self.aem_instance.url}/crx/packmgr/service.jsp",
                headers=headers,
                files=form_data,
                auth=self.aem_instance.auth())
        print(response.status_code, response.text)

    def download(self, package):
        '''Download package from server'''
        # TODO: add destination dir as parameter, version as part of downloaded file name

        if os.path.isfile(f"{package.name}.zip"):
            print(f"File already exists, please remove it from the {os.getcwd()} directory.")
            return
        
        response = requests.get(self.aem_instance.url + self.aem_instance.path, auth=self.aem_instance.auth())

        with open(f"{package.name}.zip", 'wb') as f:
            if response.status_code == 200:
                f.write(response.content)
                return SUCCESS
            else:
                print(f"Download of a package: {package.name} failed with an error code {response.status_code}")
                return FAILURE

    def rebuild(self, package):
        '''Rebuild an existing package in CQ'''
        headers = { 'Referrer': self.aem_instance.refferer }
        form_data = { 'cmd': (None, 'build') }
        response = requests.post(
                f"{self.aem_instance.url}/crx/packmgr/service/script.html{package.url_path}",
                files=form_data,
                auth=self.aem_instance.auth())
        
        if "no package" in response.text:
            print(f"Package: {package.name}, version: {package.version} not found")
            return FAILURE
        else:
            print(f"Package: {package.name}, version: {package.version} installed")
            return SUCCESS
