import requests
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()

dev_var.add('csar_file')

context = Variables.task_call(dev_var)

context['desc_type'] = "NSD"

MSA_API.task_success('DONE: parameters OK', context, True)