from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NsLcmSol005 import NsLcmSol005
from custom.ETSI.NsdSol005 import NsdSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
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
    
    #SOL005 NS Lifecycle Management
    nsLcm = NsLcmSol005(context["mano_ip"], context["mano_port"])
    
    #SOL005 Package Management
    nsd = NsdSol005(context["mano_ip"], context["mano_port"])
    
    auth_mode = context["auth_mode"]
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        nsLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
        nsd.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        nsLcm.set_parameters(context['mano_user'], context['mano_pass'])
        nsd.set_parameters(context['mano_user'], context['mano_pass'])
    
    r1 = nsd.nsd_descriptors_get(context['ns_package_id'])
    
    if nsd.state != "ENDED":
        ret = MSA_API.process_content(nsd.state, f'{r1.content}', context, True)
        print(ret)
        exit()
    
    #Store the NSD Id for checking in the context.
    nsd_id = r1.json()["nsdId"]
    context['nsd_id_checking'] = nsd_id
    
    ret = MSA_API.process_content(nsLcm.state, f'{r1}, {r2}', context, True)
    print(ret)