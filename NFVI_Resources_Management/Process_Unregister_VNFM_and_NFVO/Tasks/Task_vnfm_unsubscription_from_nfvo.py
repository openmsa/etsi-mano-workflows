import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.NfvoVnfmSubscription import NfvoVnfmSubscription

dev_var = Variables()
dev_var.add('nfvo_device', var_type='Device')
dev_var.add('vnfm_device', var_type='Device')
dev_var.add('is_vnfm_register_only', var_type='Boolean')
dev_var.add("service_instance_name", var_type='String')
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
    vnfm_subs_id_to_nfvo = context("nfvo_subs_vnfm_id")
    #Execute the unsubscription of the VNFM from the NFVO.
    r = nfvoSubscription.subscribe(vnfm_subs_id_to_nfvo)
    
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
