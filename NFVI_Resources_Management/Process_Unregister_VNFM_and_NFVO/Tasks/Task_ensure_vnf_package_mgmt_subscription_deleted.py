from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.subscriptions.VnfpkgmSubscription import VnfpkgmSubscription

dev_var = Variables()
context = Variables.task_call(dev_var)

'''
Delete force the vnf package management subscriptions.
@param subscription_ids 
@param context
@param timeout
'''
def _delete_force_subscriptions_vnfpkgm(subscription_ids, vnfpkgmSubscription, context, timeout=60):
    if subscription_ids:
        for index, subscription_id in enumerate(subscription_ids):
            #Call SDK method to force to delete the subscription where type=VNFINDICATOR in the remote server (vnfm).  
            vnfpkgm_subscription = vnfpkgmSubscription.delete_subscription_force(subscription_id, timeout)
            # [DEBUG] Store in the context the vnfind_subscription state.
            context['vnfpkgm_subscription'] = vnfpkgm_subscription
    else:
        ret = MSA_API.process_content("WARNING","Task skipped: empty vnf package mgmt subscription ids from the workflow context.", context, True)
        print(ret)


if __name__ == "__main__":
    
    #Get is_vnfm_register_only value.
    is_vnfm_register_only = context.get('is_vnfm_register_only')
    
    #Skip task if NFVO was not subscribed to the VNFM.
    if is_vnfm_register_only == True or is_vnfm_register_only == 'True' or is_vnfm_register_only == 'true':
        MSA_API.task_success('Task skipped, N/A.', context)
    
    #Get VNFM ME connection informations.
    nfvo_me_ref = context["nfvo_device"]
    nfvo_me_id = context["nfvo_device"][3:]
    nfvo_ip    = context["nfvo_mano_ip"]
    nfvo_port  = context["nfvo_mano_port"]
    nfvo_username  = context["nfvo_mano_user"]
    nfvo_password  = context["nfvo_mano_pass"]
    #NFVO Keycloak server.
    nfvo_keycloak_server_url = context["nfvo_mano_keycloak_server_url"]
    #NFVO base URL.
    nfvo_base_url  = context["nfvo_mano_base_url"]

    # Init subsrciptions to vnfm object.
    vnfpkgmSubscription = VnfpkgmSubscription(nfvo_ip, nfvo_port, nfvo_base_url)
    vnfpkgmSubscription.set_parameters(nfvo_username, nfvo_password)
    
    #Get Authentication mode ('basic' or 'oauth2').
    nfvo_auth_mode  = context["nfvo_mano_auth_mode"]
    
    if nfvo_auth_mode == 'oauth2' or nfvo_auth_mode == 'oauth_v2':            
        vnfpkgmSubscription.set_parameters(nfvo_username, nfvo_password, nfvo_auth_mode, nfvo_keycloak_server_url)
    else:
        vnfpkgmSubscription.set_parameters(nfvo_username, nfvo_password)
    
    # Get VNFM Subscription to NFVO (fetched via 'admin/server/{id}' API resource).
    if not 'nfvo_to_vnfm_subscription' in context:
        MSA_API.task_success("Task skipped: empty nfvo subscription object in the context.", context, True)
        
    if isinstance(context.get('nfvo_to_vnfm_subscription'), dict):
        vnfm_to_nfvo_subscription = context['nfvo_to_vnfm_subscription']
    
    # Vnf indicator subscription force delete.
    subscription_ids = vnfpkgmSubscription.get_subscription_ids_by_type(vnfm_to_nfvo_subscription)
    vnfpkgm_subscription = _delete_force_subscriptions_vnfpkgm(subscription_ids, vnfpkgmSubscription, context, 60)

    if isinstance(vnfpkgm_subscription, dict):
        MSA_API.task_failed("Failed to force to delete the vnfpkgm subscriptions.\n", context, True)    

    MSA_API.task_success("Task execution completed.", context, True)