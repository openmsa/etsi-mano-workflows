import json
import time
import sys
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device
from msa_sdk import constants
import openstack

from custom.ETSI.NfviVim import NfviVim
from custom.ETSI.VnfLcmSol003 import VnfLcmSol003
from custom.ETSI.VnfPkgSol005 import VnfPkgSol005

#openstack.enable_logging(debug=True, path='/opt/fmc_repository/etsi-mano-workflows/openstack.log', stream=sys.stdout)
'''
Get VIM connection.
'''
def _get_vim_connection_auth(nfvo_device, vim_id, is_user_domain=False, is_user_domain_id_attribute=False):
    #Openstack Authification Connection.
    conn = ''
    
    nfviVim = NfviVim(context["nfvo_mano_ip"], context["nfvo_mano_port"], context['nfvo_mano_base_url'])
    
    auth_mode = context["nfvo_mano_auth_mode"]
    if auth_mode == 'oauth_v2':
        nfviVim.set_parameters(context['nfvo_mano_user'], context['nfvo_mano_pass'], auth_mode, context['nfvo_mano_keycloak_server_url'])
    else:
        nfviVim.set_parameters(context['nfvo_mano_user'], context['nfvo_mano_pass'])
    
    #Get VIM connection info by id.
    vim_list = nfviVim.nfvi_vim_get()
    
    if vim_list:
        for index, vimInfo in enumerate(vim_list.json()):
            if vimInfo.get('vimId') == vim_id:
                
                context.update(vimInfo=vimInfo)
                
                auth_url = vimInfo['interfaceInfo']['endpoint']
                auth_url = auth_url[:-2]
                username = vimInfo['accessInfo']['username']
                password = vimInfo['accessInfo']['password']
                project_id = vimInfo['accessInfo']['projectId']
                user_domain_id = vimInfo['accessInfo']['userDomain']
                #
                project_domain_id = vimInfo['accessInfo']['projectDomain']
                #
                region_name = 'RegionOne'
                compute_api_version = '2'
                identity_interface = 'public'
                
                context.update(auth_url=auth_url)
                context.update(username=username)
                context.update(password=password)
                context.update(project_id=project_id)
                context.update(user_domain_id=user_domain_id)
                context.update(project_domain_id=project_domain_id)
                #
                context.update(region_name=region_name)
                context.update(compute_api_version=compute_api_version)
                context.update(identity_interface=identity_interface)
                
                domain_id = user_domain_id
                domain_id_var_conf_attr = 'USER_DOMAIN_ID'
                if is_user_domain == False:
                    domain_id = project_domain_id
                    domain_id_var_conf_attr = 'PROJECT_DOMAIN_ID'
                
                context.update(domain_id=domain_id)
                context.update(domain_id_var_conf_attr=domain_id_var_conf_attr)
                
                #Get Openstack connection
                auth = dict(auth_url=auth_url, username=username, password=password, project_id=project_id)
                try:
                    if not is_user_domain_id_attribute:
                        auth.update(domain_name=domain_id)
                    else:
                        auth.update(user_domain_id=domain_id)
                    conn = openstack.connection.Connection(region_name=region_name, auth=auth, compute_api_version=compute_api_version, identity_interface=identity_interface, verify=False)
                except:
                    MSA_API.task_error('Failed to authentify to openstack (VIM).')
    return conn


'''
Get external network from VIM tenant.
'''
def _get_vim_external_network(conn):
    external_network = ''
    for network in conn.network.networks():
        if network.get('is_router_external') == True:
            external_network = network.get('name')
    return external_network


'''
Ensure the list of the addresses is available.
'''
def _isinstance_is_list(addresses, conn, timeout = 60, interval=5):
    addr_list = ''
    
    global_timeout = time.time() + timeout
    while True:
        #Get openstack tenant external networks.
        external_network = _get_vim_external_network(conn)
        addr_list = addresses.get(external_network)
        
        if isinstance(addr_list, list) or time.time() > global_timeout:
            break
        time.sleep(interval)

    return addr_list


'''
Get external IP addresse from external network object.
'''
def _get_ip_address_from_network(addresses, conn):
    #Exeternal network list of addresses
    addr_list = _isinstance_is_list(addresses, conn)
    
    for index, address in enumerate(addr_list):
        if address.get('addr'):
            server_ip_addr = address.get('addr')
            return server_ip_addr
            
    return ''

'''
Get management IP address based-on the network name convention.
''' 
def _get_vdu_mgmt_address_convention(server, server_list_address):
    server_ip_addr = ''
    for network_name, iface_list in server_list_address.items():
        #CONVERSION OF THE MANAGEMENT NETWORK NAMING.
        if "mgmt" in network_name.lower() or "management" in network_name.lower():
            for iface in iface_list:
                server_ip_addr = iface.get('addr')
                server_name = server.name
                return {"server_ip_addr": server_ip_addr, "server_name": server_name}
            #MSA_API.task_error('DEBUG: ' + network_name + " iface " + server_ip_addr + "Name: " + server_name, context, True)
    if not server_ip_addr:
        MSA_API.task_error('No management network found as per the naming convention: \nThe key words "mgmt" or "management" should be set as a prefix for the management network name.', context, True)

'''
Get VNFC resource (VDU) instance public IP address.
'''
def _get_vnfc_resource_public_ip_address(nfvo_device, vim_id, server_id, timeout=60, interval=5):
    #Get openstack authenfication
    conn = _get_vim_connection_auth(nfvo_device, vim_id, False)

    #Get VDU (server instance) details.
    servers = {}
    global_timeout = time.time() + timeout
    status = 'BUILD'
    while True and status != 'ACTIVE':
        #Get VDU (server instance) details.
        try:
            servers = conn.compute.servers()
        except:
            servers = conn.compute.servers()
            
        #if servers is not a empty dictionnary.
        if bool(servers) == True or time.time() > global_timeout:
            for server in servers:
                if server.id == server_id:
                    if server.status == 'ACTIVE':
                        status = server.status
                        addresses = server.addresses
                        return _get_vdu_mgmt_address_convention(server, addresses)
        time.sleep(interval)

#----------------------------
def _get_vnfc_resource_ip_addresses(nfvo_device, vim_id, server_id, timeout=60, interval=5):
    
    #Get openstack authenfication
    conn = _get_vim_connection_auth(nfvo_device, vim_id, False)

    #server_ip_addr = ''
    ip_list=[]
        
    #Get VDU (server instance) details.
    servers = {}
    global_timeout = time.time() + timeout
    status = 'BUILD'
    while True and status != 'ACTIVE':
        #Get VDU (server instance) details.
        try:
            servers = conn.compute.servers()
        except:
            conn = _get_vim_connection_auth(nfvo_device, vim_id, True)
            servers = conn.compute.servers()
            
        #if servers is not a empty dictionnary.
        if bool(servers) == True or time.time() > global_timeout:
            for server in servers:
                if server.id == server_id:
                    if server.status == 'ACTIVE':
                        addresses = server.addresses
                        for network_name, iface_list in addresses.items():
                            for ip_addr in iface_list:
                                ip_a=ip_addr.get('addr')
                                ip_list.append(ip_a)
            break
        time.sleep(interval)
            
    return ip_list
#----------------------------


'''
Function to check if the VDU has already is corresponding managed entity created.
'''
def _is_vdu_managed_entity_exists(vnf_me_list, vnfResourceId, context):
    list_debug_me = []
    context.update(list_debug_me=list_debug_me)
    for vdu_me in vnf_me_list:
        me_d = {vnfResourceId:vdu_me.get('vnf_resource_id')}
        list_debug_me.append(me_d)
        #if 'vnf_resource_id' in vdu_me and 'device_ext_ref' in vdu_me:
        if vnfResourceId == vdu_me.get('vnf_resource_id'):
            #MSA_API.task_error('isvdu_me = True', context, True)
            context.update(vnf_me_list=vnf_me_list)
            return True
    return False


######################################################################################################
#
# ****************************************** MAIN ***************************************************
#
######################################################################################################

dev_var = Variables()
context = Variables.task_call(dev_var)

subtenant_ext_ref = context['UBIQUBEID']
vnf_service_instance_ref = context.get('SERVICEINSTANCEREFERENCE')

if __name__ == "__main__":

    if "is_third_party_vnfm" in context:
            is_third_party_vnfm = context.get('is_third_party_vnfm')
            if is_third_party_vnfm == 'true':
                MSA_API.task_success('Skip for 3rd party VNFM.', context)
    
    ## Get list of VNFC vdu.
    vnfLcm = VnfLcmSol003(context["vnfm_mano_ip"], context["vnfm_mano_port"], context['vnfm_mano_base_url'])
    
    auth_mode = context["vnfm_mano_auth_mode"]
    if auth_mode == 'oauth_v2':
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'], auth_mode, context['vnfm_mano_keycloak_server_url'])
    else:
        vnfLcm.set_parameters(context['vnfm_mano_user'], context['vnfm_mano_pass'])
    
    #waiting
    #time.sleep(120)
    r = vnfLcm.vnf_lcm_get_vnf_instance_details(context["vnf_instance_id"])

    #Check request status.
    r_details = ''
    status = vnfLcm.state
    if status == 'ENDED':
        # Get the operation state from the operation accurancies response.
        response = r.json()
        r_details = 'Successful!'
    else:
        r_details = str(r.json().get('detail'))
        MSA_API.task_error('Failed to get VNF Instance details: \n"' + r_details + '"', context, True)
    
    context.update(vnf_instance_details=r.json())
    
    vnfResourcesList = r.json()["instantiatedVnfInfo"]["vnfcResourceInfo"]
    #vnfName = context['vnf_instance_name']
#---------------------------------------------
    nfvo_device_ref = context.get('nfvo_device')
#---------------------------------------------
    context.update(vnfResourcesList=vnfResourcesList)
    
    #VNF Managed Entities.
    vnf_me_list = list()
    
    #For each VNFC-VDU create corresponding ME's.
    for index, vnfR in enumerate(vnfResourcesList):
        #openstack server instance ID.
        vnfResourceId = vnfR["computeResource"]["resourceId"]
        #Get VIM (openstack) id from the VNF Instance details.
        vim_connection_id = vnfR["computeResource"]['vimConnectionId']

        #Save vim_connection_id in the context.
        context.update(vim_connection_id=vim_connection_id)
        
        #Get openstack connection.
        conx = _get_vim_connection_auth(nfvo_device_ref, vim_connection_id, False)

        #Get server (VDU) instance id from openstack tenant.
        try:
            serv = conx.compute.get_server(vnfResourceId)
        except:
            conx = _get_vim_connection_auth(nfvo_device_ref, vim_connection_id, False, True)
            try:
                serv = conx.compute.get_server(vnfResourceId)
            except:
                MSA_API.task_error('Failed to get authentified to the openstack project.')
        #Store server image id
        img=serv.image.id
        #Store server image name.
        img_name=conx.image.get_image(img).name
#-----------------------------------------------------------
        #Customer ID
        customer_id = subtenant_ext_ref[4:]

        #ME as Juniper vSRX.
        if "vsrx" in img_name.lower():
            manufacturer_id='18'
            model_id='121'
        else:
            #ME as Monitoring Generic.
            manufacturer_id='770000'
            model_id='770010'
        nfvo_device_ref = context.get('nfvo_device')
        
        management_address = ''
        server_name = ''
        
        try:
            #Get the management API.
            re = _get_vnfc_resource_public_ip_address(nfvo_device_ref, vim_connection_id, vnfResourceId, 500)
            management_address = re.get('server_ip_addr')
            server_name = re.get('server_name')
        except TypeError:
            MSA_API.task_error('Failed to get details about the VDU instance from openstack, where id='+vnfResourceId, context, True)
        except AttributeError:
            MSA_API.task_error('Failed to get management IP Address and name of the VDU instance from openstack, where id='+vnfResourceId, context, True)
#---------------------------------------
        try:
            addr_list = _get_vnfc_resource_ip_addresses(nfvo_device_ref, vim_connection_id, vnfResourceId, 500)
        except TypeError:
            MSA_API.task_error('Failed to get details about the VDU instance from openstack, where id='+vnfResourceId, context, True)
#---------------------------------------
        
        if not management_address:
            management_address = '1.1.1.1'
        
        #Kubernetes adaptor does not use the password and login of ME.
        password = 'ipcore123'
        management_port='22'
        name = server_name

        #check if the vnfc-vdu corresponding ME is already created.
        is_vdu_me = False
        if context.get('vnf_me_list'):
            vnf_me_list = context.get('vnf_me_list')
            is_vdu_me = _is_vdu_managed_entity_exists(vnf_me_list, vnfResourceId, context)
        context.update(is_vdu_me=is_vdu_me)

        #Create Device
        if is_vdu_me == False :
            device = Device(customer_id=customer_id, name=name, manufacturer_id=manufacturer_id, model_id=model_id, login='ipcore', password=password, password_admin=password, management_address=management_address, management_port=management_port, device_external="", log_enabled=True, log_more_enabled=True, mail_alerting=False, reporting=True, snmp_community='ubiqube', device_id="")
            response = device.create()
            context.update(device=response)
            #get device external reference
            device_ext_ref = response.get('externalReference')
            
            #Add device_ext_ref to the VNF ME list.
            vnfc_dict = dict(vnf_resource_id=vnfResourceId, device_ext_ref=device_ext_ref)
            vnf_me_list.append(vnfc_dict)
            
            #get device external reference
            device_id = response.get('id')
            context.update(vnf_me_id=device_id)

            #add ns_service_instance_ref as VNF ME config variable.
            if 'ns_service_instance_ref' in context:
                ns_service_instance_ref = context.get('ns_service_instance_ref')
                if ns_service_instance_ref:
                    device.create_configuration_variable('nslcm_wf_service_instance_ref', ns_service_instance_ref)
                    
            #Create VNF LCM service instance REF config variable:
            device.create_configuration_variable('vnflcm_wf_service_instance_ref', vnf_service_instance_ref)

            #Create vnfc openstack instance id config variable.
            device.create_configuration_variable('openstack_vnfc_instance_id', vnfResourceId)

            #Create vnf instance config variable.
            device.create_configuration_variable('vnf_instance_name', context.get('vnf_instance_name'))

#--------------------------------------------------------------
            uri=''
            #add config variables, attach suitable config templates and do initial provisioning
            if "vsrx" in img_name.lower():
                device.create_configuration_variable('HOST_NAME', img_name+str(device_id))
                if len(addr_list) > 1:
                    if addr_list[1]:
                        device.create_configuration_variable('SECOND_INT_IP', addr_list[1])
                    if len(addr_list) > 2:
                        if addr_list[2]:
                            device.create_configuration_variable('THIRD_INT_IP', addr_list[2])
                #using the device id for priority as it always increases
                #hence any time the first VNF created will have a low numeric vlaue for priority
                priority=device_id%250
                device.create_configuration_variable('PRIORITY', priority)
                uri = {"uri": "Configuration/demo/vsrx_day0_standalone"}
                uris = []
                uris.append(uri)
                device.attach_files(uris, 'PRE_CONFIG')
                #sleep for some time so that the VNF is reachable from MSA
                time.sleep(30)
                device.initial_provisioning()
                time.sleep(10)
#--------------------------------------------------------------
    #Store vnf_me_list in the context.
    context.update(vnf_me_list=vnf_me_list)

    MSA_API.task_success('The VNF managed entities are created.', context)
