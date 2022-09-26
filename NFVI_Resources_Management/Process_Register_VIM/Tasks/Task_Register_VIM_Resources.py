import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NfviVim import NfviVim


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vim_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
    #Set NFVO access infos.
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
    
    #Init NFVI VIM object.
    nfviVim = NfviVim(nfvo_mano_ip, nfvo_mano_port)
    
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        nfviVim.set_parameters(nfvo_mano_user, nfvo_mano_pass, auth_mode, context['keycloak_server_url'])
    else:
        nfviVim.set_parameters(nfvo_mano_user, nfvo_mano_pass)
    
    #Get VimCOnnectionInfo, retrieve from openstack Managed Entity configuration vars + ME informations.
    vim_me_id = context["vim_device"][3:]
    vim__ip    = Device(device_id=vim_me_id).management_address
    vim_username  = Device(device_id=vim_me_id).login
    vim_password  = Device(device_id=vim_me_id).password
    
    vim_type = 'OPENSTACK_V3'
    
    http_protocol_var = Device(device_id=vim_me_id).get_configuration_variable("HTTP_PROTOCOL")
    http_protocol = http_protocol_var.get("value")
    
    endpoint = http_protocol  +'://' + vim__ip + ':5000/v3'
    
    project_id_var= Device(device_id=vim_me_id).get_configuration_variable("TENANT_ID")
    project_id = project_id_var.get("value")
    
    project_domain_var =  Device(device_id=vim_me_id).get_configuration_variable("PROJECT_DOMAIN_ID")
    project_domain = project_domain_var.get("value")
    
    user_domain_var = Device(device_id=vim_me_id).get_configuration_variable("USER_DOMAIN_ID")
    user_domain = user_domain_var.get("value")
    
    content = {
               "vimId": str(uuid.uuid4()),
               "vimType": vim_type,
               "interfaceInfo": {
                   "endpoint": endpoint,
                   "non-strict-ssl": "true"
                   },
               "accessInfo": {
                   "username": vim_username,
                   "password": vim_password,
                   "projectId": project_id,
                   "projectDomain": project_domain,
                   "userDomain": user_domain,
                   "vim_project": "cbamnso"
                   },
               "geoloc": {
                   "lng": 45.75801,
                   "lat": 4.8001016
                   }
               }

    r = nfviVim.nfvi_vim_register(content)
    
    r_details = ''
    status = nfviVim.state
    if status == 'ENDED':
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(nfviVim.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)