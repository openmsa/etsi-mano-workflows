from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003

def __init_context():
    dev_var = Variables()
    dev_var.add('vnfm_managed_entity', var_type='Device')
    dev_var.add('vnf_instance_id', var_type='OBMFRef')
    context = Variables.task_call(dev_var)
    
    return context

def __get_kubeconfig_by(vnf_instance_id):
    #TODO - fetch kubeconfig from juju server by the vnf_insatnce_id.
    kubeconfig = ''
    #Save kubeconfig in the context.
    context['vnf_instance_k8s_cluster_kubeconfig'] = kubeconfig

def __init_vnflcm(context):
    vnfLcm = VnfLcmSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
    
    auth_mode = context["vnfm_mano_auth_mode"]
    if auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'], auth_mode, context['vnfm_mano_keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
    
    return vnfLcm

def __vnf_lcm_get_vnf_instance_details(context):
    vnf_instance_id = context.get('vnf_instance_id')
    return vnfLcm.vnf_lcm_get_vnf_instance_details(vnf_instance_id)

def __check_request_status_of(vnf_instance_get_details):
    r_details = ''
    status = vnfLcm.state
    
    if status != 'ENDED':
        r_details = str(vnf_instance_get_details.json().get('detail'))
        MSA_API.task_error('Failed to get VNF Instance details: \n"' + r_details + '"', context, True)
    

if __name__ == "__main__":
    
    #Init context variables.
    context = __init_context()

    #Init VNFlCM object.
    vnfLcm = __init_vnflcm(context)
    
    #Get VNF Instance details by id.
    #vnf_instance = __vnf_lcm_get_vnf_instance_details(context)

    MSA_API.task_success('Task OK', context, True)

