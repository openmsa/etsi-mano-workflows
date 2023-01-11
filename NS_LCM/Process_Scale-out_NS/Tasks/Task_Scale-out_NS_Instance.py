from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
import sys

from custom.ETSI.NsLcmSol005 import NsLcmSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('aspectId', var_type='String')
    dev_var.add('numberOfSteps', var_type='String')
    context = Variables.task_call(dev_var)
    
    nsLcm = NsLcmSol005(context["mano_ip"], context["mano_port"])
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        nsLcm.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'])
    else:
        nsLcm.set_parameters(context['mano_user'], context['mano_pass'])
    
    ns_instance_id = context["ns_instance_id"]
    
    #scale-out payload.
    payload = dict()
    
    numberOfSteps = int(context.get('numberOfSteps'))
    aspectId = context.get('aspectId')
    scaleNsByStepsData = dict(scalingDirection="SCALE_OUT", aspectId=aspectId, numberOfSteps=numberOfSteps)
    
    scaleNsData = dict()
    scaleNsData.update(scaleNsByStepsData=scaleNsByStepsData)
    
    scaleType = "SCALE_NS"
    payload.update(scaleType=scaleType, scaleNsData=scaleNsData)
    
    #Get NS package id.
    ns_instance_id = context.get('ns_instance_id')

    r = nsLcm.ns_lcm_scale_ns(ns_instance_id, payload)
    
        #----------
    if nsLcm.state == "ENDED":
        location = ''
        try:
            location = r.headers['Location']
        except:
            MSA_API.task_error('NS Scale-out is failed.', context)
            
        context["ns_lcm_op_occ_id"] = location.split("/")[-1]
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        status = 'FAILED'
        
        ret = MSA_API.process_content(status, f'{r}' + ': ' + r_details, context, True) 
        print(ret)
        sys.exit()
    #----------
    
    ret = MSA_API.process_content(nsLcm.state, f'NS Scaled-out is success!',
                                  context, True)
    print(ret)
    sys.exit()