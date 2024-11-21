# Copyright (C) 2019-2023  Ubiqube
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import requests
from requests.exceptions import HTTPError
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from custom.ETSI.BaseApi import BaseApi
from custom.ETSI.ManoProtocolsVersion import ManoProtocolsVersion    


class VnfLcmSol003(BaseApi):

    #VNF_LCM_URL = 'sol003/vnflcm/v1/vnf_instances'
    #VNF_LCM_URL = 'vnflcm/v1/vnf_instances'

    NFV_API_PROTOCOL = "sol003"
    NFV_RESOURCE_FRAGMENT = "vnflcm"
    VNF_LCM_URL = ""

    def __init__(self, hostname, port, base_url, sol_version='2.6.1'):
       super().__init__(hostname=hostname, port=port, root_url=base_url, sol_version=sol_version)

       _mano_proto_version_obj = ManoProtocolsVersion()
       data = _mano_proto_version_obj.get_fragment_versions(self.NFV_API_PROTOCOL, self.sol_version, self.NFV_RESOURCE_FRAGMENT)
       if 'fragment_version' in data:
           self.fragment_version = data.get('fragment_version')

       if 'header_version' in data:
           self.header_version = data.get('header_version')

       #update request header object by adding the header_version.
       self.headers.update(version=self.header_version)

       #self.VNF_LCM_URL = self.NFV_RESOURCE_FRAGMENT + "/v" + self.fragment_version + "/vnf_instances"
       self.VNF_LCM_URL = self.NFV_RESOURCE_FRAGMENT + "/v2/vnf_instances"
       
    def vnf_lcm_create_instance(self, _payload):
        response = self.do_post(self.VNF_LCM_URL, _payload)
        return response

    def vnf_lcm_instantiate_vnf(self, vnf_instance_id, _payload={}):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id + "/instantiate"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_terminate_vnf(self, vnf_instance_id, _payload={}):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id + "/terminate"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_delete_instance_of_vnf(self, vnf_instance_id):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id
        response = self.do_delete(_url)
        return response

    def vnf_lcm_scale_to_level_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id + "/scale_to_level"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_scale_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id + "/scale"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_heal_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id + "/heal"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_operate_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id + "/operate"
        response = self.do_post_return_location(_url, _payload)
        return response
    def vnf_lcm_get_vnf_instance_details(self, vnf_instance_id):
        _url = self.VNF_LCM_URL + "/" + vnf_instance_id
        response = self.do_get(_url)
        return response
