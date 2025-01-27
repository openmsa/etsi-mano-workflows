import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vnf_pkg_id')
    dev_var.add('vnf_instance_name')
    dev_var.add('vnf_instance_description')
    dev_var.add('vnf_instantiation_payload')
    dev_var.add('is_vnf_instance_exist')
    dev_var.add('vnf_instance_id')
    dev_var.add('ns_service_instance_ref')
    context = Variables.task_call(dev_var)
    
    #Get VNFM config variables values from context.
    vnfm_mano_auth_mode = context["vnfm_mano_auth_mode"]
    vnfm_mano_base_url = context["vnfm_mano_base_url"]
    vnfm_mano_ip = context["vnfm_mano_ip"]
    vnfm_mano_port = context["vnfm_mano_port"]
    vnfm_mano_user = context["vnfm_mano_user"]
    vnfm_mano_pass = context["vnfm_mano_pass"]
    
    #Create VNF Instance resources.
    vnfLcm = VnfLcmSol003(vnfm_mano_ip, vnfm_mano_port, vnfm_mano_base_url)
    
    #Create VNF LCM service instance of an existing VNF Instance.
    if context.get('is_vnf_instance_exist') == True:
        vnf_instance_id = context.get('vnf_instance_id')
        
        MSA_API.task_success('VNF LCM service instance is created for VNF instance id: {vnf_instance_id}.', context)
    
    if vnfm_mano_auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_server_url = context["vnfm_mano_keycloak_server_url"]
        
        vnfLcm.set_parameters(vnfm_mano_user, vnfm_mano_pass, vnfm_mano_auth_mode, keycloak_server_url)
    else:
        vnfLcm.set_parameters(vnfm_mano_user, vnfm_mano_pass)
    
    #--------------------- 3rd party S-VFNM ---------------
    metadata = {"onboardedVnfPkgInfoId": context["vnf_pkg_id"]}
    
    #Get VNF Descriptor id from the context.    
    vnfd_id = context["vnfd_id"]
        
    #Prepare the VNF Instance Resources creation request payload.
    payload = {"vnfdId": vnfd_id,
               "vnfInstanceName": context["vnf_instance_name"],
               "vnfInstanceDescription": context['vnf_instance_description'],
               "metadata": metadata
               }
    
    #Execute the VNF LCM operation to create VNF instance resources to the VNFM.
    r = vnfLcm.vnf_lcm_create_instance(payload)
    
    #Check the operation status and get the response details.
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        lcm_data = r.json()
        context["vnf_instance_id"] = lcm_data['id']
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
        
    ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
    print(ret)