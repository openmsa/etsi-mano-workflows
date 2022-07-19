from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfLcmOpOccsSol003 import VnfLcmOpOccsSol003


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    vnfLcmOpOccs = VnfLcmOpOccsSol003(context["mano_ip"], context["mano_port"], context['mano_base_url'])
    
    auth_mode = context["auth_mode"]
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfLcmOpOccs.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfLcmOpOccs.set_parameters(context['mano_user'], context['mano_pass'])

    r = vnfLcmOpOccs.vnf_lcm_op_occs_completion_wait(context["vnf_lcm_op_occ_id"])
    
    context["operation_state"] = r.json()['operationState']

    ret = MSA_API.process_content(vnfLcmOpOccs.state, f'{context["operation_state"]}', context, True)
    print(ret)