import requests
import xmltodict

class AEMInstance:
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
    
    def package_dict_gen(self):
        '''Creates a dictionary of all of the packages installed on the instance and its versions'''
        headers = {'Referrer': self.refferer}
        form_data = {'cmd': (None, 'ls')}
        response = requests.post(f"{self.url}/crx/packmgr/service.jsp",
                headers=headers,
                files=form_data,
                auth=self.auth())

        xml_response = xmltodict.parse(response.text)
        self.package_dict = xml_response['crx']['response']['data']['packages']['package']
