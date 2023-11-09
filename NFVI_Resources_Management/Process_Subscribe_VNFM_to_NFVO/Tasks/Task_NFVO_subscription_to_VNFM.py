import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
dev_var.add("nfvo_subscription_id", var_type='String')
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
        #Get VNFM Keycloak server
        vnfm_mano_keycloak_server_url = context["vnfm_mano_keycloak_server_url"]
        #Get VNFM base URL.
        vnfm_mano_base_url  = context["vnfm_mano_base_url"]
        #Get VNFM Authentication mode ('basic' or 'oauth2').
        vnfm_auth_mode  = context["vnfm_mano_auth_mode"]

        # Execute NFVO registration to teh VNFM.
        nfvoSubscription = NfvoVnfmSubscription(vnfm_ip, vnfm_port, vnfm_mano_base_url)
        nfvoSubscription.set_parameters(vnfm_username, vnfm_password)
        
        if vnfm_auth_mode == 'oauth2' or vnfm_auth_mode == 'oauth_v2':
            nfvoSubscription.set_parameters(vnfm_username, vnfm_password, vnfm_auth_mode, vnfm_mano_keycloak_server_url)
        else:
            nfvoSubscription.set_parameters(vnfm_username, vnfm_password)
        
        #Set NFVO access infos.
        nfvo_mano_me_ref = context["nfvo_device"]
        nfvo_mano_me_id = context["nfvo_device"][3:]
        nfvo_mano_ip    = context["nfvo_mano_ip"]
        nfvo_mano_port  = context["nfvo_mano_port"]
        nfvo_mano_user  = context["nfvo_mano_user"]
        nfvo_mano_pass  = context["nfvo_mano_pass"]
        nfvo_mano_base_url  = context["nfvo_mano_base_url"]
        nfvo_mano_keycloak_server_url = context["nfvo_mano_keycloak_server_url"] 
        #Get NFVO SOL003 version.
        nfvo_mano_sol003_version = context["nfvo_mano_sol003_version"]
        #Get VNFM Authentication mode ('basic' or 'oauth2').
        nfvo_mano_auth_mode  = context["nfvo_mano_auth_mode"]
        
        #NFVO URL Variables.
        http_protocol = 'http'
        nfvo_url = http_protocol + '://' + nfvo_mano_ip +':' + nfvo_mano_port + nfvo_mano_base_url + 'sol003'
        
        #NFVO authification type.
        authType = ['BASIC']
        if nfvo_mano_auth_mode == 'basic':
            authType = ['BASIC']
            #Basic authentication parameters.
            authParamBasic =  {
                "userName": nfvo_mano_user,
                "password": nfvo_mano_pass
                }
        elif nfvo_mano_auth_mode == 'oauth2' or nfvo_mano_auth_mode == 'oauth_v2':
            authType = ['OAUTH2_CLIENT_CREDENTIALS']
            #Oauth2.0 authentication parameters.
            authParamOauth2 = {
                "clientId": nfvo_mano_user,
                "clientSecret": nfvo_mano_pass,
                "tokenEndpoint": nfvo_mano_keycloak_server_url,
                "grantType": "client_credentials"
            }
        
        #vnfn name var.
        nfvo_name = 'nfvo-1'
        
        content = {
                    "name": nfvo_name,
                    "authentification": {
                        "authType": authType
                     },
                     "localUser": {
                        "tokenEndpoint": nfvo_mano_keycloak_server_url,
                        "clientSecret": nfvo_mano_pass,
                        "clientId": nfvo_mano_user,
                     },
                    "url": nfvo_url,
                    "ignoreSsl": True,
                    "tlsCert": "",
                    "version": nfvo_mano_sol003_version,
                    "subscriptionType": "VNF",
                    "serverType": "NFVO"
                    }
        #Insert authentication parameters into the content.
        if nfvo_mano_auth_mode == 'basic':
            content['authentification']['authParamBasic'] = authParamBasic
        elif nfvo_mano_auth_mode == 'oauth2' or nfvo_mano_auth_mode == 'oauth_v2':
            content['authentification']['authParamOauth2'] = authParamOauth2
            
        r = nfvoSubscription.subscribe(content)
        
        try:
            location = r.headers["Location"]
            
            nfvo_subs_id_to_vnfm = location.split("/")[-1]
            context["nfvo_subs_id_to_vnfm"] = nfvo_subs_id_to_vnfm
            #Set the nfvo_subscription_id (display variable).
            context["nfvo_subscription_id"] = nfvo_subs_id_to_vnfm
            
            #Check asynchronously the subscribe_nfvo_to_vnfm operation status.
            r = nfvoSubscription.subscribe_completion_wait(nfvo_subs_id_to_vnfm, 60)
        except KeyError:
            pass
        
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
                MSA_API.task_success(r_details, context, True)

            elif serverStatus == 'FAILED':
                error_detail = r_dict.get('failureDetails').get('detail')
                MSA_API.task_error('The server subscription status is ' + serverStatus + '. \nFailure Details: ' + error_detail, context, True)
        else:
            if isinstance(r_dict, dict):
                r_details = str(r_dict.get('detail'))
        
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details , context, True)
        print(ret)
        
    #Skip task message.
    MSA_API.task_success('The NFVO to VNFM registration is skipped.', context)