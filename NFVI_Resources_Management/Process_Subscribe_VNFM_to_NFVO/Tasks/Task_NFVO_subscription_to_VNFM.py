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
        #VNFM Keycloak server
        nfvo_keycloak_server_url = context["vnfm_mano_keycloak_server_url"]
        #VNFM base URL.
        vnfm_base_url  = context["vnfm_mano_base_url"]

        # Execute NFVO registration to teh VNFM.
        vnfmSubscription = NfvoVnfmSubscription(vnfm_ip, vnfm_port, vnfm_base_url)
        vnfmSubscription.set_parameters(vnfm_username, vnfm_password)
        
        #Set NFVO access infos.
        nfvo_mano_me_ref = context["nfvo_device"]
        nfvo_mano_me_id = context["nfvo_device"][3:]
        nfvo_mano_ip    = context["nfvo_mano_ip"]
        nfvo_mano_port  = context["nfvo_mano_port"]
        nfvo_mano_user  = context["nfvo_mano_user"]
        nfvo_mano_pass  = context["nfvo_mano_pass"]
        nfvo_base_url  = context["nfvo_mano_base_url"]
        nfvo_keycloak_server_url = context["nfvo_mano_keycloak_server_url"] 

        #Get Authentication mode ('basic' or 'oauth2').
        vnfm_auth_mode  = context["vnfm_mano_auth_mode"]
        
        if vnfm_auth_mode == 'oauth2' or vnfm_auth_mode == 'oauth_v2':            
            vnfmSubscription.set_parameters(vnfm_username, vnfm_password, vnfm_auth_mode, context['keycloak_server_url'])
        else:
            vnfmSubscription.set_parameters(vnfm_username, vnfm_password)
        
        #NFVO URL Variables.
        http_protocol = 'http'
        nfvo_url = http_protocol + '://' + nfvo_mano_ip +':' + nfvo_mano_port + nfvo_base_url + 'sol003'
        
        #NFVO authification type.
        authType = ['BASIC']
        if nfvo_keycloak_server_url == 'basic':
            authType = ['BASIC']
            #Basic authentication parameters.
            authParamBasic =  {
                "userName": nfvo_mano_user,
                "password": nfvo_mano_pass
                }
        elif nfvo_keycloak_server_url == 'oauth2' or nfvo_keycloak_server_url == 'oauth_v2':
            authType = ['OAUTH2_CLIENT_CREDENTIALS']
            #Oauth2.0 authentication parameters.
            authParamOauth2 = {
                "clientId": nfvo_mano_user,
                "clientSecret": nfvo_mano_pass,
                "tokenEndpoint": context["keycloak_server_url"],
                "grantType": "client_credentials"
            }
        
        #NFVO SOL003 version.
        nfvo_sol003_version  = context["nfvo_sol003_version"]
        
        #vnfn name var.
        nfvo_name = 'nfvo-1'
        
        content = {
                    "name": nfvo_name,
                    "authentification": {
                        "authType": authType
                     },
                     "localUser": {
                 	    "clientId": vnfm_username,
                 	    "secretId": vnfm_password
                     },
                    "url": nfvo_url,
                    "ignoreSsl": True,
                    "tlsCert": "",
                    "version": nfvo_sol003_version,
                    "subscriptionType": "VNF",
                    "serverType": "NFVO"
                    }
        #Insert authentication parameters into the content.
        if nfvo_keycloak_server_url == 'basic':
            content['authentification']['authParamBasic'] = authParamBasic
        elif nfvo_keycloak_server_url == 'oauth2' or nfvo_keycloak_server_url == 'oauth_v2':
            content['authentification']['authParamOauth2'] = authParamOauth2
            
        r = vnfmSubscription.subscribe(content)
        
        try:
            location = r.headers["Location"]
            
            vnfm_subs_nfvo_id = location.split("/")[-1]
            context["vnfm_subs_nfvo_id"] = vnfm_subs_nfvo_id
            
            #Check asynchronously the subscribe_nfvo_to_vnfm operation status.
            r = vnfmSubscription.subscribe_completion_wait(vnfm_subs_nfvo_id, 60)
        except KeyError:
            pass
        
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
    MSA_API.task_success('NFVO to VNFM registration is skipped.', context)