from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

def __init_context():
    dev_var = Variables()
    context = Variables.task_call(dev_var)
    return context

def __get_managed_entity_external_reference_from(context):
    if not 'managed_entity_external_reference' in context:
        MSA_API.task_error("No managed entity externalReference found the context.")
        
    managed_entity_reference = context.get('managed_entity_external_reference')
    return managed_entity_reference

def __do_initial_provision_to_managed_entity(external_reference):
    managed_entity_id = external_reference[3:]
    managed_entity = Device(device_id=managed_entity_id)
    try:
        managed_entity.initial_provisioning()
    except:
        pass

if __name__ == '__main__':
    
    #Init the context.
    context = __init_context()
    
    #Get the managed entity externalReference.
    managed_entity_reference = __get_managed_entity_external_reference_from(context)
    
    #Delete managed entity.
    __do_initial_provision_to_managed_entity(managed_entity_reference)
    
    #Display task success message.
    MSA_API.task_success('Task OK', context, True)

