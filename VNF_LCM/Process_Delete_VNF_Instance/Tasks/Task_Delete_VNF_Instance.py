from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    vnfLcm = VnfLcmSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
    
    auth_mode = context["vnfm_mano_auth_mode"]
    if auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'], auth_mode, context['vnfm_mano_keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
        
    vnf_instance_id = context["vnf_instance_id"]
    
    #Ensure the vnf_instance_id exists from the context.
    if not vnf_instance_id:
        MSA_API.task_error('The VNF instance id to be deleted is empty from the workflow instance context.', context, True)
        
    r = vnfLcm.vnf_lcm_delete_instance_of_vnf(vnf_instance_id)
    
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
    
    ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
    print(ret)