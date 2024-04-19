from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()

context = Variables.task_call(dev_var)

#TODO - Implemenet the logic.

MSA_API.task_ssuccess('Task OK', context, True)
