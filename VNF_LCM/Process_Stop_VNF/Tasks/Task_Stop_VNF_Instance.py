import json
from msa_sdk import constants
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    vnfLcm = VnfLcmSol003(context["mano_ip"], context["mano_port"], context['mano_base_url'])
    
    auth_mode = context["auth_mode"]
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'])
    
    content = {
               "additionalParams": {},
               "changeStateTo": "STOPPED",
               "gracefulStopTimeout": 0,
               "stopType": "FORCEFUL"
               }
    
    r = vnfLcm.vnf_lcm_operate_instance_vnf(context["vnf_instance_id"], content)
    
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        location = ''
        try:
            location = r.headers['Location']
        except:
            MSA_API.task_error('Stop VNF is failed.', context)
            
        context["vnf_lcm_op_occ_id"] = location.split("/")[-1]
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        state = 'FAILED'
    
    ret = MSA_API.process_content(vnfLcm.state, f'{r}' + ': ' + r_details, context, True) 
    print(ret)