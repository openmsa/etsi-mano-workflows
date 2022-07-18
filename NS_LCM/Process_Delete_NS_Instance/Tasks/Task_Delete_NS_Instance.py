from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.NsLcmSol005 import NsLcmSol005


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    nsLcm = NsLcmSol005(context["mano_ip"], context["mano_port"])
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        nsLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        nsLcm.set_parameters(context['mano_user'], context['mano_pass'])
    
    ns_instance_id = context["ns_instance_id"]
    
    r = nsLcm.ns_lcm_delete_instance_of_ns(ns_instance_id)
    
    ret = MSA_API.process_content(nsLcm.state, f'{r}', context, True)
    print(ret)