import yaml

from package import AEMPackage

with open('config.yaml') as config_data:
    config = yaml.full_load(config_data)

class GroovyScript:
    def __init__(self):
        pass

    def install_groovy_console(self, console_url):
        pass
        #groovy_console = AEMPackage.ini