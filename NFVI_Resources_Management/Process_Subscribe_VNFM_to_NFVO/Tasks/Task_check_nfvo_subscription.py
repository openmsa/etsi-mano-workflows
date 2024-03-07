import uuid
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
        vnfm_keycloak_server_url = context["vnfm_mano_keycloak_server_url"]
        #VNFM base URL.
        vnfm_base_url  = context["vnfm_mano_base_url"]

        # Execute NFVO unregistration to the VNFM.
        nfvoSubscription = NfvoVnfmSubscription(vnfm_ip, vnfm_port, vnfm_base_url)
        nfvoSubscription.set_parameters(vnfm_username, vnfm_password)
        
        #Get Authentication mode ('basic' or 'oauth2').
        vnfm_auth_mode  = context["vnfm_mano_auth_mode"]
        
        if vnfm_auth_mode == 'oauth2' or vnfm_auth_mode == 'oauth_v2':            
            nfvoSubscription.set_parameters(vnfm_username, vnfm_password, vnfm_auth_mode, vnfm_keycloak_server_url)
        else:
            nfvoSubscription.set_parameters(vnfm_username, vnfm_password)

        #NFVO subscription id to the VNFM.
        nfvo_subs_id_to_vnfm = context["nfvo_subs_id_to_vnfm"]
        
        r = nfvoSubscription.subscribe_get_status(nfvo_subs_id_to_vnfm)
        
        # Check the type of the response. In case subscription http failure (e.g: http 500) the 'r' type is dictionnary. Otherwise it is a Response object type.
        r_dict = r
        if not isinstance(r_dict, dict):
            r_dict = r.json()

        r_details = ''
        status = nfvoSubscription.state

        if status == 'ENDED':
            serverStatus = r_dict.get('serverStatus')
            context.update(nfvo_subscription_serverStatus=serverStatus)
            
            if serverStatus == 'SUCCESS':
                r_details = 'The server subscription status is ' + serverStatus + '!'
                #Store in the context the VNFM to NFVO subscription object.
                context['nfvo_to_vnfm_subscription'] = r_dict
                MSA_API.task_success(r_details, context, True)

            elif serverStatus == 'FAILED':
                error_detail = r_dict.get('failureDetails').get('detail')
                MSA_API.task_error('The server subscription status is ' + serverStatus + '. \nFailure Details: ' + error_detail, context, True)
        else:
            if isinstance(r_dict, dict):
                r_details = str(r_dict.get('detail'))
                
            ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True)
            print(ret)
        
    #Skip task message.
    MSA_API.task_success('Task skipped: NFVO was not subscribed to the VNFM.', context)