import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants
import json

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
dev_var.add('nfvo_device', var_type='Device')
dev_var.add('vnfm_device', var_type='Device')
dev_var.add('is_vnfm_register_only', var_type='Boolean')
dev_var.add("service_instance_name", var_type='String')
dev_var.add("vnfm_subscription_id", var_type='String')
context = Variables.task_call(dev_var)

if __name__ == "__main__":

    #Get VNFM ME connection informations.
    vnfm_me_ref = context["vnfm_device"]
    vnfm_me_id = context["vnfm_device"][3:]
    vnfm_ip = context["vnfm_mano_ip"]
    vnfm_port = context["vnfm_mano_port"]
    vnfm_username = context["vnfm_mano_user"]
    vnfm_password = context["vnfm_mano_pass"]
    vnfm_capabilities = context["vnfm_mano_capabilities"]
    vnfm_sol003_version = context["vnfm_mano_sol003_version"]
    #Get VNFM Authentication mode ('basic' or 'oauth2').
    vnfm_mano_auth_mode = context["vnfm_mano_auth_mode"]
    #Get VNFM keycloak server url.
    vnfm_mano_keycloak_server_url  = context["vnfm_mano_keycloak_server_url"]
    #VNFM - SOL003 Base URL
    vnfm_mano_base_url = context["vnfm_mano_base_url"]
  
    #Set NFVO access infos.
    nfvo_mano_me_ref = context["nfvo_device"]
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip = context["nfvo_mano_ip"]
    nfvo_mano_port = context["nfvo_mano_port"]
    nfvo_mano_user = context["nfvo_mano_user"]
    nfvo_mano_pass = context["nfvo_mano_pass"]
    nfvo_mano_name = context['nfvo_mano_name']
    #Get VNFM keycloak server url.
    nfvo_mano_keycloak_server_url = context["nfvo_mano_keycloak_server_url"]
    
    #Get NFVO Base URL.
    nfvo_mano_base_url = context["nfvo_mano_base_url"]
    
    #Get Authentication mode ('basic' or 'oauth2').
    nfvo_mano_auth_mode = context["nfvo_mano_auth_mode"]
    
    vnfmSubscription = NfvoVnfmSubscription(nfvo_mano_ip, nfvo_mano_port, nfvo_mano_base_url)
    
    if nfvo_mano_auth_mode == 'oauth2' or nfvo_mano_auth_mode == 'oauth_v2':
        vnfmSubscription.set_parameters(nfvo_mano_user, nfvo_mano_pass, nfvo_mano_auth_mode, nfvo_mano_keycloak_server_url)
    else:
        vnfmSubscription.set_parameters(nfvo_mano_user, nfvo_mano_pass)
    
    
    #VNFM URL Variables.
    http_protocol = 'http'
    vnfm_url = http_protocol + '://' + vnfm_ip +':' + vnfm_port
    
    if vnfm_mano_base_url != '/':
        vnfm_url = vnfm_url + vnfm_mano_base_url
    
    if vnfm_mano_base_url == '/vnfm-webapp/' or vnfm_mano_base_url == '/ubi-etsi-mano/':
        vnfm_url = vnfm_url + 'sol003'

    #VNFM authification type.
    authType = ['BASIC']
    if vnfm_mano_auth_mode == 'basic':
        authType = ['BASIC']
        #Basic authentication parameters.
        authParamBasic =  {
            "userName": vnfm_username,
            "password": vnfm_password
            }
    elif vnfm_mano_auth_mode == 'oauth2' or vnfm_mano_auth_mode == 'oauth_v2':
        authType = ['OAUTH2_CLIENT_CREDENTIALS']
        #Oauth2.0 authentication parameters.
        authParamOauth2 = {
            "clientId": vnfm_username,
            "clientSecret": vnfm_password,
            "tokenEndpoint": vnfm_mano_keycloak_server_url,
            "grantType": "client_credentials"
        }
    
    #VNFM SOL003 version.
    if not vnfm_sol003_version:
        vnfm_sol003_version = '2.6.1'
    
    #VNFM capabilities.
    if not vnfm_capabilities:
        capabilities = ['100:ubi-v2.6.1']
    capabilities = [vnfm_capabilities]
    
    #vnfn name var.
    vnfm_mano_name = context['vnfm_mano_name']
    
    content = {
                "name": vnfm_mano_name,
                "authentification": {
                    "authType": authType
                 },
                 "localUser": {
                    "tokenEndpoint": vnfm_mano_keycloak_server_url,
                    "clientSecret": vnfm_password,
                    "clientId": vnfm_username,
                 },
                "url": vnfm_url,
                "ignoreSsl": True,
                "tlsCert": "",
                "version": vnfm_sol003_version,
                "subscriptionType": "VNF",
                "serverType": "VNFM",
                "capabilities": capabilities
                }
    
    #Insert authentication parameters into the content.
    if vnfm_mano_auth_mode == 'basic':
        content['authentification']['authParamBasic'] = authParamBasic
    elif vnfm_mano_auth_mode == 'oauth2' or vnfm_mano_auth_mode == 'oauth_v2':
        content['authentification']['authParamOauth2'] = authParamOauth2
    
    #Execute the subscription/registration of the VNFM to the NFVO.
    r = vnfmSubscription.subscribe(content)
    
    try:
        location = r.headers["Location"]
        vnfm_subs_id_to_nfvo = location.split("/")[-1]
        context["vnfm_subs_id_to_nfvo"] = vnfm_subs_id_to_nfvo
        #Set the nfvo_subscription_id (display variable).
        context["vnfm_subscription_id"] = vnfm_subs_id_to_nfvo
        
        #Check asynchronously the subscribe_nfvo_to_vnfm operation status.
        r = vnfmSubscription.subscribe_completion_wait(vnfm_subs_id_to_nfvo, 60)
    except KeyError:
        pass
    
    # Check the type of the response. In case subscription http failure (e.g: http 500) the 'r' type is dictionnary. Otherwise it is a Response object type.
    r_dict = r
    if not isinstance(r_dict, dict):
        r_dict = r.json()
        
    r_details = ''
    
    status = vnfmSubscription.state
    if status == 'ENDED':
        serverStatus = r_dict.get('serverStatus')
        context.update(vnfm_subscription_serverStatus=serverStatus)
        
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
