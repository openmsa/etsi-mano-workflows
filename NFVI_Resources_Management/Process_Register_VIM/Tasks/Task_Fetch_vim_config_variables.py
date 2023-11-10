import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

'''
Get config variable value from managed entity (ME).
'''
def _get_config_variable (managed_entity_id, var_name, isrequired=True):
    try:
        var = Device(device_id=managed_entity_id).get_configuration_variable(var_name)
        value  = var.get("value")
        return value.strip()
    except:
        if isrequired == True:
            error_msg = "Config variable '" + var_name + "' can't be retrieved from " + managed_entity_id + " Managed Entity."
            MSA_API.task_error(error_msg, context, True) 
        else:
            return ''

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vim_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
    #Get VimCOnnectionInfo, retrieve from openstack Managed Entity configuration vars + ME informations.
    vim_me_id = context["vim_device"][3:]
    vim_ip    = (Device(device_id=vim_me_id).management_address).strip()
    vim_username  = Device(device_id=vim_me_id).login
    vim_password  = Device(device_id=vim_me_id).password
    
    http_protocol = _get_config_variable (vim_me_id, "HTTP_PROTOCOL")
    
    project_id = _get_config_variable (vim_me_id, "TENANT_ID")
    
    project_domain = _get_config_variable (vim_me_id, "PROJECT_DOMAIN_ID")
    
    user_domain = _get_config_variable (vim_me_id, "USER_DOMAIN_ID")
    
    #Get SDN controller (e.g: Juniper contrail) endpoint if exists.
    sdn_endpoint = _get_config_variable (vim_me_id, "SDN_CONTROLLER_ENDPOINT", False)
    
    #VIM type.
    vim_type = _get_config_variable (vim_me_id, "SDN_CONTROLLER_ENDPOINT", False)
    
    if not vim_type or vim_type == '':
        vim_type = 'OPENSTACK_V3'
    
    #VIM authication endpoint.
    vim_auth_endpoint = ''
    
    if vim_type == 'OPENSTACK_V3':
        vim_auth_endpoint = http_protocol  +'://' + vim_ip + ':5000/v3'
    
    #Store VIM config variables values into the workflow service instance context.
    context["vim_ip"] = vim_ip.strip()
    context["vim_username"] = vim_username.strip()
    context["vim_password"] = vim_password.strip()
    context["vim_project_id"] = project_id.strip()
    context["vim_http_protocol"] = http_protocol.strip()
    context["vim_project_id"] = project_id.strip()
    context["vim_project_domain"] = project_domain.strip()
    context["vim_user_domain"] = user_domain.strip()
    context["vim_type"] = vim_type.strip()
    context["vim_auth_endpoint"] = vim_auth_endpoint.strip()
    context["vim_sdn_endpoint"] = sdn_endpoint.strip()
    
    MSA_API.task_success('VIM config variables are stored into the context!', context, True) 