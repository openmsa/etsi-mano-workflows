from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
dev_var.add('vnfm_managed_entity', var_type='Device')
dev_var.add('vnf_instance_id', var_type='OBMFRef')

context = Variables.task_call(dev_var)

#TODO - Implemenet the logic.

MSA_API.task_ssuccess('Task OK', context, True)

