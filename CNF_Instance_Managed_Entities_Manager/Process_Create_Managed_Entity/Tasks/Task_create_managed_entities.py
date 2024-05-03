from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
import json

def __init_context():
    dev_var = Variables()
    dev_var.add('managed_entity_manufacturer', var_type='String')
    dev_var.add('managed_entity_model', var_type='String')
    dev_var.add('managed_entity_ip_address', var_type='String')
    dev_var.add('managed_entity_login', var_type='String')
    dev_var.add('managed_entity_password', var_type='String')
    dev_var.add('managed_entity_is_log_enable', var_type='String')
    context = Variables.task_call(dev_var)
    
    return context

def __create_managed_entity(context):
    
    #Get managed entity details.
    msa_subtenant_reference = context.get('UBIQUBEID')[4:] #Customer reference.
    managed_entity_name = "Test_name"
    managed_entity_manufacturer_id = context.get('managed_entity_manufacturer')
    managed_entity_model_id = context.get('managed_entity_model')
    managed_entity_management_address = context.get('managed_entity_ip_address')
    managed_entity_login = context.get('managed_entity_login')
    managed_entity_password = context.get('managed_entity_password')
    managed_entity_is_log_enable_as_str = context.get('managed_entity_is_log_enable')
    
    managed_entity_is_log_enable = __convert_string_to_bool(managed_entity_is_log_enable_as_str)

    #Create managed entity.
    device = Device(customer_id=msa_subtenant_reference,
                    name=managed_entity_name,
                    manufacturer_id=managed_entity_manufacturer_id,
                    model_id=managed_entity_model_id,
                    management_address=managed_entity_management_address,
                    login=managed_entity_login,
                    password=managed_entity_password,
                    password_admin="",
                    log_enabled=managed_entity_is_log_enable
                    )
    managed_entity_creation_response = device.create()
    
    return managed_entity_creation_response

def __check_satus(managed_entity_creation_response):
    if 'wo_status' in managed_entity_creation_response:
        MSA_API.task_error(json.dumps(managed_entity_creation_response), context, True)
    else:
        pass

def __convert_string_to_bool(string_to_convert):
    if string_to_convert == "True":
        bool_value = True
    else:
        bool_value = False
    return bool_value

def __get_external_reference(managed_entity_creation_response):
    if not 'externalReference' in managed_entity_creation_response:
        MSA_API.task_error("No managed entity externalReference found.")
    return managed_entity_creation_response.get('externalReference')

if __name__ == '__main__':

    #Set the context variables.
    context = __init_context()
    
    #Create managed entity.
    managed_entity_creation_response = __create_managed_entity(context)
    
    #Check operation status.
    __check_satus(managed_entity_creation_response)
    
    #Get managed entity reference.
    managed_entity_reference = __get_external_reference(managed_entity_creation_response)
    
    #Save managed entity external reference in the context.
    context['managed_entity_external_reference'] = managed_entity_reference
    
    #Display task success messsage.
    MSA_API.task_success('Managed entity created, reference = ' + managed_entity_reference, context, True)

