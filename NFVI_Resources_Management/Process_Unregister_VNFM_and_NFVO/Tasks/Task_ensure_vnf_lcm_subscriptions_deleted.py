from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.subscriptions.VnflcmSubscription import VnflcmSubscription

dev_var = Variables()
context = Variables.task_call(dev_var)

'''
Delete force the vnf indicator subscriptions.
@param subscription_ids 
@param vnflcmSubscription
@param context
@param timeout
'''
def _delete_force_subscriptions_vnflcm(subscription_ids, vnflcmSubscription, context, timeout=60):
    if subscription_ids:
        for index, subscription_id in enumerate(subscription_ids):
            #Call SDK method to force to delete the subscription where type=VNFINDICATOR in the remote server (vnfm).  
            vnflcm_subscription = vnflcmSubscription.delete_subscription_force(subscription_id, timeout)
            # [DEBUG] Store in the context the vnfind_subscription state.
            context['vnflcm_subscription'] = vnflcm_subscription
    else:
        ret = MSA_API.process_content("ENDED","Task skipped: empty vnflcm subscription ids from the workflow context.", context, True)
        print(ret)

if __name__ == "__main__":
    
    #Get is_vnfm_register_only value.
    is_vnfm_register_only = context.get('is_vnfm_register_only')
    
    #Skip task if NFVO was not subscribed to the VNFM.
    if is_vnfm_register_only == True or is_vnfm_register_only == 'True' or is_vnfm_register_only == 'true':
        MSA_API.task_success('Task skipped, N/A.', context)
        
    #Get VNFM ME connection informations.
    vnfm_me_ref = context["vnfm_device"]
    vnfm_me_id = context["vnfm_device"][3:]
    vnfm_ip    = context["vnfm_mano_ip"]
    vnfm_port  = context["vnfm_mano_port"]
    vnfm_username  = context["vnfm_mano_user"]
    vnfm_password  = context["vnfm_mano_pass"]
    #VNFM Keycloak server.
    vnfm_keycloak_server_url = context["vnfm_mano_keycloak_server_url"]
    #VNFM base URL.
    vnfm_base_url  = context["vnfm_mano_base_url"]

    # Init subsrciptions to vnfm object.
    vnflcmSubscription = VnflcmSubscription(vnfm_ip, vnfm_port, vnfm_base_url)
    vnflcmSubscription.set_parameters(vnfm_username, vnfm_password)
    
    #Get Authentication mode ('basic' or 'oauth2').
    vnfm_auth_mode  = context["vnfm_mano_auth_mode"]
    
    if vnfm_auth_mode == 'oauth2' or vnfm_auth_mode == 'oauth_v2':
        vnflcmSubscription.set_parameters(vnfm_username, vnfm_password, vnfm_auth_mode, vnfm_keycloak_server_url)
    else:
        vnflcmSubscription.set_parameters(vnfm_username, vnfm_password)

    # Get remoteSubscriptions from NFVO get 'admin/server/{id}' API resource.
    if not 'vnfm_to_nfvo_subscription' in context:
        MSA_API.task_success("Task skipped: empty 'remoteSubscriptions' object in the context.", context, True)
        
    if isinstance(context.get('vnfm_to_nfvo_subscription'), dict):
        nfvo_to_vnfm_subscription = context['vnfm_to_nfvo_subscription']

    # Vnflcm subscription force delete.
    subscription_ids = vnflcmSubscription.get_subscription_ids_by_type(nfvo_to_vnfm_subscription)
    vnflcm_subscription = _delete_force_subscriptions_vnflcm(subscription_ids, vnflcmSubscription, context, 60)

    if isinstance(vnflcm_subscription, dict):
        MSA_API.task_failed("Failed to force to delete the vnflcm subscriptions.\n", context, True)
    
    MSA_API.task_success("Task execution completed.", context, True)
        