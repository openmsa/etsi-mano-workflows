import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NfviVim import NfviVim

if __name__ == "__main__":
    dev_var = Variables()
    dev_var.add('vim_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
    #Lock the workflow instance to be dedicated to the VIM registration management.
    context["service_instance_assignment"] = 'vim_registration_mgmt'
    
    #Set NFVO access infos.
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = context["nfvo_mano_ip"]
    nfvo_mano_port  = context["nfvo_mano_port"]
    nfvo_mano_user  = context["nfvo_mano_user"]
    nfvo_mano_pass  = context["nfvo_mano_pass"]
    #Get keycloak server URL.
    nfvo_keycloak_server_url  = context["nfvo_mano_keycloak_server_url"]
    #Get Authentication mode ('basic' or 'oauth2').
    auth_mode  = context["nfvo_mano_auth_mode"]
    #Get NFVO API base url.
    base_url  = context["nfvo_mano_base_url"]
    
    #Init NFVI VIM object.
    nfviVim = NfviVim(nfvo_mano_ip, nfvo_mano_port, base_url)
    
    if auth_mode == 'oauth_v2':
        nfviVim.set_parameters(nfvo_mano_user, nfvo_mano_pass, auth_mode, nfvo_keycloak_server_url)
    else:
        nfviVim.set_parameters(nfvo_mano_user, nfvo_mano_pass)
    
    #Get VimCOnnectionInfo, retrieve from openstack Managed Entity configuration vars + ME informations.
    vim_me_id = context["vim_device"][3:]
    
    vim_username = context["vim_username"]
    vim_password = context["vim_password"]
    http_protocol = context["vim_http_protocol"]
    project_id = context["vim_project_id"]
    project_domain = context["vim_project_domain"]
    user_domain = context["vim_user_domain"]
    vim_type = context["vim_type"]
    endpoint = context["vim_auth_endpoint"]
    sdn_endpoint = context["vim_sdn_endpoint"]
    
    #Get VIM registration id.
    if 'vim_registration_id' in context:
        vim_registration_id = context["vim_registration_id"]
    else:
        MSA_API.task_success("Task skipped: the vim registration id is empty for this workflow instance context.", context, True)
        
    #InterfaceInfo dict.
    interfaceInfo = {"endpoint": endpoint}
    
    #Main content
    content = {
               "vimId": vim_registration_id,
               "vimType": vim_type,
               "accessInfo": {
                   "username": vim_username,
                   "password": vim_password,
                   "projectId": project_id,
                   "projectDomain": project_domain,
                   "userDomain": user_domain,
                   "vim_project": "cbamnso"
                   }
               }
    #Add the sdn controller endpoint.
    if sdn_endpoint:
        interfaceInfo['sdn-endpoint'] = sdn_endpoint
        
    #Insert InterfaceInfo dict to the main content.
    content.update(interfaceInfo=interfaceInfo)
    
    #Execute the VIM registration to the NFVO
    r = nfviVim.nfvi_vim_register_update(vim_registration_id, content)
    
    
    
    r_details = ''
    status = nfviVim.state
    if status == 'ENDED':
        if isinstance(r.json(), dict):
            vim_registration_id = r.json().get('id')
            #Store the vimId in the context.
            context["vim_registration_id"] = vim_registration_id
            r_details = 'SUCCESS! The VIM registered with id=' + vim_registration_id + ' is updated.'
    elif status == 'FAIL': 
        if isinstance(r.json(), dict):
            error_detail = r.json().get('detail')
            MSA_API.task_error('FAILED! The VIM registered with id=' + vim_registration_id + ' update is failed. \nFailure Details: ' + error_detail, context, True)
    else:
        if isinstance(r.json, dict):
            r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(nfviVim.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)