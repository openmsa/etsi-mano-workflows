import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.NsdSol005 import NsdSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('ns_package_id', var_type='String')
    context = Variables.task_call(dev_var)

    #Get SOL00X version from context.
    sol_version = context.get('sol005_version')

    nsdApi = NsdSol005(context["mano_ip"], context["mano_port"], context["mano_base_url"], sol_version)    
        
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        nsdApi.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        nsdApi.set_parameters(auth_mode, context['mano_user'], context['mano_pass'])
    
    r = nsdApi.ns_descriptors_nsd_info_id_delete(context["ns_package_id"])

    r_details = ''
    status = nsdApi.state
    if status == 'ENDED':
        r_details = 'Successful!'
        context.update(ns_package_id='')
    else:
        r_details = str(r.json().get('detail'))
        
    ret = MSA_API.process_content(nsdApi.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)
