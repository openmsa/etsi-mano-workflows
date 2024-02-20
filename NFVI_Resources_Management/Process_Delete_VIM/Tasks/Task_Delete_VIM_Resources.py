import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NfviVim import NfviVim


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    context = Variables.task_call(dev_var)
    
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
        
    #Get VIM registration id.
    if 'vim_registration_id' in context:
        vim_registration_id = context["vim_registration_id"]
    else:
        MSA_API.task_success("Task skipped: the vim registration id is empty for this workflow instance context.", context, True)
        
    #Delete registered VIM by id.
    r = nfviVim.nfvi_vim_delete(vim_registration_id)
    
    r_details = ''
    status = nfviVim.state
    if status == 'ENDED':
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(nfviVim.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)
