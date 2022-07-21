import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

'''
This function allows to build the NS Update request body if updateType = "ADD_VNF".
'''
def _addVnfInstanceId_content_builder(addVnfInstanceIds):
    content = list()
    if isinstance(addVnfInstanceIds, list):
        return addVnfInstanceIds
    elif isinstance(addVnfInstanceIds, dict):
        for index in addVnfInstanceIds:
            vnfi_id = addVnfInstanceIds.get(index)
            content.append(vnfi_id)
            
    return content

'''
This function allows to build the NS Update request body if updateType = "REMOVE_VNF".
'''
def _removeVnfInstanceId_content_builder(removeVnfInstanceIds):
    content = list()
    if isinstance(removeVnfInstanceIds, list):
        for vnfiId_dict in removeVnfInstanceIds:
            vnfi_id = vnfiId_dict.get('vnfInstanceId')
            content.append(vnfi_id)
    elif isinstance(removeVnfInstanceIds, dict):
        for index in removeVnfInstanceIds:
            vnfi_id = removeVnfInstanceIds.get(index).get('vnfInstanceId')
            content.append(vnfi_id)
            
    return content

'''
This function allows to build the NS Update request body if updateType = "ADD_VNFFG".
'''
def _addVnffgId_content_builder(addVnffgIds):
    content = list()
    if isinstance(addVnffgIds, list):
        return addVnffgIds
    elif isinstance(addVnffgIds, dict):
        for index in addVnffgIds:
            vnffg_id = addVnffgIds.get(index)
            content.append(vnffg_id)
            
    return content

'''
This function allows to build the NS Update request body if updateType = "REMOVE_VNFFG".
'''
def _removeVnffgId_content_builder(removeVnffgIds):
    content = list()
    if isinstance(removeVnffgIds, list):
        for vnffg_id_dict in removeVnffgIds:
            vnffg_id = vnffg_id_dict.get('vnffgId')
            content.append(vnffg_id)
    elif isinstance(removeVnffgIds, dict):
        for index in removeVnffgIds:
            vnffg_id = removeVnffgIds.get(index).get('vnffgId')
            content.append(vnffg_id)
        
    return content

'''
This function allows to build the NS Update request body if updateType = "UPDATE_VNFFG".
'''
def _updateVnffg_content_builder(updateVnffgs):
    #TODO: handle VNFFG update content from WF service instance input.
    content = list()
    if isinstance(updateVnffgs, list):
        for vnffg in updateVnffgs:
            nfp_content = json.loads(vnffg.get('nfp'))
            vnffg.update(nfp=nfp_content)
            content.append(vnffg)
    elif isinstance(updateVnffgs, dict):
        for index in updateVnffgs:
            vnffg = updateVnffgs.get(index)
            nfp_content = json.loads(vnffg.get('nfp'))
            vnffg.update(nfp=nfp_content)
            content.append(vnffg)
            
    return content

#MAIN code.
if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add('vnfm_device', var_type='Device')
    dev_var.add('updateType', var_type='String')
    #It shall be present only if updateType = "ADD_VNF".
    dev_var.add('addVnfIstance.0.vnfInstanceId', var_type='String')
    dev_var.add('addVnfIstance.0.vnfProfileId', var_type='String')
    #It shall be present only if updateType = "REMOVE_VNF.
    dev_var.add('removeVnfInstanceId.0.vnfInstanceId', var_type='String')
    #It shall be present only if updateType = "ADD_VNFFG".
    dev_var.add('addVnffg.0.targetNsInstanceId', var_type='String')
    dev_var.add('addVnffg.0.vnffgName', var_type='String')
    dev_var.add('addVnffg.0.description', var_type='String')
    #It shall be present only if updateType = "REMOVE_VNFFG".
    dev_var.add('removeVnffgId.0.vnffgId', var_type='String')
    #It shall be present only if updateType = "UPDATE_VNFFG".
    dev_var.add('updateVnffg.0.vnffgInfoId', var_type='String')
    dev_var.add('updateVnffg.0.nfp', var_type='String')
    dev_var.add('updateVnffg.0.nfpInfoId', var_type='String')
    context = Variables.task_call(dev_var)
    
    #Get the update type.
    updateType = context.get("updateType")
    
    #Init content variable.
    content = []
    
    #Prepare the NS update request body according to the updateType value.
    if updateType == 'ADD_VNF':
        addVnfInstanceIds = context.get('addVnfIstance')
        if not addVnfInstanceIds:
            MSA_API.task_error('FAILED, ADD_VNF input is empty.', context, True)
        content = _addVnfInstanceId_content_builder(addVnfInstanceIds)
        
    elif updateType == 'REMOVE_VNF':
        removeVnfInstanceIds = context.get('removeVnfInstanceId')
        if not removeVnfInstanceIds:
            MSA_API.task_error('FAILED, REMOVE_VNF input is empty.', context, True)
        content = _removeVnfInstanceId_content_builder(removeVnfInstanceIds)
    
    elif updateType == 'ADD_VNFFG':
        addVnffgIds = context.get('addVnffg')
        if not addVnffgIds:
            MSA_API.task_error('FAILED, ADD_VNFFG input is empty.', context, True)
        content = _addVnffgId_content_builder(addVnffgIds)
    
    elif updateType == 'REMOVE_VNFFG':
        removeVnffgIds = context.get('removeVnffgId')
        if not removeVnffgIds:
            MSA_API.task_error('FAILED, REMOVE_VNFFG input is empty.', context, True)
        content = _removeVnffgId_content_builder(removeVnffgIds)
    
    elif updateType == 'UPDATE_VNFFG':
        updateVnffgs = context.get('updateVnffg')
        if not updateVnffgs:
            MSA_API.task_error('FAILED, UPDATE_VNFFG input is empty.', context, True)
        content = _updateVnffg_content_builder(updateVnffgs)
    else:
        MSA_API.task_error('NS updateType is required.', context, True)
    
    #Insert NS Update request body content in the context.
    context.update(content=content)
    
    MSA_API.task_success('NS Update request body is ready!.', context, True)