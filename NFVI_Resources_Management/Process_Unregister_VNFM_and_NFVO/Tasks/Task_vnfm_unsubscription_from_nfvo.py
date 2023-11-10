import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
dev_var.add('is_vnfm_register_only', var_type='Boolean')
dev_var.add("service_instance_name", var_type='String')
dev_var.add("vnfm_subscription_id", var_type='String')
context = Variables.task_call(dev_var)

if __name__ == "__main__":

    #Set NFVO access infos.
    nfvo_mano_me_ref = context["nfvo_device"]
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = context["nfvo_mano_ip"]
    nfvo_mano_port  = context["nfvo_mano_port"]
    nfvo_mano_user  = context["nfvo_mano_user"]
    nfvo_mano_pass  = context["nfvo_mano_pass"]
    nfvo_base_url  = context["nfvo_mano_base_url"]
    nfvo_keycloak_server_url = context["nfvo_mano_keycloak_server_url"]
    nfvo_auth_mode = context["nfvo_mano_auth_mode"]
    
    nfvoSubscription = NfvoVnfmSubscription(nfvo_mano_ip, nfvo_mano_port, nfvo_base_url)
    
    if nfvo_auth_mode == 'oauth2' or nfvo_auth_mode == 'oauth_v2':
        nfvoSubscription.set_parameters(nfvo_mano_user, nfvo_mano_pass, nfvo_auth_mode, nfvo_keycloak_server_url)
    else:
        nfvoSubscription.set_parameters(nfvo_mano_user, nfvo_mano_pass)

    #Get VNFM suscription id.
    vnfm_subs_id_to_nfvo = context["vnfm_subs_id_to_nfvo"]
    #Execute the unsubscription of the VNFM from the NFVO.
    r = nfvoSubscription.unsubscribe(vnfm_subs_id_to_nfvo)
    
    # Check the type of the response. In case subscription http failure (e.g: http 500) the 'r' type is dictionnary. 
    #Otherwise it is a Response object type.
    #r_dict = r
    #if not isinstance(r_dict, dict):
    #    MSA_API.task_error(str(r_dict), context, True)
    #    r_dict = r.json()
    
    r_details = ''
    status = nfvoSubscription.state
    if status == 'ENDED':
        r_details = 'Successful!'
        MSA_API.task_success(r_details, context, True)
    else:
        if isinstance(r, dict):
            r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True)
    print(ret)
