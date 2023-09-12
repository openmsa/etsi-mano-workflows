from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants
import json

from custom.ETSI.VnfPkgSol005 import VnfPkgSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vnf_pkg_id', var_type='OBMFRef')
    context = Variables.task_call(dev_var)
    
    #Get VNFM config variables values from context.
    nfvo_mano_auth_mode = context["nfvo_mano_auth_mode"]
    nfvo_mano_base_url = context["nfvo_mano_base_url"]
    nfvo_mano_ip = context["nfvo_mano_ip"]
    nfvo_mano_port = context["nfvo_mano_port"]
    nfvo_mano_user = context["nfvo_mano_user"]
    nfvo_mano_pass = context["nfvo_mano_pass"]
    
    #Create VNF Package Sol005 object instancs.
    vnfPkg = VnfPkgSol005(nfvo_mano_ip,nfvo_mano_port, nfvo_mano_base_url)
    
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
    
    #Store VNFD id into the context.
    context["vnfd_id"] = r.json()["vnfdId"]
    
    #Check the VNF Package operational state.
    operational_state = r.json()["operationalState"]
    if operational_state != 'ENABLED':
        MSA_API.task_error("The VNF package operationalState must be 'ENABLED', instead of '" + operational_state + ".", context)
        
    ret = MSA_API.process_content(status, f'{r}: The VNF package operationalState is ' + operational_state, context, True) 
    print(ret)