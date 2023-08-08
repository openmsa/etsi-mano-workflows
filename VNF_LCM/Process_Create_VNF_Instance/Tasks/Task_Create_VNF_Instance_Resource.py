from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants
import json

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003
from custom.ETSI.VnfPkgSol005 import VnfPkgSol005
from msa_sdk import util

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vnfm_device', var_type='Device')
    dev_var.add('vnf_pkg_id', var_type='OBMFRef')
    dev_var.add('vnf_instance_name', var_type='String')
    dev_var.add('vnf_instance_description', var_type='String')
    dev_var.add('is_vnf_instance_exist', var_type='Boolean')
    dev_var.add('vnf_instance_id', var_type='String')
    dev_var.add('ns_service_instance_ref', var_type='String')
    context = Variables.task_call(dev_var)
    process_id = context['SERVICEINSTANCEID']
    mano_me_id = context["vnfm_device"][3:]
    mano_ip    = Device(device_id=mano_me_id).management_address
    mano_var   = Device(device_id=mano_me_id).get_configuration_variable("HTTP_PORT")
    mano_port  = mano_var.get("value")
    mano_user  = Device(device_id=mano_me_id).login
    mano_pass  = Device(device_id=mano_me_id).password
    
    mano_base_url_var   = Device(device_id=mano_me_id).get_configuration_variable("BASE_URL")
    mano_base_url  = mano_base_url_var.get("value")
    context["mano_base_url"] = mano_base_url


    #Get SOL003 version.
    sol003_version_var   = Device(device_id=mano_me_id).get_configuration_variable("SOL003_VERSION")
    sol003_version  = sol003_version_var.get("value")
    context.update(sol003_version=sol003_version)

    try:
        #--------------------- 3rd party S-VFNM ---------------
        is_third_party_vnfm   = Device(device_id=mano_me_id).get_configuration_variable("IS_THIRD_PARTY_VNFM")
        is_third_party_vnfm  = is_third_party_vnfm.get("value")
        context["is_third_party_vnfm"] = is_third_party_vnfm
    except:
        pass
    #---------------------------------------------
    
    context["mano_ip"]   = mano_ip
    context["mano_port"] = mano_port
    context["mano_user"] = mano_user
    context["mano_pass"] = mano_pass
    
    nfvo_mano_me_id = context["nfvo_device"][3:]
    nfvo_mano_ip    = Device(device_id=nfvo_mano_me_id).management_address
    nfvo_mano_var   = Device(device_id=nfvo_mano_me_id).get_configuration_variable("HTTP_PORT")
    nfvo_mano_port  = nfvo_mano_var.get("value")
    nfvo_mano_user  = Device(device_id=nfvo_mano_me_id).login
    nfvo_mano_pass  = Device(device_id=nfvo_mano_me_id).password
    
    context["nfvo_mano_ip"]   = nfvo_mano_ip
    context["nfvo_mano_port"] = nfvo_mano_port
    context["nfvo_mano_user"] = nfvo_mano_user
    context["nfvo_mano_pass"] = nfvo_mano_pass
    
    #Get Authentication mode ('basic' or 'oauth2').
    auth_mode_var   = Device(device_id=mano_me_id).get_configuration_variable("AUTH_MODE")
    auth_mode  = auth_mode_var.get("value")
    context["auth_mode"] = auth_mode
    
    sol003_version = context.get('sol003_version')

    #Create VNF Instance resources.
    vnfLcm = VnfLcmSol003(context["mano_ip"], context["mano_port"], context["mano_base_url"], sol003_version)
    
    #Create VNF Package Sol005 object instancs.
    vnfPkg = VnfPkgSol005(context["nfvo_mano_ip"], context["nfvo_mano_port"], context["mano_base_url"])
    
    #Create VNF LCM service instance of an existing VNF Instance.
    if context.get('is_vnf_instance_exist') == True:
        vnf_instance_id = context.get('vnf_instance_id')
        util.log_to_process_file(process_id, '\n ici1\n')
        MSA_API.task_success('VNF LCM service instance is created for VNF instance id: {vnf_instance_id}.', context)

    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        #Get keycloak server URL.
        keycloak_url_var   = Device(device_id=mano_me_id).get_configuration_variable("SIGNIN_REQ_PATH")
        keycloak_server_url  = keycloak_url_var.get("value")
        context["keycloak_server_url"] = keycloak_server_url
        
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
        vnfPkg.set_parameters(context['nfvo_mano_user'], context['nfvo_mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'])
        vnfPkg.set_parameters(context['nfvo_mano_user'], context['nfvo_mano_pass'])
    
    r1 = vnfPkg.vnf_packages_get_package(context["vnf_pkg_id"])

    if vnfPkg.state != "ENDED":
        util.log_to_process_file(process_id, '\n ici2\n')
        ret = MSA_API.process_content(vnfPkg.state, f'{r1}',
                                      context, True)
        print(ret)
        exit()
        
    context["vnfd_id"] = r1.json()["vnfdId"]
    var_check = r1.json()["operationalState"]
    if var_check != 'ENABLED':
        util.log_to_process_file(process_id, '\n ici3\n')
        MSA_API.task_error('VNF package is '+var_check, context)
    
    '''
    metadata = {"deviceManufacturer": "",
                "deviceModel": ""
                }
    '''            
    vnfd_id = context["vnfd_id"]
    
    #--------------------- 3rd party S-VFNM ---------------
    metadata = {"onboardedVnfPkgInfoId": context["vnf_pkg_id"]}
    
    if "is_third_party_vnfm" in context:
        is_third_party_vnfm = context.get('is_third_party_vnfm')
        if is_third_party_vnfm == 'true':
            
            #Set default root base URL as '/' if empty and 3rd party VNFM.
            if not context["mano_base_url"]:
                context["mano_base_url"] = '/'
            
            #-------------------- RIBBON S-VNFM 3rd Party CUSTOM------------#
            vnfd_id = context["vnf_pkg_id"]
            #---------------------------------------------------------------#
    #---------------------------------------------

    payload = {"vnfdId": vnfd_id,
               "vnfInstanceName": context["vnf_instance_name"],
               "vnfInstanceDescription": "",
               "metadata": metadata
               }
    util.log_to_process_file(process_id, '\n toto1')
    r2 = vnfLcm.vnf_lcm_create_instance(payload)
    util.log_to_process_file(process_id, '\n toto2')

    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        lcm_data = r2.json()
        context["vnf_instance_id"] = lcm_data['id']
        r_details = 'Successful!'
    else:
        r_details = str(r2.json().get('detail'))
        status = 'FAILED'
        
    util.log_to_process_file(process_id, '\n ici3\n')
    ret = MSA_API.process_content(status, f'{r2}' + ': ' + r_details, context, True) 
    print(ret)