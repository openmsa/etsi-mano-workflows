from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfPkgSol005 import VnfPkgSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vnf_package_id', var_type='String')
    dev_var.add('vnf_descriptor', var_type='String')
    context = Variables.task_call(dev_var)

    vnfPkgApi = VnfPkgSol005(context["mano_ip"], context["mano_port"])
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfPkgApi.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfPkgApi.set_parameters(auth_mode, context['mano_user'], context['mano_pass'])
        
    r = vnfPkgApi.vnf_packages_vnfpkgid_package_file_put(context['vnf_package_id'],
                                                         context['vnf_descriptor'])

    ret = MSA_API.process_content(vnfPkgApi.state, f'{r}', context, True)
    print(ret)