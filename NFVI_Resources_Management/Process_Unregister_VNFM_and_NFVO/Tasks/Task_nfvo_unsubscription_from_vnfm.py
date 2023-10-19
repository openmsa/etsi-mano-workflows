import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
dev_var.add('vnfm_device', var_type='Device')
dev_var.add('is_vnfm_register_only', var_type='Boolean')
dev_var.add("service_instance_name", var_type='String')
context = Variables.task_call(dev_var)

if __name__ == "__main__":
    
    #Get is_vnfm_register_only value.
    is_vnfm_register_only = context.get('is_vnfm_register_only')
    
    #MSA_API.task_success(is_vnfm_register_only, context)
    
    if is_vnfm_register_only == False or is_vnfm_register_only == 'False' or is_vnfm_register_only == 'false':
        #Get VNFM ME connection informations.
        vnfm_me_ref = context["vnfm_device"]
        vnfm_me_id = context["vnfm_device"][3:]
        vnfm_ip    = context["vnfm_mano_ip"]
        vnfm_port  = context["vnfm_mano_port"]
        vnfm_username  = context["vnfm_mano_user"]
        vnfm_password  = context["vnfm_mano_pass"]
        #VNFM Keycloak server.
        nfvo_keycloak_server_url = context["vnfm_mano_keycloak_server_url"]
        #VNFM base URL.
        vnfm_base_url  = context["vnfm_mano_base_url"]

        # Execute NFVO unregistration to the VNFM.
        vnfmSubscription = NfvoVnfmSubscription(vnfm_ip, vnfm_port, vnfm_base_url)
        vnfmSubscription.set_parameters(vnfm_username, vnfm_password)
        
        #Get Authentication mode ('basic' or 'oauth2').
        vnfm_auth_mode  = context["vnfm_mano_auth_mode"]
        
        if vnfm_auth_mode == 'oauth2' or vnfm_auth_mode == 'oauth_v2':            
            vnfmSubscription.set_parameters(vnfm_username, vnfm_password, vnfm_auth_mode, context['keycloak_server_url'])
        else:
            vnfmSubscription.set_parameters(vnfm_username, vnfm_password)

        #NFVO SOL003 version.
        nfvo_sol003_version  = context["nfvo_sol003_version"]

        #NFVO subscription id to the VNFM.
        nfvo_subs_id_to_vnfm = context["vnfm_subs_nfvo_id"]
        
        r = vnfmSubscription.unsubscribe(nfvo_subs_id_to_vnfm)
        
        r_details = ''
        status = vnfmSubscription.state
        if status == 'ENDED':
            r_details = 'Successful!'
            MSA_API.task_success(r_details, context, True)
        else:
            if isinstance(r, dict):
                r_details = str(r.json().get('detail'))
        
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True)
        print(ret)
        
    #Skip task message.
    MSA_API.task_success('Task skipped: NFVO was not subscribed to VNFM.', context)