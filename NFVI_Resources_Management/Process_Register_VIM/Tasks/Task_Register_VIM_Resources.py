import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NfviVim import NfviVim

if __name__ == "__main__":
    dev_var = Variables()
    dev_var.add('vim_device', var_type='Device')
    dev_var.add("vim_registration_id", var_type='String')
    dev_var.add("service_instance_name", var_type='String')
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
    region = context["vim_region"]
    vim_type = context["vim_type"]
    endpoint = context["vim_auth_endpoint"]
    sdn_endpoint = context["vim_sdn_endpoint"]
    cnf_dnsServer = context["cnf_dnsServer"]
    keyPair = context["cnf_keypair"]
    cnf_endpoint = context["cnf_endpoint"]
    extNetworkId = context["cnf_extNetworkId"]
    k8sVersion = context["cnf_k8sVersion"]
    flavorId = context["cnf_flavorId"]
    cnf_image = context["cnf_image"]
    cnf_flavor = context["cnf_flavor"]
    cnf_minNumberInstance = context["cnf_minNumberInstance"]
    cni_module = context["cni_module"]
    cni_version = context["cni_version"]
    csi_module = context["csi_module"]
    csi_version = context["csi_version"]
    ccm_module = context["ccm_module"]
    ccm_version = context["ccm_version"]
    
    #InterfaceInfo dict.
    interfaceInfo = {"endpoint": endpoint, "non-strict-ssl": "true"}
    
    #Main content
    if context["cnf"] == True:
        content = {
                   "vimId": str(uuid.uuid4()),
                   "vimType": vim_type,
                   "interfaceInfo": {
                       "endpoint": cnf_endpoint,
                       "connection-timeout": 5,
                       "read-timeout": 5,
                       "retry": 4
                   },
                   "accessInfo": {
                       "username": vim_username,
                       "password": vim_password,
                       "projectId": project_id,
                       "projectDomain": project_domain,
                       "userDomain": user_domain,
                       "region": region
                       },
                   "cnfInfo": {
                       "dnsServer": cnf_dnsServer,
                       "keyPair": keyPair,
                       "extNetworkId": extNetworkId,
                       "k8sVersion": k8sVersion,
                       "master": {
                           "flavorId": flavorId,
                           "flavor": cnf_flavor,
                           "minNumberInstance": cnf_minNumberInstance,
                           "image": cnf_image
                           },
                       "worker": {
                           "flavorId": flavorId,
                           "flavor": cnf_flavor,
                           "minNumberInstance": cnf_minNumberInstance,
                           "image": cnf_image
                           },
                       "cni": {
                           "module": cni_module,
                           "version": cni_version
                           },
                       "csi": {
                           "module": csi_module,
                           "version": csi_version
                           },
                       "ccm": {
                           "module": ccm_module,
                           "version": ccm_version
                           }
                   },
                   "geoloc": {
                       "lng": 45.75801,
                       "lat": 4.8001016
                       }
                   }
    else:
        content = {
                   "vimId": str(uuid.uuid4()),
                   "vimType": vim_type,
                   "accessInfo": {
                       "username": vim_username,
                       "password": vim_password,
                       "projectId": project_id,
                       "projectDomain": project_domain,
                       "userDomain": user_domain,
                       "region": region
                       },
                   "geoloc": {
                       "lng": 45.75801,
                       "lat": 4.8001016
                       }
                   }
    
    
    #Add the sdn controller endpoint.
    if sdn_endpoint:
        interfaceInfo['sdn-endpoint'] = sdn_endpoint
        
    #Insert InterfaceInfo dict to the main content.
    content.update(interfaceInfo=interfaceInfo)
    
    #Execute the VIM registration to the NFVO
    r = nfviVim.nfvi_vim_register(content)
    
    r_details = ''
    status = nfviVim.state
    if status == 'ENDED':
        if isinstance(r.json(), dict):
            vim_registration_id = r.json().get('id')
            #Store the vimId in the context.
            context["vim_registration_id"] = vim_registration_id
            r_details = 'SUCCESS! The VIM is registered with id=' + vim_registration_id + '.'
    else:
        if isinstance(r.json, dict):
            r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(nfviVim.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)