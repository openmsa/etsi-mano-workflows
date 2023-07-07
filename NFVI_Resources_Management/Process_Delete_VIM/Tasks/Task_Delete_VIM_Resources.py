import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NfviVim import NfviVim


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vim_id', var_type='String')
    context = Variables.task_call(dev_var)
    
    #Get NFVO access infos.
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = Device(device_id=nfvo_mano_me_id).management_address
    nfvo_mano_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("HTTP_PORT")
    nfvo_mano_port  = nfvo_mano_var.get("value").strip()
    nfvo_mano_user  = Device(device_id=nfvo_mano_me_id).login
    nfvo_mano_pass  = Device(device_id=nfvo_mano_me_id).password
    
    #Get NFVO API base url.
    base_url_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("BASE_URL")
    base_url  = base_url_var.get("value").strip()
    context["auth_mode"] = base_url
    
    nfviVim = NfviVim(nfvo_mano_ip, nfvo_mano_port, base_url)
    nfviVim.set_parameters(nfvo_mano_user, nfvo_mano_pass)
    
    r = nfviVim.nfvi_vim_delete(context["vim_id"])
    
    r_details = ''
    status = nfviVim.state
    if status == 'ENDED':
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
    
    ret = MSA_API.process_content(nfviVim.state, f'{r}' + ': ' + r_details, context, True)
    print(ret)
