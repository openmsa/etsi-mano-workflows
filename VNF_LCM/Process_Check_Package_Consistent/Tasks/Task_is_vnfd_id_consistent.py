from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vnf_pkg_id', var_type='OBMFRef')
    context = Variables.task_call(dev_var)
    
    #Get the checking VNFD id and the original VNFD id (stored during the instantiation) from the context.
    origin_vnfd_id = context['vnfd_id']
    checking_vnfd_id = context['vnfd_id_checking']
    
    if origin_vnfd_id != checking_vnfd_id:
        msg = 'The context vnfd_id is different than the vnfd_id specied in the VNF Package from NFVO Catalog: ' + origin_vnfd_id + ' ==> ' + checking_vnfd_id
        MSA_API.task_error(msg, context)
    
    msg = 'The context vnfd_id is matched to the VNF Package from NFVO Catalog.\n original_vnfd_id = ' + origin_vnfd_id + '\ncurrent_vnfd_id = ' + checking_vnfd_id 
    MSA_API.task_success(msg, context)