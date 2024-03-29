from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.VnfLcmSol003 import VnfLcmSol003


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add("aspect_id", var_type="String")
    dev_var.add("scale_level", var_type="Integer")
    context = Variables.task_call(dev_var)

    vnfLcm = VnfLcmSol003(context["mano_ip"], context["mano_port"], context['mano_base_url'])
    
    auth_mode = context["auth_mode"]
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['mano_user'], context['mano_pass'])
    
    content = {"additionalParams": {},
               "instantiationLevelId": "demo",
               "scaleInfo": [
                    {
                      "aspectId": context["aspect_id"],
                      "scaleLevel": int(context["scale_level"])
                    }
                  ]
               }

    r = vnfLcm.vnf_lcm_scale_to_level_instance_vnf(context["vnf_instance_id"],
                                                   content)
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        location = ''
        try:
            location = r.headers['Location']
        except:
            MSA_API.task_error('Scale-to-level VNF is failed.', context)
            
        context["vnf_lcm_op_occ_id"] = location.split("/")[-1]
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
    
    ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
    print(ret)