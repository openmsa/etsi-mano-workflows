from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('vnf_pkg_id', var_type='OBMFRef')
    context = Variables.task_call(dev_var)
    
    #Get original Pkg ID (stored during the instantiation) from the context.
    origin_vnf_package_id = context['vnf_pkg_id']
    
    if not origin_vnf_package_id:
        msg = "The original VNF package id is empty from the context. \n VNF instantiation is required beforehand to run this process." 
        MSA_API.task_error(msg, context)
        
    MSA_API.task_success('The original VNF Package Id retrieved from the context is "' + origin_vnf_package_id + '"', context)