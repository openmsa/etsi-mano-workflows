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
    r = vnfPkgApi.vnf_packages_get_package(context['vnf_package_id'])
    
    onboarding_state = r.json().get('onboardingState')
    operational_state = r.json().get('operationalState')
    if onboarding_state != 'ONBOARDED' or operational_state != 'ENABLED':
        ret = MSA_API.process_content(MSA_API.FAILED, 'Onboarding State: ' + onboarding_state + ' Operational state: ' + operational_state, context, True)
        print(ret)
    else:
        r_details = ''
        status = vnfPkgApi.state
        if status == 'ENDED':
            r_details = 'Successful!'
        else:
            r_details = str(r.json().get('detail'))
        
        ret = MSA_API.process_content(vnfPkgApi.state, f'{r}' + ': ' + r_details, context, True)
        print(ret)