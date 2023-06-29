import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfPkgSol005 import VnfPkgSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vnf_package_name', var_type='String')
    dev_var.add('vnf_package_id', var_type='String')
    context = Variables.task_call(dev_var)
    
    #Set the WF service instance name.
    if 'vnf_package_name' in context:
        vnf_package_name = context['vnf_package_name']
        if vnf_package_name:
            context.update(service_instance_name=vnf_package_name)
    
    #Get SOL00X version from context.
    sol_version = context.get('sol005_version')

    vnfPkgApi = VnfPkgSol005(context["mano_ip"], context["mano_port"], context["mano_base_url"], sol_version)
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfPkgApi.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfPkgApi.set_parameters(context['mano_user'], context['mano_pass'])
    
    pkg = {"userDefinedData": {"name": context['vnf_package_name']}}
    r = vnfPkgApi.vnf_packages_post(pkg)
   
    r_details = ''
    status = vnfPkgApi.state
    MSA_API.task_success(str(r), context, True)
    if status == 'ENDED':
        r_details = 'Successful!'
        vnf_package_id = r.json().get('id')
        context.update(vnf_package_id=vnf_package_id)
    else:
        try:
            r_details = str(r.json().get('detail'))
        except:
            MSA_API.task_success(r.json(), context, True)
        
    ret = MSA_API.process_content(vnfPkgApi.state, f'{r}' + ': ' + r_details, context, True) 
    print(ret)

