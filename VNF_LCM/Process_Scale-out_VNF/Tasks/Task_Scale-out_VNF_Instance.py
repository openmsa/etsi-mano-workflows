import json
from msa_sdk import constants
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('aspectId', var_type='String')
    dev_var.add('numberOfSteps', var_type='String')
    context = Variables.task_call(dev_var)

    vnfLcm = VnfLcmSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
    
    auth_mode = context["vnfm_mano_auth_mode"]
    if auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'], auth_mode, context['vnfm_mano_keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
    
    aspectId = context.get('aspectId')
    if not aspectId:
        aspectId = 'aspect'
    
    numberOfSteps = context.get('numberOfSteps')
    if not numberOfSteps:
        numberOfSteps = '1'
    
    content = {
               "type": "SCALE_OUT",
               "aspectId": aspectId,
               "numberOfSteps": numberOfSteps,
               "additionalParams": {}
               }
    
    r = vnfLcm.vnf_lcm_scale_instance_vnf(context["vnf_instance_id"], content)
    
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        location = ''
        try:
            location = r.headers['Location']
        except:
            MSA_API.task_error('Scale-out VNF is failed.', context)
            
        context["vnf_lcm_op_occ_id"] = location.split("/")[-1]
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
    
    ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
    print(ret)