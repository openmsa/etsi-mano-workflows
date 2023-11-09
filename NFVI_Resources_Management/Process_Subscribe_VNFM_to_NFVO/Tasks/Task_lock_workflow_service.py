from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()

context = Variables.task_call(dev_var)

if __name__ == "__main__":
    #Lock the workflow instance for the NFVO and VNFM subscription management.
    context["service_instance_assignment"] = "vnfm_and_nfvo_subscription_mgmt"
    
    ret = MSA_API.process_content('ENDED', 'This workflow service is now dedicated to the VNFM / NFVO subscription related operations.', context, True)
    print(ret)

