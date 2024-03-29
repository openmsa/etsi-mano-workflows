from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add("nfvo_device", var_type='Device')
    dev_var.add("service_instance_name", var_type='String')
    context = Variables.task_call(dev_var)
    
    mano_me_id = context["nfvo_device"][3:]
    mano_ip    = Device(device_id=mano_me_id).management_address
    mano_var   = Device(device_id=mano_me_id).get_configuration_variable("HTTP_PORT")
    mano_port  = mano_var.get("value")
    mano_user  = Device(device_id=mano_me_id).login
    mano_pass  = Device(device_id=mano_me_id).password
    
    context["mano_ip"]   = mano_ip
    context["mano_port"] = mano_port
    context["mano_user"] = mano_user
    context["mano_pass"] = mano_pass
    
    #Get Authentication mode ('basic' or 'oauth2').
    auth_mode_var   = Device(device_id=mano_me_id).get_configuration_variable("AUTH_MODE")
    auth_mode  = auth_mode_var.get("value")
    context["auth_mode"] = auth_mode
    
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
    
    #Get nfvo base url.
    mano_base_url_var   = Device(device_id=mano_me_id).get_configuration_variable("BASE_URL")
    mano_base_url  = mano_base_url_var.get("value")
    context["mano_base_url"] = mano_base_url
    
    #Get SOL005 version.
    sol005_version_var   = Device(device_id=mano_me_id).get_configuration_variable("SOL005_VERSION")
    sol005_version  = sol005_version_var.get("value")
    context.update(sol005_version=sol005_version)
    
    ret = MSA_API.process_content('ENDED', f'Task OK!', context, True)
    print(ret)
