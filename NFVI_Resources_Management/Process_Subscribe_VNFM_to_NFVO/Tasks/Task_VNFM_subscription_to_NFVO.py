import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
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
    vnfm_var   = Device(device_id=vnfm_me_id).get_configuration_variable("CAPABILITIES")
    vnfm_capabilities  = vnfm_var.get("value")
    vnfm_var   = Device(device_id=vnfm_me_id).get_configuration_variable("SOL003_VERSION")
    vnfm_sol003_version  = vnfm_var.get("value")
    
    #Get Authentication mode ('basic' or 'oauth2').
    auth_mode_var   = Device(device_id=vnfm_me_id).get_configuration_variable("AUTH_MODE")
    auth_mode  = auth_mode_var.get("value")
    context["auth_mode"] = auth_mode
    
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
    
    nfvoSubscription = NfvoVnfmSubscription(nfvo_mano_ip, nfvo_mano_port)
    
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        nfvoSubscription.set_parameters(nfvo_mano_user, nfvo_mano_pass, auth_mode, context['keycloak_server_url'])
    else:
        nfvoSubscription.set_parameters(nfvo_mano_user, nfvo_mano_pass)
    
    #VNFM URL Variables.
    http_protocol = 'http'
    vnfm_url = http_protocol + '://' + vnfm_ip +':' + vnfm_port +'/ubi-etsi-mano/sol003'
    
    #VNFM authification type.
    authType = ['BASIC']
    if auth_mode == 'basic':
        authType = ['BASIC']
        #Basic authentication parameters.
        authParamBasic =  {
            "userName": vnfm_username,
            "password": vnfm_password
            }
        }
    elif auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        authType = ['OAUTH2_CLIENT_CREDENTIALS']
        #Oauth2.0 authentication parameters.
        authParamOauth2 = {
            "clientId": vnfm_username,
            "clientSecret": vnfm_password,
            "tokenEndpoint": context["keycloak_server_url"],
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
    vnfm_name = 'vnfm-' + capabilities[0]
    
    content = {
                "name": vnfm_name,
                "authentification": {
                "authType": authType,
                "url": vnfm_url,
                "ignoreSsl": True,
                "tlsCert": "",
                "version": vnfm_sol003_version,
                "subscriptionType": "VNF",
                "serverType": "VNFM",
                "capabilities": capabilities
                }
    
    #Insert authentication parameters into the content.
    if auth_mode == 'basic':
        context['authParamBasic'] = authParamBasic
    elif auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        context['authParamOauth2'] = authParamOauth2
    
    #Execute the subscription/registration of the VNFM to the NFVO.
    r = nfvoSubscription.subscribe(content)
    
    location = r.headers["Location"]

    nfvo_subs_vnfm_id = location.split("/")[-1]
    context["nfvo_subs_vnfm_id"] = nfvo_subs_vnfm_id
    
    #Check asynchronously the subscribe_nfvo_to_vnfm operation status.
    r = nfvoSubscription.subscribe_completion_wait(nfvo_subs_vnfm_id, 60)
    status = r['serverStatus']
    if status != 'SUCCESS':
        MSA_API.task_error('Subscribe NFVO ('+ nfvo_mano_me_ref +') to VNFM ('+ vnfm_me_ref +'), status=' + status, context)
        
    MSA_API.task_success('Subscribe NFVO ('+ nfvo_mano_me_ref +') to VNFM ('+ vnfm_me_ref +'), status=' + status, context)