import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants
from msa_sdk.device import Device
from custom.ETSI.DescriptorGraphGeneration import DescriptorGraphGeneration


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_me', var_type='String')
    context = Variables.task_call(dev_var)
    
    mano_me_id = context["nfvo_me"][3:]
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
    
    vnfGraph = DescriptorGraphGeneration(context["mano_ip"], context["mano_port"])
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        vnfGraph.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfGraph.set_parameters(context['mano_user'], context['mano_pass'])
    
    ### Check the response status. If status == 200:
    ## Write response body in the repository data. 
    
    ret = MSA_API.task_success('New service is created successfully!', context, True)
    