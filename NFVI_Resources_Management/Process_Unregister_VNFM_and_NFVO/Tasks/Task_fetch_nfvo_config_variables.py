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
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('cnf', var_type='Boolean')
    dev_var.add('cnf_keypair', var_type='Composite')
    dev_var.add('cnf_endpoint', var_type='String')
    dev_var.add('cnf_extNetworkId', var_type='String')
    dev_var.add('cnf_k8sVersion', var_type='String')
    dev_var.add('cnf_flavorId', var_type='String')
    dev_var.add('cnf_image', var_type='String')
    dev_var.add('cnf_dnsServer', var_type='String')
    dev_var.add('cnf_flavor', var_type='String')
    dev_var.add('cnf_minNumberInstance', var_type='String')
    dev_var.add('cni_module', var_type='String')
    dev_var.add('cni_version', var_type='String')
    dev_var.add('csi_module', var_type='String')
    dev_var.add('csi_version', var_type='String')
    dev_var.add('ccm_module', var_type='String')
    dev_var.add('ccm_version', var_type='String')
    context = Variables.task_call(dev_var)
    
    #Get config variables values from NFVO ME.
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = Device(device_id=nfvo_mano_me_id).management_address
    nfvo_mano_user  = Device(device_id=nfvo_mano_me_id).login
    nfvo_mano_pass  = Device(device_id=nfvo_mano_me_id).password
    nfvo_mano_name  = Device(device_id=nfvo_mano_me_id).name
    
    ##Get NFVO Authentication mode ('basic' or 'oauth2').
    nfvo_mano_auth_mode  = _get_config_variable (nfvo_mano_me_id, "AUTH_MODE")
    
    ##Get NFVO API Base URL.
    nfvo_mano_base_url  = _get_config_variable (nfvo_mano_me_id, "BASE_URL")
    
    ##Get NFVO service port.
    nfvo_mano_port  = _get_config_variable (nfvo_mano_me_id, "HTTP_PORT")
    
    ##Get VNFM sol003 version.
    nfvo_mano_sol003_version  = _get_config_variable (nfvo_mano_me_id, "SOL003_VERSION")
    
    #Store NFVO config variables values into the workflow service instance context.
    context["nfvo_mano_auth_mode"] = nfvo_mano_auth_mode
    context["nfvo_mano_base_url"] = nfvo_mano_base_url
    context["nfvo_mano_ip"] = nfvo_mano_ip
    context["nfvo_mano_port"] = str(nfvo_mano_port)
    context["nfvo_mano_user"] = nfvo_mano_user
    context["nfvo_mano_pass"] = nfvo_mano_pass
    context["nfvo_mano_sol003_version"] = nfvo_mano_sol003_version
    context["nfvo_mano_name"] = nfvo_mano_name
    
    if nfvo_mano_auth_mode == 'oauth_v2':
        #Get keycloak server URL. 
        keycloak_server_url  = _get_config_variable (nfvo_mano_me_id, "SIGNIN_REQ_PATH")
        context["nfvo_mano_keycloak_server_url"] = keycloak_server_url
        
    MSA_API.task_success('NFVO config variables are stored into the context!', context, True) 