import json
import uuid
import os
import errno
import sys
from msa_sdk import constants
from msa_sdk.order import Order
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('vnfd_name', var_type='String')
dev_var.add('vnfd_contents', var_type='String')
context = Variables.task_call(dev_var)

#filename is created based-on the device external reference
uuid_gen = str(uuid.uuid4())
if 'uuid_gen' in context:
    uuid_gen = context.get('uuid_gen')

vnfd_name = ''
if not 'vnfd_name_uuid' in context:
    # if the uuid_gen exists in the context do not create a new one. This allow to update the existing NSD.
    vnfd_name = ''
    name = context.get('vnfd_name')
    if name:
        vnfd_name = name + '_' + uuid_gen

    #Store vnfd_name_uuid in context.
    context.update(vnfd_name_uuid=vnfd_name)
else:
    vnfd_name = context.get('vnfd_name_uuid')

vnfd_sol0001_schema = 'etsi_nfv_sol001_vnfd_types.yaml'
filename = '/opt/fmc_repository/Datafiles/NFV/VNFD/' + vnfd_name + '/Definitions/' + vnfd_sol0001_schema

#vnfd_sol0001_schema content

etsi_nfv_sol001_vnfd_types = """
tosca_definitions_version: tosca_simple_yaml_1_3
description: ETSI NFV SOL 001 vnfd types definitions version 3.5.1
metadata:
  template_name: etsi_nfv_sol001_vnfd_types
  template_author: ETSI_NFV
  template_version: 3.5.1
imports:
   - https://forge.etsi.org/rep/nfv/SOL001/raw/v3.5.1/etsi_nfv_sol001_common_types.yaml
# editor's note: During the development of the SOL001ed351 GS, to enable this file to be verified by a TOSCA parser, the imports statement has to be replaced with a reference to a local copy of the common definitions YAML file
data_types:
  tosca.datatypes.nfv.VirtualNetworkInterfaceRequirements:
   derived_from: tosca.datatypes.Root
   description: Describes requirements on a virtual network interface
   properties:
     name:
       type: string
       description: Provides a human readable name for the requirement.
       required: false
     description:
       type: string
       description: Provides a human readable description of the requirement.
       required: false
     support_mandatory:
       type: boolean
       description: Indicates whether fulfilling the constraint is mandatory (TRUE) for successful operation or desirable (FALSE).
       required: true
     network_interface_requirements:
       type: map
       description: The network interface requirements. A map of strings that contain a set of key-value pairs that describes the hardware platform specific  network interface deployment requirements.
       required: true
       entry_schema:
         type: string
     nic_io_requirements:
       type: tosca.datatypes.nfv.LogicalNodeData
       description: references (couples) the CP with any logical node I/O requirements (for network devices) that may have been created. Linking these attributes is necessary so that so that I/O requirements that need to be articulated at the logical node level can be associated with the network interface requirements associated with the CP.
       required: false
  tosca.datatypes.nfv.RequestedAdditionalCapability:
   derived_from: tosca.datatypes.Root
   description: describes requested additional capability for a particular VDU
   properties:
     requested_additional_capability_name:
       type: string
       description: Identifies a requested additional capability for the VDU.
       required: true
     support_mandatory:
       type: boolean
       description: Indicates whether the requested additional capability is mandatory for successful operation.
       required: true
     min_requested_additional_capability_version:
       type: string
       description: Identifies the minimum version of the requested additional capability.
       required: false
     preferred_requested_additional_capability_version:
       type: string
       description: Identifies the preferred version of the requested additional capability.
       required: false
     target_performance_parameters:
       type: map
       description: Identifies specific attributes, dependent on the requested additional capability type.
       required: true
       entry_schema:
         type: string
  tosca.datatypes.nfv.VirtualMemory:
     derived_from: tosca.datatypes.Root
     description: supports the specification of requirements related to virtual memory of a virtual compute resource
     properties:
       virtual_mem_size:
         type: scalar-unit.size
         description: Amount of virtual memory.
         required: true
       virtual_mem_oversubscription_policy:
         type: string
         description: The memory core oversubscription policy in terms of virtual memory to physical memory on the platform.
         required: false
       vdu_mem_requirements:
         type: map
         description: The hardware platform specific VDU memory requirements. A map of strings that contains a set of key-value pairs that describes hardware platform specific VDU memory requirements.
         required: false
         entry_schema:
           type: string
       numa_enabled:
         type: boolean
         description: It specifies the memory allocation to be cognisant of the relevant process/core allocation.
         required: true
         default: false
  tosca.datatypes.nfv.VirtualCpu:
   derived_from: tosca.datatypes.Root
   description: Supports the specification of requirements related to virtual CPU(s) of a virtual compute resource
   properties:
     cpu_architecture:
       type: string
       description: CPU architecture type. Examples are x86, ARM
       required: false
     num_virtual_cpu:
       type: integer
       description: Number of virtual CPUs
       required: true
       constraints:
         - greater_than: 0
     virtual_cpu_clock:
       type: scalar-unit.frequency
       description: Minimum virtual CPU clock rate
       required: false
     virtual_cpu_oversubscription_policy:
       type: string
       description: CPU core oversubscription policy e.g. the relation of virtual CPU cores to physical CPU cores/threads.
       required: false
     vdu_cpu_requirements:
       type: map
       description: The hardware platform specific VDU CPU requirements. A map of strings that contains a set of key-value pairs describing VDU CPU specific hardware platform requirements.
       required: false
       entry_schema:
         type: string
     virtual_cpu_pinning:
       type: tosca.datatypes.nfv.VirtualCpuPinning
       description: The virtual CPU pinning configuration for the virtualised compute resource.
       required: false
  tosca.datatypes.nfv.VirtualCpuPinning:
   derived_from: tosca.datatypes.Root
   description: Supports the specification of requirements related to the virtual CPU pinning configuration of a virtual compute resource
   properties:
     virtual_cpu_pinning_policy:
       type: string
       description: Indicates the policy for CPU pinning. The policy can take values of "static" or "dynamic". In case of "dynamic" the allocation of virtual CPU cores to logical CPU cores is decided by the VIM. (e.g. SMT (Simultaneous Multi-Threading) requirements). In case of "static" the allocation is requested to be according to the virtual_cpu_pinning_rule.
       required: false
       constraints:
         - valid_values: [ static, dynamic ]
     virtual_cpu_pinning_rule:
       type: list
       description: Provides the list of rules for allocating virtual CPU cores to logical  CPU cores/threads
       required: false
       entry_schema:
         type: string
  tosca.datatypes.nfv.VnfcConfigurableProperties:
   derived_from: tosca.datatypes.Root
   description: Defines the configurable properties of a VNFC
   #properties:
     # additional_vnfc_configurable_properties:
     #   type: tosca.datatypes.nfv.VnfcAdditionalConfigurableProperties
     #   description: Describes additional configuration for VNFC that can be modified using the ModifyVnfInfo operation
     #   required: false
     # derived types are expected to introduce
     # additional_vnfc_configurable_properties with its type derived from
     # tosca.datatypes.nfv.VnfcAdditionalConfigurableProperties
  tosca.datatypes.nfv.VnfcAdditionalConfigurableProperties:
   derived_from: tosca.datatypes.Root
   description: VnfcAdditionalConfigurableProperties type is an empty base type for deriving data types for describing additional configurable properties for a given VNFC.
  tosca.datatypes.nfv.VduProfile:
   derived_from: tosca.datatypes.Root
   description: describes additional instantiation data for a given Vdu.Compute used in a specific deployment flavour.
   properties:
     min_number_of_instances:
       type: integer
       description: Minimum number of instances of the VNFC based on this Vdu.Compute that is permitted to exist for a particular VNF deployment flavour.
       required: true
       constraints:
         - greater_or_equal: 0
     max_number_of_instances:
       type: integer
       description: Maximum number of instances of the VNFC based on this Vdu.Compute that is permitted to exist for a particular VNF deployment flavour.
       required: true
       constraints:
         - greater_or_equal: 0
  tosca.datatypes.nfv.VlProfile:
   derived_from: tosca.datatypes.Root
   description: Describes additional instantiation data for a given VL used in a specific VNF deployment flavour.
   properties:
     max_bitrate_requirements:
       type: tosca.datatypes.nfv.LinkBitrateRequirements
       description: Specifies the maximum bitrate requirements for a VL instantiated according to this profile.
       required: true
     min_bitrate_requirements:
       type: tosca.datatypes.nfv.LinkBitrateRequirements
       description: Specifies the minimum bitrate requirements for a VL instantiated according to this profile.
       required: true
     qos:
       type: tosca.datatypes.nfv.Qos
       description: Specifies the QoS requirements of a VL instantiated according to this profile.
       required: false
     virtual_link_protocol_data:
       type: list
       description: Specifies the protocol data for a virtual link.
       required: false
       entry_schema:
         type: tosca.datatypes.nfv.VirtualLinkProtocolData
  tosca.datatypes.nfv.VirtualLinkProtocolData:
   derived_from: tosca.datatypes.Root
   description: describes one protocol layer and associated protocol data for a given virtual link used in a specific VNF deployment flavour
   properties:
     associated_layer_protocol:
        type: string
        description: Identifies one of the protocols a virtualLink gives access to (ethernet, mpls, odu2, ipv4, ipv6, pseudo-wire) as specified by the connectivity_type property.
        required: true
        constraints:
          - valid_values: [ ethernet, mpls, odu2, ipv4, ipv6, pseudo-wire ]
     l2_protocol_data:
        type: tosca.datatypes.nfv.L2ProtocolData
        description: Specifies the L2 protocol data for a virtual link. Shall be present when the associatedLayerProtocol attribute indicates a L2 protocol and shall be absent otherwise.
        required: false
     l3_protocol_data:
        type: tosca.datatypes.nfv.L3ProtocolData
        description: Specifies the L3 protocol data for this virtual link.  Shall be present when the associatedLayerProtocol attribute indicates a L3 protocol and shall be absent otherwise.
        required: false
  tosca.datatypes.nfv.L2ProtocolData:
   derived_from: tosca.datatypes.Root
   description: describes L2 protocol data for a given virtual link used in a specific VNF deployment flavour.
   properties:
     name:
       type: string
       description: Identifies the network name associated with this L2 protocol.
       required: false
     network_type:
       type: string
       description: Specifies the network type for this L2 protocol. The value may be overridden at run-time.
       required: false
       constraints:
         - valid_values: [ flat, vlan, vxlan, gre ]
     vlan_transparent:
       type: boolean
       description: Specifies whether to support VLAN transparency for this L2 protocol or not.
       required: true
       default: false
     mtu:
       type: integer
       description: Specifies the maximum transmission unit (MTU) value for this L2 protocol.
       required: false
       constraints:
         - greater_than: 0
     segmentation_id:
       type: string
       description: Specifies a specific virtualised network segment, which depends on the network type. For e.g., VLAN ID for VLAN network type and tunnel ID for GRE/VXLAN network types
       required: false
  tosca.datatypes.nfv.L3ProtocolData:
   derived_from: tosca.datatypes.Root
   description: describes L3 protocol data for a given virtual link used in a specific VNF deployment flavour.
   properties:
     name:
       type: string
       description: Identifies the network name associated with this L3 protocol.
       required: false
     ip_version:
       type: string
       description: Specifies IP version of this L3 protocol. The value of the ip_version property shall be consistent with the value of the layer_protocol in the connectivity_type property of the virtual link node.
       required: true
       constraints:
         - valid_values: [ ipv4, ipv6 ]
     cidr:
       type: string
       description: Specifies the CIDR (Classless Inter-Domain Routing) of this L3 protocol. The value may be overridden at run-time.
       required: true
     ip_allocation_pools:
       type: list
       description: Specifies the allocation pools with start and end IP addresses for this L3 protocol. The value may be overridden at run-time.
       required: false
       entry_schema:
         type: tosca.datatypes.nfv.IpAllocationPool
     gateway_ip:
       type: string
       description: Specifies the gateway IP address for this L3 protocol. The value may be overridden at run-time.
       required: false
     dhcp_enabled:
       type: boolean
       description: Indicates whether DHCP (Dynamic Host Configuration Protocol) is enabled or disabled for this L3 protocol. The value may be overridden at run-time.
       required: false
     ipv6_address_mode:
       type: string
       description: Specifies IPv6 address mode. May be present when the value of the ipVersion attribute is "ipv6" and shall be absent otherwise. The value may be overridden at run-time.
       required: false
       constraints:
         - valid_values: [ slaac, dhcpv6-stateful, dhcpv6-stateless ]
  tosca.datatypes.nfv.IpAllocationPool:
   derived_from: tosca.datatypes.Root
   description: Specifies a range of IP addresses
   properties:
     start_ip_address:
       type: string
       description: The IP address to be used as the first one in a pool of addresses derived from the cidr block full IP range
       required: true
     end_ip_address:
       type: string
       description: The IP address to be used as the last one in a pool of addresses derived from the cidr block full IP range
       required: true
  tosca.datatypes.nfv.InstantiationLevel:
   derived_from: tosca.datatypes.Root
   description: Describes the scale level for each aspect that corresponds to a given level of resources to be instantiated within a deployment flavour in term of the number VNFC instances
   properties:
     description:
       type: string
       description: Human readable description of the level
       required: true
     scale_info:
       type: map # key: aspectId
       description: Represents for each aspect the scale level that corresponds to this instantiation level. scale_info shall be present if the VNF supports scaling.
       required: false
       entry_schema:
         type: tosca.datatypes.nfv.ScaleInfo
  tosca.datatypes.nfv.VduLevel:
   derived_from: tosca.datatypes.Root
   description: Indicates for a given Vdu.Compute in a given level the number of instances to deploy
   properties:
     number_of_instances:
       type: integer
       description: Number of instances of VNFC based on this VDU to deploy for this level.
       required: true
       constraints:
         - greater_or_equal: 0
  tosca.datatypes.nfv.VnfLcmOperationsConfiguration:
   derived_from: tosca.datatypes.Root
   description: Represents information to configure lifecycle management operations
   properties:
     instantiate:
       type: tosca.datatypes.nfv.VnfInstantiateOperationConfiguration
       description: Configuration parameters for the InstantiateVnf operation
       required: false
     scale:
       type: tosca.datatypes.nfv.VnfScaleOperationConfiguration
       description: Configuration parameters for the ScaleVnf operation
       required: false
     scale_to_level:
       type: tosca.datatypes.nfv.VnfScaleToLevelOperationConfiguration
       description: Configuration parameters for the ScaleVnfToLevel operation
       required: false
     change_flavour:
       type: tosca.datatypes.nfv.VnfChangeFlavourOperationConfiguration
       description: Configuration parameters for the changeVnfFlavourOpConfig operation
       required: false
     heal:
       type: tosca.datatypes.nfv.VnfHealOperationConfiguration
       description: Configuration parameters for the HealVnf operation
       required: false
     terminate:
       type: tosca.datatypes.nfv.VnfTerminateOperationConfiguration
       description: Configuration parameters for the TerminateVnf operation
       required: false
     operate:
       type: tosca.datatypes.nfv.VnfOperateOperationConfiguration
       description: Configuration parameters for the OperateVnf operation
       required: false
     change_ext_connectivity:
       type:   tosca.datatypes.nfv.VnfChangeExtConnectivityOperationConfiguration
       description: Configuration parameters for the changeExtVnfConnectivityOpConfig operation
       required: false
     change_current_package:
       type: tosca.datatypes.nfv.VnfChangeCurrentPackageOperationConfiguration
       description: Configuration parameters for the ChangeCurrentVnfPackage operation
       required: false
       # derived types are expected to introduce new properties, with their type derived from
       # tosca.datatypes.nfv.VnfChangeCurrentPackageOperationConfiguration,
       # with the same name as the operation designated to the ChangeCurrentVnfPackage request
     create_snapshot:
       type: tosca.datatypes.nfv.VnfCreateSnapshotOperationConfiguration
       description: Configuration parameters for the CreateVnfSnapshot operation
       required: false
     revert_to_snapshot:
       type: tosca.datatypes.nfv.VnfRevertToSnapshotOperationConfiguration
       description: Configuration parameters for the RevertToVnfSnapshot operation
       required: false
  tosca.datatypes.nfv.VnfInstantiateOperationConfiguration:
   derived_from: tosca.datatypes.Root
   description: represents information that affect the invocation of the InstantiateVnf operation.
   # This data type definition is reserved for future use in the present document.
   # properties:
  tosca.datatypes.nfv.VnfScaleOperationConfiguration:
   derived_from: tosca.datatypes.Root
   description: Represents information that affect the invocation of the ScaleVnf operation
   properties:
     scaling_by_more_than_one_step_supported:
       type: boolean
       description: Signals whether passing a value larger than one in the numScalingSteps parameter of the ScaleVnf operation is supported by this VNF.
       required: true
       default: false
  tosca.datatypes.nfv.VnfScaleToLevelOperationConfiguration:
   derived_from: tosca.datatypes.Root
   description: represents information that affect the invocation of the ScaleVnfToLevel operation
   properties:
     arbitrary_target_levels_supported:
       type: boolean
       description: Signals whether scaling according to the parameter "scaleInfo" is supported by this VNF
       required: true
  tosca.datatypes.nfv.VnfHealOperationConfiguration:
   derived_from: tosca.datatypes.Root
   description: represents information that affect the invocation of the HealVnf operation
   properties:
     causes:
       type: list
       description: Supported "cause" parameter values
       required: false
       entry_schema:
         type: string
  tosca.datatypes.nfv.VnfTerminateOperationConfiguration:
   derived_from: tosca.datatypes.Root
   description: represents information that affect the invocation of the TerminateVnf
   properties:
     min_graceful_termination_timeout:
       type: scalar-unit.time
       description: Minimum timeout value for graceful termination of a VNF instance
       required: true
     max_recommended_graceful_termination_timeout:
       type: scalar-unit.time
       description: Maximum recommended timeout value that can be needed to gracefully terminate a VNF instance of a particular type under certain conditions, such as maximum load condition. This is provided by VNF provider as information for the operator facilitating the selection of optimal timeout value. This value is not used as constraint
       required: false
  tosca.datatypes.nfv.VnfOperateOperationConfiguration:
   derived_from: tosca.datatypes.Root
   description: represents information that affect the invocation of the OperateVnf operation
   properties:
     min_graceful_stop_timeout:
       type: scalar-unit.time
       description: Minimum timeout value for graceful stop of a VNF instance
       required: true
     max_recommended_graceful_stop_timeout:
       type: scalar-unit.time
       description: Maximum recommended timeout value that can be needed to gracefully stop a VNF instance of a particular type under certain conditions, such as maximum load condition. This is provided by VNF provider as information for the operator facilitating the selection of optimal timeout value. This value is not used as constraint
       required: false
  tosca.datatypes.nfv.ScaleInfo:
   derived_from: tosca.datatypes.Root
   description: Indicates for a given scaleAspect the corresponding scaleLevel
   properties:
     scale_level:
       type: integer
       description: The scale level for a particular aspect
       required: true
       constraints:
         - greater_or_equal: 0
  tosca.datatypes.nfv.ScalingAspect:
   derived_from: tosca.datatypes.Root
   description: describes the details of an aspect used for horizontal scaling
   properties:
     name:
       type: string
       description: Human readable name of the aspect
       required: true
     description:
       type: string
       description: Human readable description of the aspect
       required: true
     max_scale_level:
       type: integer # positiveInteger
       description: Total number of scaling steps that can be applied w.r.t. this aspect. The value of this property corresponds to the number of scaling steps can be applied to this aspect when scaling it from the minimum scale level (i.e. 0) to the maximum scale level defined by this property
       required: true
       constraints:
         - greater_or_equal: 0
     step_deltas:
       type: list
       description: List of scaling deltas to be applied for the different subsequent scaling steps of this aspect. The first entry in the array shall correspond to the first scaling step (between scale levels 0 to 1) and the last entry in the array shall correspond to the last scaling step (between maxScaleLevel-1 and maxScaleLevel)
       required: false
       entry_schema:
         type: string # Identifier
  tosca.datatypes.nfv.VnfConfigurableProperties:
   derived_from: tosca.datatypes.Root
   description: indicates configuration properties for a given VNF (e.g. related to auto scaling and auto healing).
   properties:
     is_autoscale_enabled:
       type: boolean
       description: It permits to enable (TRUE)/disable (FALSE) the auto-scaling functionality. If the property is not present, then configuring this VNF property is not supported
       required: false
     is_autoheal_enabled:
       type: boolean
       description: It permits to enable (TRUE)/disable (FALSE) the auto-healing functionality. If the property is not present, then configuring this VNF property is not supported
       required: false
     vnfm_interface_info:
       type: tosca.datatypes.nfv.VnfmInterfaceInfo
       description: Contains information enabling access to the NFV-MANO interfaces produced by the VNFM (e.g. URIs and credentials), If the property is not present, then configuring this VNF property is not supported.
       required: false
     vnfm_oauth_server_info:
       type: tosca.datatypes.nfv.OauthServerInfo
       description: Contains information to enable discovery of the authorization server protecting access to VNFM interfaces. If the property is not present, then configuring this VNF property is not supported.
       required: false
     vnf_oauth_server_info:
       type: tosca.datatypes.nfv.OauthServerInfo
       description: Contains information to enable discovery of the authorization server to validate the access tokens provided by the VNFM when  the VNFM accesses the VNF interfaces, if that functionality (token introspection) is supported by the authorization server. If the property is not present, then configuring this VNF property is not supported.
       required: false
     # additional_configurable_properties:
       # description: It provides VNF specific configurable properties that can be
       # modified using the ModifyVnfInfo operation
       # required: false
       # type: tosca.datatypes.nfv.VnfAdditionalConfigurableProperties
     # derived types are expected to introduce
     # additional_configurable_properties with its type derived from
     # tosca.datatypes.nfv.VnfAdditionalConfigurableProperties
  tosca.datatypes.nfv.VnfAdditionalConfigurableProperties:
   derived_from: tosca.datatypes.Root
   description: is an empty base type for deriving data types for describing additional configurable properties for a given VNF
   properties:
     is_writable_anytime:
       type: boolean
       description: It specifies whether these additional configurable properties are writeable (TRUE) at any time (i.e. prior to / at instantiation time as well as after instantiation).or (FALSE) only prior to / at instantiation time. If this property is not present, the additional configurable properties are writable anytime.
       required: true
       default : true
  tosca.datatypes.nfv.VnfInfoModifiableAttributes:
   derived_from: tosca.datatypes.Root
   description: Describes VNF-specific extension and metadata for a given VNF
   #properties:
     #extensions:
       #type: tosca.datatypes.nfv.VnfInfoModifiableAttributesExtensions
       #description: "Extension" properties of VnfInfo that are writeable
       #required: false
       # derived types are expected to introduce
       # extensions with its type derived from
       # tosca.datatypes.nfv.VnfInfoModifiableAttributesExtensions
     #metadata:
       #type: tosca.datatypes.nfv.VnfInfoModifiableAttributesMetadata
       #description: "Metadata" properties of VnfInfo that are writeable
       #required: false
       # derived types are expected to introduce
       # metadata with its type derived from
       # tosca.datatypes.nfv.VnfInfoModifiableAttributesMetadata
  tosca.datatypes.nfv.VnfInfoModifiableAttributesExtensions:
   derived_from: tosca.datatypes.Root
   description: is an empty base type for deriving data types for describing VNF-specific extension
  tosca.datatypes.nfv.VnfInfoModifiableAttributesMetadata:
   derived_from: tosca.datatypes.Root
   description: is an empty base type for deriving data types for describing VNF-specific metadata
  tosca.datatypes.nfv.LogicalNodeData:
   derived_from: tosca.datatypes.Root
   description: Describes compute, memory and I/O requirements associated with a particular VDU.
   properties:
     logical_node_requirements:
       type: map
       description: The logical node-level compute, memory and I/O requirements. A map  of strings that contains a set of key-value pairs that describes hardware platform specific deployment requirements, including the number of CPU cores on this logical node, a memory configuration specific to a logical node  or a requirement related to the association of an I/O device with the logical node.
       required: false
       entry_schema:
         type: string
  tosca.datatypes.nfv.SwImageData:
   derived_from: tosca.datatypes.Root
   description: describes information  related to a software image artifact
   properties:
     name:
       type: string
       description: Name of this software image
       required: true
     version:
       type: string
       description: Version of this software image
       required: true
     provider:
       type: string
       description: Provider of this software image
       required: false
     checksum:
       type: tosca.datatypes.nfv.ChecksumData
       description:  Checksum of the software image file
       required: true
     container_format:
       type: string
       description: The container format describes the container file format in which software image is provided
       required: true
       constraints:
         - valid_values: [ aki, ami, ari, bare, docker, ova, ovf ]
     disk_format:
       type: string
       description: The disk format of a software image is the format of the underlying disk image
       required: true
       constraints:
         - valid_values: [ aki, ami, ari, iso, qcow2, raw, vdi, vhd, vhdx, vmdk ]
     min_disk:
       type: scalar-unit.size # Number
       description:  The minimal disk size requirement for this software image
       required: true
       constraints:
         - greater_or_equal: 0 B
     min_ram:
       type: scalar-unit.size # Number
       description: The minimal RAM requirement for this software image
       required: false
       constraints:
         - greater_or_equal: 0 B
     size:
       type: scalar-unit.size # Number
       description: The size of this software image
       required: true
     operating_system:
       type: string
       description: Identifies the operating system used in the software image
       required: false
     supported_virtualisation_environments:
       type: list
       description: Identifies the virtualisation environments (e.g. hypervisor) compatible with this software image
       required: false
       entry_schema:
         type: string
  tosca.datatypes.nfv.VirtualBlockStorageData:
   derived_from: tosca.datatypes.Root
   description: VirtualBlockStorageData describes block storage requirements associated with compute resources in a particular VDU, either as a local disk or as virtual attached storage
   properties:
     size_of_storage:
       type: scalar-unit.size
       description: Size of virtualised storage resource
       required: true
       constraints:
         - greater_or_equal: 0 B
     vdu_storage_requirements:
       type: map
       description: The hardware platform specific storage requirements. A map of strings that contains a set of key-value pairs that represents the hardware platform specific storage deployment requirements
       required: false
       entry_schema:
         type: string
     rdma_enabled:
       type: boolean
       description: Indicates if the storage support RDMA
       required: true
       default: false
  tosca.datatypes.nfv.VirtualObjectStorageData:
     derived_from: tosca.datatypes.Root
     description: VirtualObjectStorageData describes object storage requirements associated with compute resources in a particular VDU
     properties:
       max_size_of_storage:
         type: scalar-unit.size
         description: Maximum size of virtualized  storage resource
         required: false
         constraints:
           - greater_or_equal: 0 B
  tosca.datatypes.nfv.VirtualFileStorageData:
       derived_from: tosca.datatypes.Root
       description: VirtualFileStorageData describes file storage requirements associated with compute resources in a particular VDU
       properties:
         size_of_storage:
           type: scalar-unit.size
           description: Size of virtualized storage resource
           required: true
           constraints:
             - greater_or_equal: 0 B
         file_system_protocol:
           type: string
           description: The shared file system protocol (e.g. NFS, CIFS)
           required: true
  tosca.datatypes.nfv.VirtualLinkBitrateLevel:
    derived_from: tosca.datatypes.Root
    description: Describes bitrate requirements applicable to the virtual link instantiated from a particicular VnfVirtualLink
    properties:
      bitrate_requirements:
       type: tosca.datatypes.nfv.LinkBitrateRequirements
       description: Virtual link bitrate requirements for an instantiation level or bitrate delta for a scaling step
       required: true
  tosca.datatypes.nfv.VnfOperationAdditionalParameters:
    derived_from: tosca.datatypes.Root
    description: Is an empty base type for deriving data type for describing VNF-specific parameters to be passed when invoking lifecycle management operations
    # properties:
  tosca.datatypes.nfv.VnfChangeFlavourOperationConfiguration:
    derived_from: tosca.datatypes.Root
    description: represents information that affect the invocation of the ChangeVnfFlavour operation
    # This data type definition is reserved for future use in the present document.
    # properties:
  tosca.datatypes.nfv.VnfChangeExtConnectivityOperationConfiguration:
    derived_from: tosca.datatypes.Root
    description: represents information that affect the invocation of the ChangeExtVnfConnectivity operation
    # This data type definition is reserved for future use in the present document.
    # properties:
  tosca.datatypes.nfv.VnfcMonitoringParameter:
    derived_from: tosca.datatypes.Root
    description: Represents information on virtualised resource related performance metrics applicable to the VNF.
    properties:
      name:
       type: string
       description: Human readable name of the monitoring parameter
       required: true
      performance_metric:
       type: string
       description: Identifies a performance metric to be monitored, according to ETSI GS NFV-IFA 027.
       required: true
       constraints:
         - valid_values: [ v_cpu_usage_mean_vnf, v_cpu_usage_peak_vnf, v_memory_usage_mean_vnf, v_memory_usage_peak_vnf, v_disk_usage_mean_vnf, v_disk_usage_peak_vnf, byte_incoming_vnf_int_cp, byte_outgoing_vnf_int_cp, packet_incoming_vnf_int_cp, packet_outgoing_vnf_int_cp, v_cpu_usage_mean, v_cpu_usage_peak,v_memory_usage_mean,v_memory_usage_peak, v_disk_usage_mean, v_disk_usage_peak, v_net_byte_incoming, v_net_byte_outgoing, v_net_packet_incoming, v_net_packet_outgoing, usage_mean_vStorage, usage_peak_vStorage ]
      collection_period:
       type: scalar-unit.time
       description: Describes the  periodicity at which to collect the performance information.
       required: false
       constraints:
        - greater_than: 0 s
  tosca.datatypes.nfv.VirtualLinkMonitoringParameter:
    derived_from: tosca.datatypes.Root
    description: Represents information on virtualised resource related performance metrics applicable to the VNF.
    properties:
      name:
       type: string
       description: Human readable name of the monitoring parameter
       required: true
      performance_metric:
       type: string
       description: Identifies a performance metric to be monitored.
       required: true
       constraints:
         - valid_values: [ byte_incoming, byte_outgoing, packet_incoming, packet_outgoing ]
      collection_period:
       type: scalar-unit.time
       description: Describes the periodicity at which to collect the performance information.
       required: false
       constraints:
        - greater_than: 0 s
  tosca.datatypes.nfv.InterfaceDetails:
    derived_from: tosca.datatypes.Root
    description: information used to access an interface exposed by a VNF
    properties:
      uri_components:
       type: tosca.datatypes.nfv.UriComponents
       description: Provides components to build a Uniform Ressource Identifier (URI) where to access the interface end point.
       required: false
      interface_specific_data:
       type: map
       description: Provides additional details that are specific to the type of interface considered.
       required: false
       entry_schema:
        type: string
  tosca.datatypes.nfv.UriComponents:
    derived_from: tosca.datatypes.Root
    description: information used to build a URI that complies with IETF RFC 3986 [8].
    properties:
      scheme:
       type: string # shall comply with IETF RFC 3986
       description: scheme component of a URI.
       required: true
      authority:
       type: tosca.datatypes.nfv.UriAuthority
       description: Authority component of a URI
       required: false
      path:
       type: string # shall comply with IETF RFC 3986
       description: path component of a URI.
       required: false
      query:
       type: string # shall comply with IETF RFC 3986
       description: query component of a URI.
       required: false
      fragment:
       type: string # shall comply with IETF RFC 3986
       description: fragment component of a URI.
       required: false
  tosca.datatypes.nfv.UriAuthority:
    derived_from: tosca.datatypes.Root
    description: information that corresponds to the authority component of a URI as specified in IETF RFC 3986 [8]
    properties:
     user_info:
      type: string # shall comply with IETF RFC 3986
      description: user_info field of the authority component of a URI
      required: false
     host:
      type: string # shall comply with IETF RFC 3986
      description: host field of the authority component of a URI
      required: false
     port:
      type: string # shall comply with IETF RFC 3986
      description: port field of the authority component of a URI
      required: false
  tosca.datatypes.nfv.ChecksumData:
     derived_from: tosca.datatypes.Root
     description: Describes information about the result of performing a checksum operation over some arbitrary data
     properties:
       algorithm:
         type: string
         description: Describes the algorithm used to obtain the checksum value
         required: true
         constraints:
           - valid_values: [sha-224, sha-256, sha-384, sha-512 ]
       hash:
         type: string
         description: Contains the result of applying the algorithm indicated by the algorithm property to the data to which this ChecksumData refers
         required: true
  tosca.datatypes.nfv.VnfmInterfaceInfo:
    derived_from: tosca.datatypes.Root
    description: describes information enabling the VNF instance to access the NFV-MANO interfaces produced by the VNFM
    properties:
      interface_name:
        type: string
        description: Identifies an interface produced by the VNFM.
        required: true
        constraints:
          - valid_values: [ vnf_lcm, vnf_pm, vnf_fm ]
      details:
        type: tosca.datatypes.nfv.InterfaceDetails
        description: Provide additional data to access the interface endpoint
        required: false
      credentials:
        type: map
        description: Provides credential enabling access to the interface
        required: false
        entry_schema:
          type: string
  tosca.datatypes.nfv.OauthServerInfo:
    derived_from: tosca.datatypes.Root
    description: information to enable discovery of the authorization server
    #properties: FFS
    #This data type definition is reserved for future use in the present document
  tosca.datatypes.nfv.BootData:
    derived_from: tosca.datatypes.Root
    description: describes the information used to customize a virtualised compute resource at boot time.
    properties:
      vim_specific_properties:
        type: tosca.datatypes.nfv.BootDataVimSpecificProperties
        description: Properties used for selecting VIM specific capabilities when setting the boot data.
        required: false
      kvp_data:
        type: tosca.datatypes.nfv.KvpData
        description: A set of key-value pairs for configuring a virtual compute resource.
        required: false
      content_or_file_data:
        type: tosca.datatypes.nfv.ContentOrFileData
        description: A string content or a file for configuring a virtual compute resource.
        required: false
  tosca.datatypes.nfv.KvpData:
    derived_from: tosca.datatypes.Root
    description: describes a set of key-value pairs information used to customize a virtualised compute resource at boot time by using only key-value pairs data.
    properties:
      data:
        type: map
        description: A map of strings that contains a set of key-value pairs that describes the information for configuring the virtualised compute resource.
        required: false
        entry_schema:
          type: string
  tosca.datatypes.nfv.ContentOrFileData:
    derived_from: tosca.datatypes.Root
    description: describes a string content or a file information used to customize a virtualised compute resource at boot time by using string content or file.
    properties:
      data:
        type: map
        description: A map of strings that contains a set of key-value pairs that carries the dynamic deployment values which used to replace the corresponding variable parts in the file as identify by a URL as described in source_path. Shall be present if "source_path" is present and shall be absent otherwise..
        required: false
        entry_schema:
          type: string
      content:
        type: string
        description: The string information used to customize a virtualised compute resource at boot time.
        required: false
      source_path:
        type: string
        description: The URL to a file contained in the VNF package used to customize a virtualised compute resource. The content shall comply with IETF RFC 3986 [8].
        required: false
      destination_path:
        type: string
        description: The URL address when inject a file into the virtualised compute resource. The content shall comply with IETF RFC 3986 [8].
        required: false
  tosca.datatypes.nfv.BootDataVimSpecificProperties:
    derived_from: tosca.datatypes.Root
    description: describes the VIM specific information used for selecting VIM specific capabilities when setting the boot data.
    properties:
      vim_type:
        type: string
        description: Discriminator for the different types of the VIM information.
        required: true
      properties:
        type: map
        description: Properties used for selecting VIM specific capabilities when setting the boot data
        entry_schema:
          type: string
        required: true
  tosca.datatypes.nfv.VnfPackageChangeSelector:
    derived_from: tosca.datatypes.Root
    description: data type describes the source and destination VNFDs as well as source deployment flavour for a change current VNF Package.
    properties:
      source_descriptor_id:
        type: string
        description: Identifier of the source VNFD and the source VNF package.
        required: true
      destination_descriptor_id:
        type: string
        description: Identifier of the destination VNFD and the destination VNF package.
        required: true
      source_flavour_id:
        type: string
        description: Identifier of the deployment flavour in the source VNF package for which this data type applies.
        required: true
  tosca.datatypes.nfv.VnfPackageChangeComponentMapping:
    derived_from: tosca.datatypes.Root
    description: A mapping between the identifier of a components or property in the source VNFD and the identifier of the corresponding component or property in the destination VNFD.
    properties:
      component_type:
        type: string
        description: The type of component or property. Possible values differentiate whether changes concern to some VNF component (e.g. VDU, internal VLD, etc.) or property (e.g. a Scaling Aspect, etc.).
        constraints:
          - valid_values: [ vdu, cp, virtual_link, virtual_storage, deployment_flavour, instantiation_level, scaling_aspect ]
        required: true
      source_id:
        type: string
        description: Identifier of the component or property in the source VNFD.
        required: true
      destination_id:
        type: string
        description: Identifier of the component or property in the destination VNFD.
        required: true
      description:
        type: string
        description: Human readable description of the component changes.
        required: false
  tosca.datatypes.nfv.VnfChangeCurrentPackageOperationConfiguration:
    derived_from: tosca.datatypes.Root
    description: represents information that affect the invocation of the change current VNF Package operation.
    # This data type definition is reserved for future use in the present document.
    # properties:
      # derived types are expected to introduce new properties, with their type derived from tosca.datatypes.nfv.VnfChangeCurrentPackageOperationConfiguration, with the same name as the operation designated to the ChangeCurrentVnfPackage request
  tosca.datatypes.nfv.VnfCreateSnapshotOperationConfiguration:
    derived_from: tosca.datatypes.Root
    description: represents information that affect the invocation of the CreateVnfSnapshot operation
  # This data type definition is reserved for future use in the present document.
  # properties:
  tosca.datatypes.nfv.VnfRevertToSnapshotOperationConfiguration:
    derived_from: tosca.datatypes.Root
    description: represents information that affect the invocation of the RevertToVnfSnapshot operation
  # This data type definition is reserved for future use in the present document.
  # properties:
  tosca.datatypes.nfv.VnfLcmOpCoord:
    derived_from: tosca.datatypes.Root
    description: describes a set of information used for a coordination action in a VNF lifecycle management operation for a given VNF.
    properties:
      description:
        type: string
        description: Human readable description of the coordination action.
        required: false
      endpoint_type:
        type: string
        description: Specifies the type of the endpoint exposing the LCM operation coordination such as other operations supporting or management systems (e.g. an EM) or the VNF instance. If the VNF produces the LCM coordination interface, this property may be omitted or may have the value "vnf". If this attribute is omitted, the type of endpoint that provides the interface is determined at deployment time. If the VNF does not produce the LCM coordination interface but coordination via this interface is needed, it is expected that a management entity such as the EM exposes the coordination interface, and consequently, this attribute shall be present and shall have the value “mgmt”.
        required: false
        constraints:
          - valid_values: [ mgmt, vnf ]
      coordination_stage:
        type: string
        description: Indicates whether the coordination action is invoked before or after all other changes performed by the VNF LCM operation. coordination_stage property shall be omitted if the coordination action is intended to be invoked at an intermediate stage of the LCM operation, i.e. neither at the start nor at the end. In this case, the time at which to invoke  the coordination during the execution of  the LCM operation is determined by means outside the scope of the present document such as VNFM-internal logic or LCM script.
        required: false
        constraints:
          - valid_values: [ start, end  ]
      # input_parameters:
        # type: tosca.datatypes.nfv.InputOpCoordParams
        # description: Input parameters to be provided in the LCM coordination request.
        # required: false
      # output_parameters:
        # type: tosca.datatypes.nfv.OutputOpCoordParams
        # description: Output parameters provided in the LCM coordination response.
        # required: false
  tosca.datatypes.nfv.OutputOpCoordParams:
    derived_from: tosca.datatypes.Root
    description: is an empty base type for deriving data types for describing additional Output operation coordination parameters for a given coordination action
artifact_types:
  tosca.artifacts.nfv.SwImage:
    derived_from: tosca.artifacts.Deployment.Image
    description: describes the software image which is directly loaded on the virtualisation container realizing of the VDU or is to be loaded on a virtual storage resource
    properties:
      name:
        type: string
        description: Name of this software image
        required: true
      version:
        type: string
        description: Version of this software image
        required: true
      provider:
        type: string
        description: Provider of this software image
        required: false
      checksum:
        type: tosca.datatypes.nfv.ChecksumData
        description:  Checksum of the software image file
        required: true
      container_format:
        type: string
        description: The container format describes the container file format in which software image is provided
        required: true
        constraints:
          - valid_values: [ aki, ami, ari, bare, docker, ova, ovf ]
      disk_format:
        type: string
        description: The disk format of a software image is the format of the underlying disk image
        required: true
        constraints:
          - valid_values: [ aki, ami, ari, iso, qcow2, raw, vdi, vhd, vhdx, vmdk ]
      min_disk:
        type: scalar-unit.size # Number
        description:  The minimal disk size requirement for this software image
        required: true
        constraints:
          - greater_or_equal: 0 B
      min_ram:
        type: scalar-unit.size # Number
        description: The minimal RAM requirement for this software image
        required: false
        constraints:
          - greater_or_equal: 0 B
      size:
        type: scalar-unit.size # Number
        description: The size of this software image
        required: true
      operating_system:
        type: string
        description: Identifies the operating system used in the software image
        required: false
      supported_virtualisation_environments:
        type: list
        description: Identifies the virtualisation environments (e.g. hypervisor) compatible with this software image
        required: false
        entry_schema:
          type: string
  tosca.artifacts.Implementation.nfv.Mistral:
    derived_from: tosca.artifacts.Implementation
    description: artifacts for Mistral workflows
    mime_type: application/x-yaml
    file_ext: [ yaml ]
capability_types:
  tosca.capabilities.nfv.VirtualBindable:
    derived_from: tosca.capabilities.Node
    description: Indicates that the node that includes it can be pointed by a tosca.relationships.nfv.VirtualBindsTo relationship type which is used to model the VduHasCpd association
  tosca.capabilities.nfv.VirtualCompute:
    derived_from: tosca.capabilities.Node
    description: Describes the capabilities related to virtual compute resources
    properties:
      logical_node:
       type: map
       description: Describes the Logical Node requirements
       required: false
       entry_schema:
         type: tosca.datatypes.nfv.LogicalNodeData
      requested_additional_capabilities:
       type: map
       description: Describes additional capability for a particular VDU
       required: false
       entry_schema:
         type: tosca.datatypes.nfv.RequestedAdditionalCapability
      compute_requirements:
       type: map
       required: false
       entry_schema:
         type: string
      virtual_memory:
       type: tosca.datatypes.nfv.VirtualMemory
       description: Describes virtual memory of the virtualized compute
       required: true
      virtual_cpu:
       type: tosca.datatypes.nfv.VirtualCpu
       description: Describes virtual CPU(s) of the virtualized compute
       required: true
      virtual_local_storage:
       type: list
       description: A list of virtual system disks created and destroyed as part of the VM lifecycle
       required: false
       entry_schema:
        type: tosca.datatypes.nfv.VirtualBlockStorageData
        description: virtual system disk definition
  tosca.capabilities.nfv.VirtualStorage:
    derived_from: tosca.capabilities.Root
    description: Describes the attachment capabilities related to Vdu.Storage
  tosca.capabilities.nfv.TrunkBindable:
    derived_from: tosca.capabilities.Node
    description: Indicates that the node that includes it can be pointed by a tosca.relationships.nfv.TrunkBindsTo relationship type which is used to model the trunkPortTopology.
relationship_types:
  tosca.relationships.nfv.VirtualBindsTo:
    derived_from: tosca.relationships.DependsOn
    description: Represents an association relationship between Vdu.Compute and VduCp node types
    valid_target_types: [ tosca.capabilities.nfv.VirtualBindable ]
  tosca.relationships.nfv.AttachesTo:
    derived_from: tosca.relationships.Root
    description: Represents an association relationship between the Vdu.Compute and one of the node types, Vdu.VirtualBlockStorage, Vdu.VirtualObjectStorage or Vdu.VirtualFileStorage
    valid_target_types: [ tosca.capabilities.nfv.VirtualStorage ]
  tosca.relationships.nfv.TrunkBindsTo:
    derived_from: tosca.relationships.DependsOn
    description: Represents the association relationship between a VduCp node used as a trunk port and other VduSubCp nodes used as subports of the same trunk.
    valid_target_types: [ tosca.capabilities.nfv.TrunkBindable ]
interface_types:
  tosca.interfaces.nfv.Vnflcm:
    derived_from: tosca.interfaces.Root
    description: This interface encompasses a set of TOSCA operations corresponding to the VNF LCM operations defined in ETSI GS NFV-IFA 007 as well as to preamble and postamble procedures to the execution of the VNF LCM operations.
    operations:
      instantiate:
        description: Invoked upon receipt of an Instantiate VNF request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      instantiate_start:
        description: Invoked before instantiate
      instantiate_end:
        description: Invoked after instantiate
      terminate:
        description: Invoked upon receipt Terminate VNF request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      terminate_start:
        description: Invoked before terminate
      terminate_end:
        description: Invoked after terminate
      modify_information:
        description: Invoked upon receipt of a Modify VNF Information request
      modify_information_start:
        description: Invoked before modify_information
      modify_information_end:
        description: Invoked after modify_information
      change_flavour:
        description: Invoked upon receipt of a Change VNF Flavour request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      change_flavour_start:
        description: Invoked before change_flavour
      change_flavour_end:
        description: Invoked after change_flavour
      change_external_connectivity:
        description: Invoked upon receipt of a Change External VNF Connectivity  request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      change_external_connectivity_start:
        description: Invoked before change_external_connectivity
      change_external_connectivity_end:
        description: Invoked after change_external_connectivity
      operate:
        description: Invoked upon receipt of an Operate VNF request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      operate_start:
        description: Invoked before operate
      operate_end:
        description: Invoked after operate
      heal:
        description: Invoked upon receipt of a Heal VNF request
      # inputs:
      #   additional_parameters:
      #     type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
      #     required: false
      # derived types are expected to introduce additional_parameters with its
      # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
        inputs:
          cause:
            type: string
            description: Indicates the reason why a healing procedure is required.
            required: false
          vnfc_instance_ids:
            type: list
            entry_schema:
              type: string
            description: List of VNFC instances requiring a healing action.
            required: false
      heal_start:
        description: Invoked before heal
      heal_end:
        description: Invoked after heal
      scale:
        description: Invoked upon receipt of a Scale VNF request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
        inputs:
          type:
            type: string
            description: Indicates the type of the scale operation requested.
            required: false
            constraints:
              - valid_values: [ scale_out, scale_in ]
          aspect:
            type: string
            description: Identifier of the scaling aspect.
            required: false
          number_of_steps:
            type: integer
            description: Number of scaling steps to be executed.
            required: true
            constraints:
              - greater_than: 0
            default: 1
      scale_start:
        description: Invoked before scale
      scale_end:
        description: Invoked after scale
      scale_to_level:
        description: Invoked upon receipt of a Scale VNF to Level request
      # inputs:
        # additional_parameters:
        # type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
        # required: false
     # derived types are expected to introduce additional_parameters with its
     # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
        inputs:
          instantiation_level:
            type: string
            description: Identifier of the target instantiation level of the current deployment flavour to which the VNF is requested to be scaled. Either instantiation_level or scale_info shall be provided.
            required: false
          scale_info:
            type: map # key: aspectId
            description: For each scaling aspect of the current deployment flavour, indicates the target scale level to which the VNF is to be scaled. Either instantiation_level or scale_info shall be provided.
            required: false
            entry_schema:
              type: tosca.datatypes.nfv.ScaleInfo
      scale_to_level_start:
        description: Invoked before scale_to_level
      scale_to_level_end:
        description: Invoked after scale_to_level
      create_snapshot:
        description: Invoked upon receipt of a Create VNF snapshot request
        # inputs:
          # additional_parameters:
          #   type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
          #   required: false
      # derived types are expected to introduce additional_parameters with its
      # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      create_snapshot_start:
        description: Invoked before create_snapshot
      create_snapshot_end:
        description: Invoked after create_snapshot
      revert_to_snapshot:
        description: Invoked upon receipt of a Revert to VNF snapshot request
        # inputs:
          # additional_parameters:
          #   type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
          #   required: false
      # derived types are expected to introduce additional_parameters with its
      # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      revert_to_snapshot_start:
        description: Invoked before revert_to_snapshot
      revert_to_snapshot_end:
        description: Invoked after revert_to_snapshot
      change_current_package:
        description: Invoked by tosca.policies.nfv.VnfPackageChange
        # inputs:
          # additional_parameters:
          #   type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
          #   required: false
      # derived types are expected to introduce additional_parameters with its
      # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
      change_current_package_start:
        description: Invoked by tosca.policies.nfv.VnfPackageChange
      change_current_package_end:
        description: Invoked by tosca.policies.nfv.VnfPackageChange
    notifications:
      change_current_package_notification:
        description: Invoked upon receipt of a ChangeCurrentVnfPackage request
      change_current_package_start_notification:
        description: Invoked before the operation designated to changing the current VNF package
      change_current_package_end_notification:
        description: Invoked after the operation designated to changing the current VNF package
  tosca.interfaces.nfv.VnfIndicator:
    derived_from: tosca.interfaces.Root
    description: This interface is an empty base interface type for deriving VNF specific interface types that include VNF indicator specific notifications.
  tosca.interfaces.nfv.ChangeCurrentVnfPackage:
    derived_from: tosca.interfaces.Root
    description: This interface is an empty base interface type for deriving VNF specific interface types that include VNF Change Current VNF Package specific operation.
  # operations:
      # operation_name: name of a VNF-specific operation serving the Change current VNF Package request.
        # description: Invoked by tosca.policies.nfv.VnfPackageChange
        # inputs:
          # additional_parameters:
          #   type: tosca.datatypes.nfv.VnfOperationAdditionalParameters
          #   required: false
      # derived types are expected to introduce additional_parameters with its
      # type derived from tosca.datatypes.nfv.VnfOperationAdditionalParameters
node_types:
  tosca.nodes.nfv.VNF:
    derived_from: tosca.nodes.Root
    description: The generic abstract type from which all VNF specific node types shall be derived to form, together with other node types, the TOSCA service template(s) representing the VNFD
    properties:
      descriptor_id: # instead of vnfd_id
       type: string # UUID
       description: Identifier of this VNFD information element. This attribute shall be globally unique
       required: true
      descriptor_version: # instead of vnfd_version
       type: string
       description: Identifies the version of the VNFD
       required: true
      provider: # instead of vnf_provider
       type: string
       description: Provider of the VNF and of the VNFD
       required: true
      product_name: # instead of vnf_product_name
       type: string
       description: Human readable name for the VNF Product
       required: true
      software_version: # instead of vnf_software_version
       type: string
       description: Software version of the VNF
       required: true
      product_info_name: # instead of vnf_product_info_name
       type: string
       description: Human readable name for the VNF Product
       required: false
      product_info_description: # instead of vnf_product_info_description
       type: string
       description: Human readable description of the VNF Product
       required: false
      vnfm_info:
       type: list
       required: true
       description: Identifies VNFM(s) compatible with the VNF
       entry_schema:
        type: string
        constraints:
          - pattern: (^etsivnfm:v[0-9]?[0-9]\.[0-9]?[0-9]\.[0-9]?[0-9]$)|(^[0-9]+:[a-zA-Z0-9.-]+$)
      localization_languages:
       type: list
       description: Information about localization languages of the VNF
       required: false
       entry_schema:
        type: string #IETF RFC 5646 string
      default_localization_language:
       type: string #IETF RFC 5646 string
       description: Default localization language that is instantiated if no information about selected localization language is available
       required: false
      #configurable_properties:
       #type: tosca.datatypes.nfv.VnfConfigurableProperties
       #description: Describes the configurable properties of the VNF
       #required: false
       # derived types are expected to introduce configurable_properties
       # with its type derived from tosca.datatypes.nfv.VnfConfigurableProperties
      #modifiable_attributes:
       #type: tosca.datatypes.nfv.VnfInfoModifiableAttributes
       #description: Describes the modifiable attributes of the VNF
       #required: false
       # derived types are expected to introduce modifiable_attributes
       # with its type derived from
       # tosca.datatypes.nfv.VnfInfoModifiableAttributes
      lcm_operations_configuration:
       type: tosca.datatypes.nfv.VnfLcmOperationsConfiguration
       description: Describes the configuration parameters for the VNF LCM operations
       required: false
      monitoring_parameters:
       type: map # key: id
       entry_schema:
        type: tosca.datatypes.nfv.VnfMonitoringParameter
       description: Describes monitoring parameters applicable to the VNF.
       required: false
      flavour_id:
       type: string
       description: Identifier of the Deployment Flavour within the VNFD
       required: true
      flavour_description:
       type: string
       description: Human readable description of the DF
       required: true
      vnf_profile:
       type: tosca.datatypes.nfv.VnfProfile
       description: Describes a profile for instantiating VNFs of a particular NS DF according to a specific VNFD and VNF DF
       required: false
    attributes:
      scale_status:
        type: map # key: aspectId
        description: Scale status of the VNF, one entry per aspect. Represents for every scaling aspect how "big" the VNF has been scaled w.r.t. that aspect.
        entry_schema:
          type: tosca.datatypes.nfv.ScaleInfo
    requirements:
      - virtual_link:
          capability: tosca.capabilities.nfv.VirtualLinkable
          relationship: tosca.relationships.nfv.VirtualLinksTo
          occurrences: [ 0, 1 ]
    # Additional requirements shall be defined in the VNF specific node type (deriving from tosca.nodes.nfv.VNF) corresponding to NS virtual links that need to connect to VnfExtCps
    interfaces:
      Vnflcm:
        type: tosca.interfaces.nfv.Vnflcm
    # VnfIndicator:
    #   type: tosca.interfaces.nfv.VnfIndicator
    # derived types are expected to introduce Vnf Indicator interfaces
    # with their type derived from tosca.interfaces.nfv.VnfIndicator
  tosca.nodes.nfv.VnfExtCp:
    derived_from: tosca.nodes.nfv.Cp
    description: Describes a logical external connection point, exposed by the VNF enabling connection with an external Virtual Link
    properties:
      virtual_network_interface_requirements:
       type: list
       description: The actual virtual NIC requirements that is been assigned when instantiating the connection point
       required: false
       entry_schema:
        type: tosca.datatypes.nfv.VirtualNetworkInterfaceRequirements
    requirements:
      - external_virtual_link:
          capability: tosca.capabilities.nfv.VirtualLinkable
          relationship: tosca.relationships.nfv.VirtualLinksTo
          occurrences: [0, 1]
      - internal_virtual_link:
          capability: tosca.capabilities.nfv.VirtualLinkable
          relationship: tosca.relationships.nfv.VirtualLinksTo
          occurrences: [1, 1]
  tosca.nodes.nfv.Vdu.Compute:
    derived_from: tosca.nodes.Root
    description: Describes the virtual compute part of a VDU which is a construct  supporting the description of the deployment and operational behavior of a VNFC
    properties:
      name:
        type: string
        description: Human readable name of the VDU
        required: true
      description:
        type: string
        description: Human readable description of the VDU
        required: true
      boot_order:
        type: boolean
        description: indicates whether the order of the virtual_storage requirements is used as the boot index (the first requirement represents the lowest index and defines highest boot priority)
        required: true
        default: false
      nfvi_constraints:
        type: map
        description: Describes constraints on the NFVI for the VNFC instance(s) created from this VDU. This property is reserved for future use in the present document.
        required: false
        entry_schema:
          type: string
      monitoring_parameters:
        type: map # key: id
        description: Describes monitoring parameters applicable to a VNFC instantiated from this VDU
        required: false
        entry_schema:
          type: tosca.datatypes.nfv.VnfcMonitoringParameter
      #configurable_properties:
        #type: tosca.datatypes.nfv.VnfcConfigurableProperties
        #required: false
        # derived types are expected to introduce
        # configurable_properties with its type derived from
        # tosca.datatypes.nfv.VnfcConfigurableProperties
      vdu_profile:
        type: tosca.datatypes.nfv.VduProfile
        description: Defines additional instantiation data for the VDU.Compute node
        required: true
      sw_image_data:
        type: tosca.datatypes.nfv.SwImageData
        description: Defines information related to a SwImage artifact used by this Vdu.Compute node
        required: false # property is required when the node template has an associated artifact of type tosca.artifacts.nfv.SwImage and not required otherwise
        status: deprecated
      boot_data:
        type: tosca.datatypes.nfv.BootData
        description: Contains the information used to customize a virtualised compute resource at boot time. The bootData may contain variable parts that are replaced by deployment specific values before being sent to the VIM.
        required: false
    capabilities:
      virtual_compute:
        type: tosca.capabilities.nfv.VirtualCompute
        occurrences: [ 1, 1 ]
      virtual_binding:
        type: tosca.capabilities.nfv.VirtualBindable
        occurrences: [ 1, UNBOUNDED ]
    requirements:
      - virtual_storage:
          capability: tosca.capabilities.nfv.VirtualStorage
          relationship: tosca.relationships.nfv.AttachesTo
          occurrences: [ 0, UNBOUNDED ]
  tosca.nodes.nfv.Vdu.VirtualBlockStorage:
    derived_from: tosca.nodes.Root
    description: This node type describes the specifications of requirements related to virtual block storage resources
    properties:
      virtual_block_storage_data:
        type: tosca.datatypes.nfv.VirtualBlockStorageData
        description: Describes the block storage characteristics.
        required: true
      sw_image_data:
        type: tosca.datatypes.nfv.SwImageData
        description: Defines information related to a SwImage artifact used by this Vdu.Compute node.
        required: false # property is required when the node template has an associated artifact of type tosca.artifacts.nfv.SwImage and not required otherwise
        status: deprecated
    capabilities:
      virtual_storage:
        type: tosca.capabilities.nfv.VirtualStorage
        description: Defines the capabilities of virtual_storage.
  tosca.nodes.nfv.Vdu.VirtualObjectStorage:
    derived_from: tosca.nodes.Root
    description: This node type describes the specifications of requirements related to virtual object storage resources
    properties:
      virtual_object_storage_data:
        type: tosca.datatypes.nfv.VirtualObjectStorageData
        description: Describes the object storage characteristics.
        required: true
    capabilities:
      virtual_storage:
        type: tosca.capabilities.nfv.VirtualStorage
        description: Defines the capabilities of virtual_storage.
  tosca.nodes.nfv.Vdu.VirtualFileStorage:
    derived_from: tosca.nodes.Root
    description: This node type describes the specifications of requirements related to virtual file storage resources
    properties:
      virtual_file_storage_data:
        type: tosca.datatypes.nfv.VirtualFileStorageData
        description: Describes the file  storage characteristics.
        required: true
    capabilities:
      virtual_storage:
        type: tosca.capabilities.nfv.VirtualStorage
        #description: Defines the capabilities of virtual_storage.
    requirements:
      - virtual_link:
          capability: tosca.capabilities.nfv.VirtualLinkable
          relationship: tosca.relationships.nfv.VirtualLinksTo
          occurrences: [1, 1]
          # description: Describes the requirements for linking to virtual link
  tosca.nodes.nfv.VduCp:
     derived_from: tosca.nodes.nfv.Cp
     description: describes network connectivity between a VNFC instance based on this VDU and an internal VL
     properties:
       bitrate_requirement:
         type: integer   # in bits per second
         description: Bitrate requirement in bit per second on this connection point
         required: false
         constraints:
           - greater_or_equal: 0
       virtual_network_interface_requirements:
         type: list
         description: Specifies requirements on a virtual network interface realising  the CPs instantiated from this CPD
         required: false
         entry_schema:
           type: tosca.datatypes.nfv.VirtualNetworkInterfaceRequirements
       order:
         type: integer
         description: The order of the NIC on the compute instance (e.g.eth2)
         required: false
         constraints:
           - greater_or_equal: 0
       vnic_type:
         type: string
         description: Describes the type of the virtual network interface realizing the CPs instantiated from this CPD
         required: false
         constraints:
         - valid_values: [ normal, macvtap, direct, baremetal, virtio-forwarder, direct-physical, smart-nic ]
     capabilities:
       trunk_binding: # This capability is available only the trunk_mode property value of this VduCp is “true” and there is at least one VduSubCp defined as subport of the same trunk.
         type: tosca.capabilities.nfv.TrunkBindable
         occurrences: [ 0, UNBOUNDED ]
     requirements:
       - virtual_link:
           capability: tosca.capabilities.nfv.VirtualLinkable
           relationship: tosca.relationships.nfv.VirtualLinksTo
           occurrences: [1, 1]
       - virtual_binding:
           capability: tosca.capabilities.nfv.VirtualBindable
           relationship: tosca.relationships.nfv.VirtualBindsTo
           node: tosca.nodes.nfv.Vdu.Compute
           occurrences: [0, 1]
  tosca.nodes.nfv.VnfVirtualLink:
    derived_from: tosca.nodes.Root
    description: Describes the information about an internal VNF VL
    properties:
      connectivity_type:
       type: tosca.datatypes.nfv.ConnectivityType
       description: Specifies the protocol exposed by the VL and the flow pattern supported by the VL
       required: true
      description:
       type: string
       description: Provides human-readable information on the purpose of the VL
       required: false
      test_access:
       type: list
       description: Test access facilities available on the VL
       required: false
       entry_schema:
        type: string
        constraints:
         - valid_values: [ passive_monitoring, active_loopback ]
      vl_profile:
       type: tosca.datatypes.nfv.VlProfile
       description: Defines additional data for the VL
       required: true
      monitoring_parameters:
       type: map #key: id
       entry_schema:
        type: tosca.datatypes.nfv.VirtualLinkMonitoringParameter
       description: Describes monitoring parameters applicable to the VL
       required: false
    capabilities:
      virtual_linkable:
       type: tosca.capabilities.nfv.VirtualLinkable
  tosca.nodes.nfv.VipCp:
    derived_from: tosca.nodes.nfv.Cp
    description: Describes a connection point to allocate one or a set of virtual IP addresses
    properties:
      dedicated_ip_address:
        type: boolean
        description: Indicates whether the VIP address shall be different from the addresses allocated to all associated VduCp instances or shall be the same as one of them.
        required: true
        default: true
      vip_function:
        type: string
        description: "Indicates the function the virtual IP address is used for: high availability or load balancing. When used for high availability, only one of the internal VDU CP instances or VNF external CP instances that share the virtual IP is bound to the VIP address at a time. When used for load balancing purposes all CP instances that share the virtual IP are bound to it."
        required: true
        constraints:
          - valid_values: [ high_availability, load_balance ]
    requirements:
      - target:
          capability: tosca.capabilities.Node
          node: tosca.nodes.nfv.VduCp
          relationship: tosca.relationships.DependsOn
          occurrences: [ 1, UNBOUNDED ]
      - virtual_link:
          capability: tosca.capabilities.nfv.VirtualLinkable
          relationship: tosca.relationships.nfv.VipVirtualLinksTo
          occurrences: [1, 1]
  tosca.nodes.nfv.VduSubCp:
    derived_from: tosca.nodes.nfv.VduCp
    description: describes network connectivity between a VNFC instance based on this VDU and an internal VL through a trunk port
    properties:
      segmentation_type:
        type: string
        description: Specifies the encapsulation type for the traffics coming in and out of the trunk subport.
        required: false
        constraints:
          - valid_values: [ vlan, inherit ]
      segmentation_id:
        type: integer
        description: Specifies the segmentation ID for the subport, which is used to differentiate the traffics on different networks coming in and out of the trunk port.
        required: false
        constraints:
          - greater_or_equal: 0
    requirements:
      - trunk_binding:
          capability: tosca.capabilities.nfv.TrunkBindable
          relationship: tosca.relationships.nfv.TrunkBindsTo
          node: tosca.nodes.nfv.VduCp
          occurrences: [1, 1]
group_types:
  tosca.groups.nfv.PlacementGroup:
    derived_from: tosca.groups.Root
    description: PlacementGroup is used for describing the affinity or anti-affinity relationship applicable between the virtualization containers to be created based on different VDUs, or between internal VLs to be created based on different VnfVirtualLinkDesc(s)
    properties:
      description:
       type: string
       description: Human readable description of the group
       required: true
    members: [ tosca.nodes.nfv.Vdu.Compute, tosca.nodes.nfv.VnfVirtualLink ]
policy_types:
  tosca.policies.nfv.InstantiationLevels:
    derived_from: tosca.policies.Root
    description: The InstantiationLevels type is a policy type representing all the instantiation levels of resources to be instantiated within a deployment flavour and including default instantiation level in term of the number of VNFC instances to be created as defined in ETSI GS NFV-IFA 011 [1].
    properties:
      levels:
       type: map # key: levelId
       description: Describes the various levels of resources that can be used to instantiate the VNF using this flavour.
       required: true
       entry_schema:
         type: tosca.datatypes.nfv.InstantiationLevel
       constraints:
         - min_length: 1
      default_level:
       type: string # levelId
       description: The default instantiation level for this flavour.
       required: false # required if multiple entries in levels
  tosca.policies.nfv.VduInstantiationLevels:
    derived_from: tosca.policies.Root
    description: The VduInstantiationLevels type is a policy type representing all the instantiation levels of resources to be instantiated within a deployment flavour in term of the number of VNFC instances to be created from each vdu.Compute. as defined in ETSI GS NFV-IFA 011 [1]
    properties:
      levels:
       type: map # key: levelId
       description: Describes the Vdu.Compute levels of resources that can be used to instantiate the VNF using this flavour
       required: true
       entry_schema:
        type: tosca.datatypes.nfv.VduLevel
       constraints:
         - min_length: 1
    targets: [ tosca.nodes.nfv.Vdu.Compute ]
  tosca.policies.nfv.VirtualLinkInstantiationLevels:
    derived_from: tosca.policies.Root
    description: The VirtualLinkInstantiationLevels type is a policy type representing all the instantiation levels of virtual link resources to be instantiated within a deployment flavour as defined in ETSI GS NFV-IFA 011 [1].
    properties:
      levels:
       type: map # key: levelId
       description: Describes the virtual link levels of resources that can be used to instantiate the VNF using this flavour.
       required: true
       entry_schema:
        type: tosca.datatypes.nfv.VirtualLinkBitrateLevel
       constraints:
         - min_length: 1
    targets: [ tosca.nodes.nfv.VnfVirtualLink ]
  tosca.policies.nfv.ScalingAspects:
    derived_from: tosca.policies.Root
    description: The ScalingAspects type is a policy type representing the scaling aspects used for horizontal scaling as defined in ETSI GS NFV-IFA 011 [1]
    properties:
      aspects:
       type: map # key: aspectId
       description: Describe maximum scale level for total number of scaling steps that can be applied to a particular aspect
       required: true
       entry_schema:
        type: tosca.datatypes.nfv.ScalingAspect
       constraints:
         - min_length: 1
  tosca.policies.nfv.VduScalingAspectDeltas:
    derived_from: tosca.policies.Root
    description: The VduScalingAspectDeltas type is a policy type representing the Vdu.Compute detail of an aspect deltas used for horizontal scaling, as defined in ETSI GS NFV-IFA 011 [1]
    properties:
      aspect:
       type: string
       description: Represents the scaling aspect to which this policy applies
       required: true
      deltas:
       type: map # key: scalingDeltaId
       description: Describes the Vdu.Compute scaling deltas to be applied for every scaling steps of a particular aspect.
       required: true
       entry_schema:
        type: tosca.datatypes.nfv.VduLevel
       constraints:
         - min_length: 1
    targets: [ tosca.nodes.nfv.Vdu.Compute ]
  tosca.policies.nfv.VirtualLinkBitrateScalingAspectDeltas:
    derived_from: tosca.policies.Root
    description: The VirtualLinkBitrateScalingAspectDeltas type is a policy type representing the VnfVirtualLink detail of an aspect deltas used for horizontal scaling, as defined in ETSI GS NFV-IFA 011 [1].
    properties:
      aspect:
       type: string
       description: Represents the scaling aspect to which this policy applies.
       required: true
      deltas:
       type: map # key: scalingDeltaId
       description: Describes the VnfVirtualLink scaling deltas to be applied for every scaling steps of a particular aspect.
       required: true
       entry_schema:
        type: tosca.datatypes.nfv.VirtualLinkBitrateLevel
       constraints:
         - min_length: 1
    targets: [ tosca.nodes.nfv.VnfVirtualLink ]
  tosca.policies.nfv.VduInitialDelta:
    derived_from: tosca.policies.Root
    description: The VduInitialDelta type is a policy type representing the Vdu.Compute detail of an initial delta used for horizontal scaling, as defined in ETSI GS NFV-IFA 011 [1].
    properties:
     initial_delta:
      type: tosca.datatypes.nfv.VduLevel
      description: Represents the initial minimum size of the VNF.
      required: true
    targets: [ tosca.nodes.nfv.Vdu.Compute ]
  tosca.policies.nfv.VirtualLinkBitrateInitialDelta:
    derived_from: tosca.policies.Root
    description: The VirtualLinkBitrateInitialDelta type is a policy type representing the VnfVirtualLink detail of an initial deltas used for horizontal scaling, as defined in ETSI GS NFV-IFA 011 [1].
    properties:
      initial_delta:
       type: tosca.datatypes.nfv.VirtualLinkBitrateLevel
       description: Represents the initial minimum size of the VNF.
       required: true
    targets: [ tosca.nodes.nfv.VnfVirtualLink ]
  tosca.policies.nfv.AffinityRule:
    derived_from: tosca.policies.Placement
    description: The AffinityRule describes the affinity rules applicable for the defined targets
    properties:
      scope:
       type: string
       description: scope of the rule is an NFVI_node, an NFVI_PoP, etc.
       required: true
       constraints:
        - valid_values: [ nfvi_node, zone, zone_group, nfvi_pop, network_link_and_node ]
    targets: [ tosca.nodes.nfv.Vdu.Compute, tosca.nodes.nfv.VnfVirtualLink, tosca.groups.nfv.PlacementGroup ]
  tosca.policies.nfv.AntiAffinityRule:
    derived_from: tosca.policies.Placement
    description: The AntiAffinityRule describes the anti-affinity rules applicable for the defined targets
    properties:
      scope:
       type: string
       description: scope of the rule is an NFVI_node, an NFVI_PoP, etc.
       required: true
       constraints:
        - valid_values: [ nfvi_node, zone, zone_group, nfvi_pop, network_link_and_node ]
    targets: [ tosca.nodes.nfv.Vdu.Compute, tosca.nodes.nfv.VnfVirtualLink, tosca.groups.nfv.PlacementGroup ]
  tosca.policies.nfv.SupportedVnfInterface:
   derived_from: tosca.policies.Root
   description:  this policy type represents interfaces produced by a VNF, the details to access them and the applicable connection points to use to access these interfaces
   properties:
     interface_name:
       type: string
       description: Identifies an interface produced by the VNF.
       required: true
       constraints:
         - valid_values: [ vnf_indicator, vnf_configuration, vnf_lcm_coordination ]
     details:
       type: tosca.datatypes.nfv.InterfaceDetails
       description: Provide additional data to access the interface endpoint
       required: false
   targets: [ tosca.nodes.nfv.VnfExtCp, tosca.nodes.nfv.VduCp ]
  tosca.policies.nfv.SecurityGroupRule:
    derived_from: tosca.policies.nfv.Abstract.SecurityGroupRule
    description: The SecurityGroupRule type is a policy type specified the matching criteria for the ingress and/or egress traffic to/from visited connection points as defined in ETSI GS NFV-IFA 011 [1].
    targets: [ tosca.nodes.nfv.VduCp, tosca.nodes.nfv.VnfExtCp ]
  tosca.policies.nfv.VnfIndicator:
    derived_from: tosca.policies.Root
    description: The VnfIndicator policy type is a base policy type for defining VNF indicator specific policies that define the conditions to assess and the action to perform when a VNF indicator changes value as defined in ETSI GS NFV-IFA 011 [1].
    properties:
      source:
        type: string
        description: Describe the source of the indicator.
        required: true
        constraints:
          - valid_values: [ vnf, em, both_vnf_and_em ]
    targets: [ tosca.nodes.nfv.VNF ]
  tosca.policies.nfv.VnfPackageChange:
    derived_from: tosca.policies.Root
    description: policy type specifying the processes and rules to be used for performing the resource related tasks, to change VNF instance to a different VNF Package (destination package)
    properties:
      selector:
        type: tosca.datatypes.nfv.VnfPackageChangeSelector
        description: Information to identify the source and destination VNFD for the change, and the related deployment flavours.
        required: true
      modification_qualifier:
        type: string
        description: Specifies the type of modification resulting from transitioning from srcVnfdId to dstVnfdId. The possible values are UP indicating that the destination VNF version is newer than the source version, DOWN indicating that the destination VNF version is older than the source version.
        constraints: [ valid_values: [ up, down ] ]
        required: true
      additional_modification_description:
        type: string
        description: Additional information to qualify further the change between the two versions.
        required: false
      component_mappings:
        type: list
        entry_schema:
          type: tosca.datatypes.nfv.VnfPackageChangeComponentMapping
        description: Mapping information related to identifiers of components in source VNFD and destination VNFD that concern to the change process.
        required: false
      destination_flavour_id:
        type: string
        description: Identifies the deployment flavour in the destination VNF package for which this change applies. The flavour ID is defined in the destination VNF package.
        required: true
      actions:
        type: list
        description: List of applicable supported LCM coordination action names (action_name) specified in this VNFD as a TOSCA policy of a type derived from tosca.policies.nfv.LcmCoordinationAction.
        required: false
        entry_schema:
          type: string
      referenced_coordination_actions:
        type: list
        description: List of names of coordination actions not specified within this VNFD as a TOSCA policy of a type derived from tosca.policies.nfv.LcmCoordinationAction.
        required: false
        entry_schema:
          type: string
  tosca.policies.nfv.LcmCoordinationAction:
    derived_from: tosca.policies.Root
    description: The LcmCoordinationAction type is a policy type representing the LCM coordination actions supported by a VNF and/or expected to be supported by its EM for a particular VNF LCM operation. This policy concerns the whole VNF (deployment flavour) represented by the topology_template and thus has no explicit target list.
    properties:
      action_name:
        type: string
        description: Coordination action name.
        required: true
      # action:  #represents a place holder for specifying actions of a VNF-specific type derived from tosca.datatypes.nfv.VnfLcmOpCoord
        # type: tosca.datatypes.nfv.VnfLcmOpCoord
        # description: Describes a set of information needed for coordination action in the VNF LCM operation.
        # required: true
  tosca.policies.nfv.LcmCoordinationsForLcmOperation:
    derived_from: tosca.policies.Root
    description: The LcmCoordinationsForLcmOperation type is a policy type representing supported LCM coordination actions associated to a VNF LCM operation. This policy concerns the whole VNF (deployment flavour) represented by the topology_template and thus has no explicit target list.
    properties:
      vnf_lcm_operation:
        type: string
        description: The VNF LCM operation the LCM coordination actions are associated with.
        required: true
        constraints:
          - valid_values: [instantiate, scale, scale_to_level, change_flavour, terminate, heal, operate, change_ext_conn, modify_info, create_snapshot, revert_to_snapshot ]
      actions:
        type: list
        description: List of applicable supported LCM coordination action names (action_name) specified in this VNFD as a TOSCA policy of a type derived from tosca.policies.nfv.LcmCoordinationAction.
        required: false
        entry_schema:
          type: string
      referenced_coordination_actions:
        type: list
        description: List of names of coordination actions not specified within this VNFD as a TOSCA policy of a type derived from tosca.policies.nfv.LcmCoordinationAction.
        required: false
        entry_schema:
          type: string
"""

#create file in http server directory.
if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
    with open(filename, "w") as file:
        file.write(etsi_nfv_sol001_vnfd_types)
        file.close()


MSA_API.task_success('VNFD TOSCA Sol001 schema was created successfully.', context, True)