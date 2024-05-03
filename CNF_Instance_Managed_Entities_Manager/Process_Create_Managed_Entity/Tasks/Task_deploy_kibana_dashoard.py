import json
import time
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.orchestration import Orchestration
from msa_sdk.util import constants

def __init_context():
    dev_var = Variables()
    dev_var.add('dashboard_name', var_type='String')
    dev_var.add('dashboard_template_id', var_type='String')
    dev_var.add('dashboard_type', var_type='String')
    context = Variables.task_call(dev_var)
    
    return context

def __init_orchestration(context):
    ubiqube_id = context['UBIQUBEID']
    return Orchestration(ubiqube_id) 

def __check_process_execution_status(orchestration):
    orchestration_content = json.loads(orchestration.content)
    status = orchestration_content.get('status').get('status')
    return status

def __get_workflow_process_instance_id(orchestration):
    orchestration_content = json.loads(orchestration.content)
    
    context["orchestration_content"] = orchestration_content
    
    status = __check_process_execution_status(orchestration)
    if status == "FAIL":
        MSA_API.task_error('Workflow service execution status=' + status, context, True)
        
    if not 'processId' in orchestration_content:
        raise BaseException("Orchestration content does not contain the workflow process_id field.")
    process_id = orchestration_content.get('processId').get('id')
    
    return process_id

def __get_worflow_process_instance_status(orchestration, process_id, timeout=600, interval=5):
    orchestration_content = {}
    global_timeout = time.time() + timeout
    while True:
        #get service instance execution status.
        orchestration.get_process_instance(process_id)
        status = __check_process_execution_status(orchestration)
        if status != constants.RUNNING or time.time() > global_timeout:
            break
        time.sleep(interval)

    return orchestration_content

def __deploy_kibana_dashboard(context, orchestration):
    SERVICE_NAME = "Process/Analytics/Kibana/kibana_dashboard"
    PROCESS_NAME = "Process/Analytics/Kibana/Process_Create_Report_Dashboard"
    
    dashboard_name = context.get('dashboard_name')
    dashboard_template_id = context.get('dashboard_template_id')
    dashboard_type = context.get('dashboard_type')
    
    remote_worklow_inputs = dict()
    remote_worklow_inputs['dashboardName'] = dashboard_name
    remote_worklow_inputs['template_id'] = dashboard_template_id
    remote_worklow_inputs['type'] = dashboard_type
    
    orchestration.execute_service(SERVICE_NAME, PROCESS_NAME, remote_worklow_inputs)
    
    process_id = __get_workflow_process_instance_id(orchestration)
    
    __get_worflow_process_instance_status(orchestration, process_id) 


if __name__ == "__main__":
    
    #Init context variables.
    context = __init_context()
    
    #Initiate orchestraction object.
    orchestration = __init_orchestration(context)
    
    #Deploy kibana dashboard.
    __deploy_kibana_dashboard(context, orchestration)
    
    #Display message.
    MSA_API.task_success('Task OK', context, True)
    

