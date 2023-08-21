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
    
    #SOL005 Package Management
    vnfPkg = VnfPkgSol005(context["nfvo_mano_ip"], context["nfvo_mano_port"])
    
    nfvo_mano_auth_mode = context["nfvo_mano_auth_mode"]
    if nfvo_mano_auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_server_url = context["nfvo_mano_keycloak_server_url"]
        
        vnfPkg.set_parameters(nfvo_mano_user, nfvo_mano_pass, nfvo_mano_auth_mode, keycloak_server_url)
    else:
        vnfPkg.set_parameters(nfvo_mano_user, nfvo_mano_pass)
        
   #Execute the operation to get the VNF Package details.
    r = vnfPkg.vnf_packages_get_package(context["vnf_pkg_id"])

    #Check the operation status.
    status = vnfPkg.state
    if status != "ENDED":
        ret = MSA_API.process_content(vnfPkg.state, f'{r}', context, True)
        print(ret)
        exit()
        
    #Store the VNFD Id for checking in the context.
    vnfd_id = r.json()["vnfId"]
    context['vnfd_id_checking'] = vnfd_id
    
    ret = MSA_API.process_content(nsLcm.state, f'{r}, {r}', context, True)
    print(ret)