import sys
import json
from msa_sdk import constants
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import util

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003
from custom.ETSI.VnfLcmOpOccsSol003 import VnfLcmOpOccsSol003
from custom.ETSI.VnfPkgSol005 import VnfPkgSol005


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)
    #Get authentication type.
    auth_mode = context["vnfm_mano_auth_mode"]
    process_id = context['SERVICEINSTANCEID']

    if context.get('is_vnf_instance_exist') != True:
        vnfPkg = VnfPkgSol005(context["nfvo_mano_ip"], context["nfvo_mano_port"], context['nfvo_mano_base_url'])
        vnfLcm = VnfLcmSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
        util.log_to_process_file(process_id, '**** auth_mode: '+auth_mode)
        
        if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
            vnfLcm.set_parameters(context['vnfm_mano_ip'], context['vnfm_mano_pass'], auth_mode, context['vnfm_mano_keycloak_server_url'])
            vnfPkg.set_parameters(context['nfvo_mano_user'], context['nfvo_mano_pass'], auth_mode, context['nfvo_mano_keycloak_server_url'])
        else:
            vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
            vnfPkg.set_parameters(context['nfvo_mano_user'], context['nfvo_mano_pass'])
            
        r1 = vnfPkg.vnf_packages_get_package(context["vnf_pkg_id"])
        var_check = r1.json()["operationalState"]
        
        if var_check != 'ENABLED':
            MSA_API.task_error('VNF package is '+var_check, context)
        
        vnf_instance_id = context["vnf_instance_id"]
        util.log_to_process_file(process_id, '**** vnf_instance_id: '+vnf_instance_id)

        #content = {'flavourId': 'simple'}
        content = context["vnf_instantiation_payload"]
        r = vnfLcm.vnf_lcm_instantiate_vnf(context["vnf_instance_id"], content)
        
        r_details = ''
        status = vnfLcm.state
        if status == 'ENDED':
            location = ''
            try:
                location = r.headers['Location']
            except:
                MSA_API.task_error('Instantiate VNF is failed.', context)
                
            context["vnf_lcm_op_occ_id"] = location.split("/")[-1]
            r_details = 'Successful!'
        else:
            r_details = str(r.json().get('detail'))
            status = 'FAILED'
        
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
        print(ret)
        sys.exit()
    else:
        vnfLcmOpOccs = VnfLcmOpOccsSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
        if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
            vnfLcmOpOccs.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'], auth_mode, context['vnfm_keycloak_server_url'])
        else:
            vnfLcmOpOccs.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
            
        vnf_instance_id = context['vnf_instance_id']
        
        vnf_lcm_op_occ_id = vnfLcmOpOccs.vnf_lcm_op_occs_get_id(vnf_instance_id)
        context["vnf_lcm_op_occ_id"] = vnf_lcm_op_occ_id
        
        #MSA_API.task_error('The VNF managed entities are created.' + vnf_lcm_op_occ_id, context)
        
    ret = MSA_API.process_content(vnfLcmOpOccs.state, f'VNF Instance context is stored.', context, True)
    print(ret)
    sys.exit()