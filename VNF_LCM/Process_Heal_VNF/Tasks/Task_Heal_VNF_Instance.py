import json
from msa_sdk import constants
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003

dev_var = Variables()
dev_var.add('cause', var_type='String')
#dev_var.add('additionalParams', var_type='String')
context = Variables.task_call(dev_var)

if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    vnfLcm = VnfLcmSol003(context["mano_ip"], context["mano_port"], context['mano_base_url'])
    
    auth_mode = context["auth_mode"]
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'])
    
    cause = context.get('cause')
    additionalParams = {}
    content = {
               "cause": cause,
               "additionalParams": additionalParams,
               }
    
    r = vnfLcm.vnf_lcm_heal_instance_vnf(context["vnf_instance_id"], content)
    
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        location = ''
        try:
            location = r.headers['Location']
        except:
            MSA_API.task_error('Heal VNF is failed.', context)
            
        context["vnf_lcm_op_occ_id"] = location.split("/")[-1]
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        state = 'FAILED'
    
    ret = MSA_API.process_content(vnfLcm.state, f'{r}' + ': ' + r_details, context, True) 
    print(ret)