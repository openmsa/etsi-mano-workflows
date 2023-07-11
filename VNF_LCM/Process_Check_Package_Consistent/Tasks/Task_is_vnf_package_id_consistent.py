import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003
from custom.ETSI.VnfPkgSol005 import VnfPkgSol005

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vnf_pkg_id', var_type='OBMFRef')
    context = Variables.task_call(dev_var)
    
    mano_me_id = context["nfvo_device"][3:]
    mano_ip    = Device(device_id=mano_me_id).management_address
    mano_var   = Device(device_id=mano_me_id).get_configuration_variable("HTTP_PORT")
    mano_port  = mano_var.get("value")
    mano_user  = Device(device_id=mano_me_id).login
    mano_pass  = Device(device_id=mano_me_id).password
    
    #Get Authentication mode ('basic' or 'oauth2').
    auth_mode_var   = Device(device_id=mano_me_id).get_configuration_variable("AUTH_MODE")
    auth_mode  = auth_mode_var.get("value")
    context["auth_mode"] = auth_mode
    
    #SOL003 VNF Lifecycle Management
    vnfLcm = VnfLcmSol003(context["mano_ip"], context["mano_port"])
    
    #SOL005 Package Management
    vnfPkg = VnfPkgSol005(context["mano_ip"], context["mano_port"])
    
    auth_mode = context["auth_mode"]
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        vnfPkg.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfPkg.set_parameters(context['mano_user'], context['mano_pass'])
    
    r1 = vnfPkg.vnf_packages_get_package(context["vnf_pkg_id"])
    
    if vnfPkg.state != "ENDED":
        ret = MSA_API.process_content(nsd.state, f'{r1.content}', context, True)
        print(ret)
        exit()
    
    #Store the VNFD Id for checking in the context.
    vnfd_id = r1.json()["vnfId"]
    context['vnfd_id_checking'] = vnfd_id
    
    ret = MSA_API.process_content(nsLcm.state, f'{r1}, {r2}', context, True)
    print(ret)