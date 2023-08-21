import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

'''
Get config variable value from managed entity (ME).
'''
def _get_config_variable (managed_entity_id, var_name):
    try:
        var = Device(device_id=managed_entity_id).get_configuration_variable(var_name)
        value  = var.get("value")
        return value
    except:
        erro_msg = "Config variable '" + var_name + "' can't be retrieved from " + managed_entity_id + " Managed Entity."
        MSA_API.task_error(error_msg, context, True) 

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
    #Get config variables values from VNFM ME.
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = Device(device_id=nfvo_mano_me_id).management_address
    nfvo_mano_user  = Device(device_id=nfvo_mano_me_id).login
    nfvo_mano_pass  = Device(device_id=nfvo_mano_me_id).password
    
    ##Get VNFM Authentication mode ('basic' or 'oauth2').
    nfvo_mano_auth_mode  = _get_config_variable (nfvo_mano_me_id, "AUTH_MODE")
    
    ##Get VNFM API Base URL.
    nfvo_mano_base_url  = _get_config_variable (nfvo_mano_me_id, "BASE_URL")
    
    ##Get VNFM service port.
    nfvo_mano_port  = _get_config_variable (nfvo_mano_me_id, "HTTP_PORT")
    
    #Store VNFM config variables values into the workflow service instance context.
    context["nfvo_mano_auth_mode"] = nfvo_mano_auth_mode
    context["nfvo_mano_base_url"] = nfvo_mano_base_url
    context["nfvo_mano_ip"] = nfvo_mano_ip
    context["nfvo_mano_port"] = nfvo_mano_port
    context["nfvo_mano_user"] = nfvo_mano_user
    context["nfvo_mano_pass"] = nfvo_mano_pass
    
    if nfvo_mano_auth_mode == 'oauth_v2':
        #Get keycloak server URL. 
        keycloak_server_url  = _get_config_variable (nfvo_mano_me_id, "SIGNIN_REQ_PATH")
        context["nfvo_mano_keycloak_server_url"] = keycloak_server_url
        
    MSA_API.task_success('NFVO config variables are stored into the context!', context, True) 