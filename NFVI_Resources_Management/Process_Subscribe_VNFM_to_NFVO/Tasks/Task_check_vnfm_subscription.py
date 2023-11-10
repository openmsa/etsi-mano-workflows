import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
context = Variables.task_call(dev_var)

if __name__ == "__main__":
    
    #Get NFVO ME connection informations.
    nfvo_me_ref = context["nfvo_device"]
    nfvo_me_id = context["nfvo_device"][3:]
    nfvo_ip    = context["nfvo_mano_ip"]
    nfvo_port  = context["nfvo_mano_port"]
    nfvo_username  = context["nfvo_mano_user"]
    nfvo_password  = context["nfvo_mano_pass"]
    #NFVO Keycloak server.
    nfvo_keycloak_server_url = context["nfvo_mano_keycloak_server_url"]
    #NFVO base URL.
    nfvo_base_url  = context["nfvo_mano_base_url"]

    #Init the NfvoVnfmSubscription object class.
    vnfmSubscription = NfvoVnfmSubscription(nfvo_ip, nfvo_port, nfvo_base_url)
    vnfmSubscription.set_parameters(nfvo_username, nfvo_password)
    
    #Get Authentication mode ('basic' or 'oauth2').
    nfvo_auth_mode  = context["nfvo_mano_auth_mode"]
    
    if nfvo_auth_mode == 'oauth2' or nfvo_auth_mode == 'oauth_v2':            
        vnfmSubscription.set_parameters(nfvo_username, nfvo_password, nfvo_auth_mode, nfvo_keycloak_server_url)
    else:
        vnfmSubscription.set_parameters(nfvo_username, nfvo_password)

    #Get VNFM subscription status by id.
    vnfm_subs_id_to_nfvo = context["vnfm_subs_id_to_nfvo"]
    r = vnfmSubscription.subscribe_get_status(vnfm_subs_id_to_nfvo)
    
    #Check the type of the response. In case subscription http failure (e.g: http 500) the 'r' type is dictionnary. 
    #Otherwise it is a Response object type.
    r_dict = r
    if not isinstance(r_dict, dict):
        r_dict = r.json()

    r_details = ''
    status = vnfmSubscription.state

    if status == 'ENDED':
        serverStatus = r_dict.get('serverStatus')
        context.update(nfvo_subscription_serverStatus=serverStatus)
        
        if serverStatus == 'SUCCESS':
            r_details = 'The server subscription status is ' + serverStatus + '!'
            MSA_API.task_success(r_details, context, True)

        elif serverStatus == 'FAILED':
            error_detail = r_dict.get('failureDetails').get('detail')
            MSA_API.task_error('The server subscription status is ' + serverStatus + '. \nFailure Details: ' + error_detail, context, True)
    else:
        if isinstance(r_dict, dict):
            r_details = str(r_dict.get('detail'))
            
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True)
        print(ret)
        