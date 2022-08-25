import os
import json
import shutil
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants
from custom.ETSI.DescriptorGraphGeneration import DescriptorGraphGeneration

dev_var = Variables()
dev_var.add('vnfd_graph', var_type='String')
context = Variables.task_call(dev_var)

if __name__ == "__main__":
    
    graph_link = context.get('vnfd_graph')
    
    if os.path.exists(graph_link):
        os.remove(graph_link)
    
    if not os.path.exists(graph_link):
        context.update(vnfd_graph='')
    ret = MSA_API.task_success('VNFD graph is deleted.', context, True)