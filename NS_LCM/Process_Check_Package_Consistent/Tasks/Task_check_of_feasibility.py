from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NsLcmSol005 import NsLcmSol005
from custom.ETSI.NsdSol005 import NsdSol005

if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)
    
    #Get original Pkg ID (stored during the instantiation) from the context.
    origin_ns_package_id = context['ns_package_id']
    
    if not origin_ns_package_id:
        msg = "The original NS package id is empty from the context. \n NS instantiation is required beforehand to run this process." 
        MSA_API.task_error(msg, context)
        
    MSA_API.task_success(msg, context)