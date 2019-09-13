import yaml

from package import AEMPackage
from package_executor import PackageExecutor
from aem import AEMInstance
from groovy_script import GroovyScript

with open('config.yaml') as config_data:
    config = yaml.full_load(config_data)

def main():
    instances = config['instances']
    groovy = config['groovy']

    author = AEMInstance(instances['protocol'], instances['author']['ip'], instances['author']['port'])
    pe_auth = PackageExecutor(author)

    bridge_hotfix_PES_285 = AEMPackage('./packages/bridge-hotfix-PES-285-1.0.1.zip')
    groovy_console = AEMPackage('./packages/aem-groovy-console-13.0.0.zip')

    pe_auth.upload(bridge_hotfix_PES_285)
    bridge_hotfix_PES_285.print_info()
    pe_auth.install(bridge_hotfix_PES_285)
    pe_auth.upload(groovy_console)
    groovy_console.print_info()
    pe_auth.install(groovy_console)

    r = pe_auth.find(bridge_hotfix_PES_285)
    print(r)
    pe_auth.uninstall(bridge_hotfix_PES_285)
    r = pe_auth.find(bridge_hotfix_PES_285)
    print(r)

main()