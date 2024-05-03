from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
dev_var.add('managed_entity_monitoring_profils', var_type='String')

context = Variables.task_call(dev_var)

#TODO - Implemenet the logic.

MSA_API.task_success('Task OK', context, True)

