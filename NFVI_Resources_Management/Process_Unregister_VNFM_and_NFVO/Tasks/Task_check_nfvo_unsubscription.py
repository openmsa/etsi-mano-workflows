import uuid
import sys
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
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
            vnfmSubscription.set_parameters(vnfm_username, vnfm_password, vnfm_auth_mode, nfvo_keycloak_server_url)
        else:
            vnfmSubscription.set_parameters(vnfm_username, vnfm_password)

        #NFVO subscription id to the VNFM.
        nfvo_subs_id_to_vnfm = context["nfvo_subs_id_to_vnfm"]
        
        #NFVO subscription id to the VNFM.
        if 'nfvo_subs_id_to_vnfm' in context:
            nfvo_subs_id_to_vnfm = context["nfvo_subs_id_to_vnfm"]
        else:
            ret = MSA_API.process_content('WARNING',"Task skipped: the server subscription is empty for this workflow instance context.", context, True)
            print(ret)
            sys.exit()
            
        r = vnfmSubscription.subscribe_get_status(nfvo_subs_id_to_vnfm)
        
        r_details = ''
        status = vnfmSubscription.state
        
        if isinstance(r, dict):
            if status == 'ENDED':
                MSA_API.task_error('The NFVO subscription (id=' + nfvo_subs_id_to_vnfm +') was not deleted.', context, True)
            else:
                r_dict = r.json()
                if isinstance(r_dict, dict):
                    r_details = str((r_dict).get('detail'))
            
        elif not r:
                MSA_API.task_success('The NFVO subscription (id=' + nfvo_subs_id_to_vnfm +') is deleted.', context, True)
                
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True)
        print(ret)
        
    #Skip task message.
    MSA_API.task_success('Task skipped: the NFVO was not subscribed to VNFM.', context)