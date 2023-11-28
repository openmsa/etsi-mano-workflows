from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NfviVim import NfviVim
from custom.ETSI.NfvoGrant import NfvoGrant


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vim_id', var_type='String')
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
    nfvoGrant = NfvoGrant(nfvo_mano_ip, nfvo_mano_port, base_url)
    
    if auth_mode == 'oauth_v2':
        nfvoGrant.set_parameters(nfvo_mano_user, nfvo_mano_pass, auth_mode, nfvo_keycloak_server_url)
    else:
        nfvoGrant.set_parameters(nfvo_mano_user, nfvo_mano_pass)
    
    #As a VIM delete pre-requisite, delete all the grant objects on the NFVO.
    r = nfvoGrant.nfvo_grant_all_delete()
    
    #Checking the of the operation response.
    r_details = ''
    status = nfvoGrant.state
    if status == 'ENDED':
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(nfvoGrant.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)
