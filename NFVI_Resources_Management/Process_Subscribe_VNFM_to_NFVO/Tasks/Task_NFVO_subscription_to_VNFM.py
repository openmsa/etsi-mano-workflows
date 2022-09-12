import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vnfm_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
    #Get VNFM ME connection informations.
    vnfm_me_ref = context["vnfm_device"]
    vnfm_me_id = context["vnfm_device"][3:]
    vnfm_ip    = Device(device_id=vnfm_me_id).management_address
    vnfm_var   = Device(device_id=vnfm_me_id).get_configuration_variable("HTTP_PORT")
    vnfm_port  = vnfm_var.get("value")
    vnfm_username  = Device(device_id=vnfm_me_id).login
    vnfm_password  = Device(device_id=vnfm_me_id).password
    
    vnfmSubscription = NfvoVnfmSubscription(vnfm_ip, vnfm_port)
    vnfmSubscription.set_parameters(vnfm_username, vnfm_password)
    
    #Set NFVO access infos.
    nfvo_mano_me_ref = context["nfvo_device"]
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = Device(device_id=nfvo_mano_me_id).management_address
    nfvo_mano_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("HTTP_PORT")
    nfvo_mano_port  = nfvo_mano_var.get("value")
    nfvo_mano_user  = Device(device_id=nfvo_mano_me_id).login
    nfvo_mano_pass  = Device(device_id=nfvo_mano_me_id).password
    
    #Get Authentication mode ('basic' or 'oauth2').
    auth_mode_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("AUTH_MODE")
    auth_mode  = auth_mode_var.get("value")
    context["auth_mode"] = auth_mode
    
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=vnfm_mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        vnfmSubscription.set_parameters(vnfm_mano_user, vnfm_mano_pass, auth_mode, context['keycloak_server_url'])
    else:
        vnfmSubscription.set_parameters(vnfm_mano_user, vnfm_mano_pass)
        
    #NFVO URL Variables.
    http_protocol = 'http'
    nfvo_url = http_protocol + '://' + nfvo_mano_ip +':' + nfvo_mano_port +'/ubi-etsi-mano/sol003'
    
    #NFVO authification type.
    authType = ['BASIC']
    if auth_mode == 'basic':
        authType = ['BASIC']
        #Basic authentication parameters.
        authParamBasic =  {
            "userName": nfvo_username,
            "password": nfvo_password
            }
        }
    elif auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        authType = ['OAUTH2_CLIENT_CREDENTIALS']
        #Oauth2.0 authentication parameters.
        authParamOauth2 = {
            "clientId": nfvo_username,
            "clientSecret": nfvo_password,
            "tokenEndpoint": context["keycloak_server_url"],
            "grantType": "client_credentials"
        }
    
    #NFVO SOL003 version.
    nfvo_sol003_version = '2.6.1'
    
    #vnfn name var.
    nfvo_name = 'nfvo-1'
    
    content = {
                "name": nfvo_name,
                "authentification": {
                "authType": authType,
                "url": nfvo_url,
                "ignoreSsl": True,
                "tlsCert": "",
                "version": nfvo_sol003_version,
                "subscriptionType": "VNF",
                "serverType": "NFVO"
                }
    #Insert authentication parameters into the content.
    if auth_mode == 'basic':
        context['authParamBasic'] = authParamBasic
    elif auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        context['authParamOauth2'] = authParamOauth2
        
    r = vnfmSubscription.subscribe(content)
    
    location = r.headers["Location"]

    vnfm_subs_nfvo_id = location.split("/")[-1]
    context["vnfm_subs_nfvo_id"] = vnfm_subs_nfvo_id
    
    #Check asynchronously the subscribe_nfvo_to_vnfm operation status.
    r = vnfmSubscription.subscribe_completion_wait(vnfm_subs_nfvo_id, 60)
    status = r['serverStatus']
    if status != 'SUCCESS':
        MSA_API.task_error('Subscribe VNFM ('+ vnfm_me_ref +') to NFVO ('+ nfvo_mano_me_ref +') is status=' + status, context)# context['vim_id'] = r.json()['id']
        
    MSA_API.task_success('Subscribe VNFM ('+ vnfm_me_ref +') to NFVO ('+ nfvo_mano_me_ref +') is status=' + status, context)