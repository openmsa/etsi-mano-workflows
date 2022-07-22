import requests
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()

dev_var.add('package_name')
dev_var.add('tosca_files.0.name')
dev_var.add('tosca_files.0.content')

context = Variables.task_call(dev_var)


MSA_API.task_success('DONE: parameters OK', context, True)
