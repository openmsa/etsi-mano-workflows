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
    vnfPkg = VnfPkgSol005(context["nfvo_mano_ip"], context["nfvo_mano_port"], context["nfvo_mano_base_url"])
    
    nfvo_mano_auth_mode = context["nfvo_mano_auth_mode"]
    if nfvo_mano_auth_mode == 'oauth_v2':
        vnfPkg.set_parameters(context["nfvo_mano_user"], context["nfvo_mano_pass"], nfvo_mano_auth_mode, context["nfvo_mano_keycloak_server_url"])
    else:
        vnfPkg.set_parameters(context["nfvo_mano_user"], context["nfvo_mano_pass"])
        
   #Execute the operation to get the VNF Package details.
    r = vnfPkg.vnf_packages_get_package(context["vnf_pkg_id"])

    #Check the operation status.
    status = vnfPkg.state
    if status != "ENDED":
        ret = MSA_API.process_content(vnfPkg.state, f'{r}', context, True)
        print(ret)
        exit()
        
    #Store the VNFD Id for checking in the context.
    #MSA_API.task_error(json.dumps(r.json()), context, True)
    if "vnfdId" in r.json():
        vnfd_id = r.json()["vnfdId"]
        vnfpkg_id = r.json()["id"]
        context['vnfd_id_checking'] = vnfd_id
        ret = MSA_API.process_content(vnfPkg.state, f'{r}, The VNF Package Id still available from NFVO catalog:\nvnf_package_id = ' + vnfpkg_id + '\nvnfd_id = ' + vnfd_id, context, True)
        print(ret)
        exit()

    MSA_API.task_error('Failed to found the "vnfdId" attribute when trying to get the VNF Package details from NFVO.')