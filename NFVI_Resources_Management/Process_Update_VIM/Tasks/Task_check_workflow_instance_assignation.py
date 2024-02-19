from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
context = Variables.task_call(dev_var)


if __name__ == "__main__":
    
    if not 'service_instance_assignment' in context:
        #Skip the service instance assignment. the check is not applicable for old version this workflow service instance.
        MSA_API.task_success('Task OK', context, True)
        
    #Get workflow service assignment to a operation type (VIM registration/deletion or VNFM and NFVO un/subscription).
    service_assignment = context["service_instance_assignment"]

    if service_assignment == "vim_registration_mgmt":
        pass
    elif service_assignment == "vnfm_and_nfvo_subscription_mgmt":
        MSA_API.task_error("This service instance is dedicated for the VNFM and NFVO subscription / unsubscription operations only.\nPlease create a new workflow service to manage the VIM registration / unregistration.", context, True)
    else:
        MSA_API.task_error("This service instance was not assigned to any type of service (VIM or MANO un/registration).", context, True)
    
    MSA_API.task_success('Task OK', context, True)


