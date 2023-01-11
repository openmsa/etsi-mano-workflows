from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants

from custom.ETSI.NsLcmOpOccsSol005 import NsLcmOpOccsSol005


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    nsLcmOpOccsInfo = NsLcmOpOccsSol005(context["mano_ip"], context["mano_port"])
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        nsLcmOpOccsInfo.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        nsLcmOpOccsInfo.set_parameters(context['mano_user'], context['mano_pass'])
        
    r = nsLcmOpOccsInfo.ns_lcm_op_occs_completion_wait(context["ns_lcm_op_occ_id"], 900)
    
    #----------
    if nsLcmOpOccsInfo.state == "ENDED":
        context["ns_lcm_op_occs"] = r.json()
        operationState = context["ns_lcm_op_occs"]["operationState"]
        
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
        
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
        print(ret)
        sys.exit()
    #----------
    
    ret = MSA_API.process_content(nsLcmOpOccsInfo.state, f'{r}' + ': ' + r_details, context, True) 
    print(ret)