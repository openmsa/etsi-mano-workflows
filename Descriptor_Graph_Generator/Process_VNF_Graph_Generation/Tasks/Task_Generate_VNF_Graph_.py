import os
import json
import shutil
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk import constants
from custom.ETSI.DescriptorGraphGeneration import DescriptorGraphGeneration

dev_var = Variables()
dev_var.add('vnfd_id', var_type='String')
dev_var.add('vnfd_graph', var_type='String')
context = Variables.task_call(dev_var)

SUBTENANT = context.get('UBIQUBEID')
DATAFILES_PATH = '/opt/fmc_repository/Datafiles/NFV_GRAPHS/' + SUBTENANT + '/VNFD/' 
GRAPH_IMAGE_EXTENSION = '.png'

if __name__ == "__main__":
    
    vnfGraph = DescriptorGraphGeneration(context["mano_ip"], context["mano_port"])
    
    auth_mode = context['auth_mode']
    if auth_mode == 'oauth2' or auth_mode == 'oauth_v2':
        vnfGraph.set_parameters(context['mano_user'], context['mano_pass'], auth_mode, context['keycloak_server_url'], 'image/png')
    else:
        vnfGraph.set_parameters(context['mano_user'], context['mano_pass'])
    
    vnfd_id = context.get("vnfd_id")
    #
    graph_link = DATAFILES_PATH + vnfd_id + GRAPH_IMAGE_EXTENSION
    context.update(vnfd_graph=graph_link)
    
    r = vnfGraph.vnf_graph_tolopology_generation(vnfd_id)
    
    ## Write response body in the repository data.
    try:
        r_status = str(r.json().get('status'))
        if r_status != "200":
            r_details = r.json().get('detail')
            MSA_API.task_error('Failed: HTTP_CODE ' + r_status + ' - ' + r_details , context, True)
    except:
        pass
    
    #Create directories if not exists.
    if not os.path.exists(DATAFILES_PATH):
        os.makedirs(DATAFILES_PATH)
    
    #Store descriptor graph image in the Datafiles.
    file = open(graph_link, "wb")
    file.write(r.content)
    file.close()
    
    vnfd_id = context.get('vnfd_id')
        
    ret = MSA_API.task_success('VNFD graph is generated , click-on the link to download the graph.', context, True)