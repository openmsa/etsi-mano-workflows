import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfPkgSol005 import VnfPkgSol005

from msa_sdk import util
import time

if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    #Get SOL00X version from context.
    sol_version = context.get('sol005_version')

    vnfPkgApi = VnfPkgSol005(context["mano_ip"], context["mano_port"], context["mano_base_url"], sol_version)
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfPkgApi.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfPkgApi.set_parameters(auth_mode, context['mano_user'], context['mano_pass'])
    
    time.sleep(5)
    vnf_package_id = context['vnf_package_id']
    r = vnfPkgApi.vnf_packages_get_package(vnf_package_id)
    r_dict = r.json()

    onboarding_state = r_dict.get('onboardingState')
    operational_state = r_dict.get('operationalState')
    if onboarding_state != 'ONBOARDED' or operational_state != 'ENABLED':
        msg = msg = 'Onboarding State: ' + onboarding_state + ' Operational state: ' + operational_state + '.'
        error_detail = ''
        if 'onboardingFailureDetails' in r_dict:
            error_detail = str(r_dict.get('onboardingFailureDetails').get('detail'))
            error_status = str(r_dict.get('onboardingFailureDetails').get('status'))
            msg = 'Onboarding CSAR file (package) to the VNF package (id='+ vnf_package_id +') is FAILED:\n - HTTP status: ' + error_status + '\n - Detail: ' + error_detail
        MSA_API.task_error(msg, context, True)
    else:
        r_details = ''
        status = vnfPkgApi.state
        if status == 'ENDED':
            r_details = 'Successful!'
        else:
            #Get details.
            r_details = str(r_dict.get('detail'))

        ret = MSA_API.process_content(vnfPkgApi.state, f'{r}' + ': ' + r_details, context, True)
        print(ret)