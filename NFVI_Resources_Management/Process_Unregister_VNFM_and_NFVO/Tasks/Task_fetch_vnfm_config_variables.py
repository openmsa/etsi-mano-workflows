import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

'''
Get config variable value from managed entity (ME).
'''
def _get_config_variable (managed_entity_id, var_name, is_ignore_exception=False):
    try:
        var = Device(device_id=managed_entity_id).get_configuration_variable(var_name)
        value  = var.get("value")
        return value.strip()
    except:
        if is_ignore_exception:
            pass
        else:
            error_msg = "Config variable '" + var_name + "' can't be retrieved from " + managed_entity_id + " Managed Entity."
            MSA_API.task_error(error_msg, context, True) 

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vnfm_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
    #Get config variables values from VNFM ME.
    vnfm_mano_me_id = context["vnfm_device"][3:]
    vnfm_mano_ip    = Device(device_id=vnfm_mano_me_id).management_address
    vnfm_mano_user  = Device(device_id=vnfm_mano_me_id).login
    vnfm_mano_pass  = Device(device_id=vnfm_mano_me_id).password
    vnfm_mano_name  = Device(device_id=vnfm_mano_me_id).name
    
    ##Get VNFM Authentication mode ('basic' or 'oauth2').
    vnfm_mano_auth_mode  = _get_config_variable (vnfm_mano_me_id, "AUTH_MODE")
    
    ##Get VNFM API Base URL.
    vnfm_mano_base_url  = _get_config_variable (vnfm_mano_me_id, "BASE_URL")
    
    ##Get VNFM service port.
    vnfm_mano_port  = _get_config_variable (vnfm_mano_me_id, "HTTP_PORT")
    
    ##Get VNFM capabilities.
    vnfm_mano_capabilities  = _get_config_variable (vnfm_mano_me_id, "CAPABILITIES")
    
    ##Get VNFM sol003 version.
    vnfm_mano_sol003_version  = _get_config_variable (vnfm_mano_me_id, "SOL003_VERSION")
    
    #Store VNFM config variables values into the workflow service instance context.
    context["vnfm_mano_auth_mode"] = vnfm_mano_auth_mode
    context["vnfm_mano_ip"] = vnfm_mano_ip
    context["vnfm_mano_port"] = vnfm_mano_port
    context["vnfm_mano_user"] = vnfm_mano_user
    context["vnfm_mano_pass"] = vnfm_mano_pass
    context["vnfm_mano_capabilities"] = vnfm_mano_capabilities
    context["vnfm_mano_sol003_version"] = vnfm_mano_sol003_version
    context['vnfm_mano_base_url'] = vnfm_mano_base_url
    context['vnfm_mano_name'] = vnfm_mano_name
    
    
    if vnfm_mano_auth_mode == 'oauth_v2':
        #Get keycloak server URL. 
        keycloak_server_url  = _get_config_variable (vnfm_mano_me_id, "SIGNIN_REQ_PATH")
        context["vnfm_mano_keycloak_server_url"] = keycloak_server_url
        
    ##Get 3rd party S-VFNM boolean config variable (optional).
    is_third_party_vnfm  = _get_config_variable (vnfm_mano_me_id, "IS_THIRD_PARTY_VNFM", True)
    context["is_third_party_vnfm"] = is_third_party_vnfm
    
    MSA_API.task_success('VNFM config variables are stored into the context!', context, True) 