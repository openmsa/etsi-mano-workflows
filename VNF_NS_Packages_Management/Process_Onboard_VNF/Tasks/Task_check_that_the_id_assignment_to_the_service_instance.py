from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)
    
    #VNF Package
    if 'vnf_package_id_initial' in context and 'vnf_package_id' in context:
        init_vnf_package_id = context.get('vnf_package_id_initial')
        vnf_package_id = context.get('vnf_package_id')
        if init_vnf_package_id != vnf_package_id:
            #Override the vnf_package_id by the its initial value generated during the package creation.
            context.update(vnf_package_id=init_vnf_package_id)
            MSA_API.task_error('This workflow service instance is only for managing the VNF package with id=' + init_vnf_package_id, context, True)
    #NS Package
    elif 'ns_package_id_initial' in context and 'ns_package_id' in context:
        init_ns_package_id = context.get('vnf_package_id_initial')
        ns_package_id = context.get('vnf_package_id')
        if init_ns_package_id != ns_package_id:
            MSA_API.task_error('This workflow service instance is only for managing the NS package with id=' + init_ns_package_id, context, True)

    MSA_API.task_success('The checking is done successfully.', context, True)
