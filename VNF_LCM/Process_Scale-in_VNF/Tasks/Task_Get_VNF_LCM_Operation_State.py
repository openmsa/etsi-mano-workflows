from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants

from custom.ETSI.VnfLcmOpOccsSol003 import VnfLcmOpOccsSol003


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)
    
    if context.get('is_vnf_instance_exist') == True:
        MSA_API.task_success('Task execution is completed.', context)

    vnfLcmOpOccs = VnfLcmOpOccsSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
    
    auth_mode = context["vnfm_auth_mode"]
    if auth_mode == 'oauth_v2':
        vnfLcmOpOccs.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'], auth_mode, context['vnfm_mano_keycloak_server_url'])
    else:
        vnfLcmOpOccs.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
    
    vnf_lcm_op_occ_id = context.get('vnf_lcm_op_occ_id')
    
    r = {}
    if 'vnf_lcm_op_occ_id' in context and vnf_lcm_op_occ_id:
        r = vnfLcmOpOccs.vnf_lcm_op_occs_completion_wait(vnf_lcm_op_occ_id)
        
    r_details = ''
    status = vnfLcmOpOccs.state
    if status == 'ENDED':
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
        
    ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
    print(ret)
