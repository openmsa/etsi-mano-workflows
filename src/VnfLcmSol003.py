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


class VnfLcmSol003(BaseApi):

    #NSLCM_BASE_URL = 'sol003/vnflcm/v1/vnf_instances'
    NSLCM_BASE_URL = 'vnflcm/v1/vnf_instances'

    def vnf_lcm_create_instance(self, _payload):
        response = self.do_post(self.NSLCM_BASE_URL, _payload)
        return response

    def vnf_lcm_instantiate_vnf(self, vnf_instance_id, _payload={}):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id + "/instantiate"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_terminate_vnf(self, vnf_instance_id, _payload={}):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id + "/terminate"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_delete_instance_of_vnf(self, vnf_instance_id):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id
        response = self.do_delete(_url)
        return response

    def vnf_lcm_scale_to_level_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id + "/scale_to_level"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_scale_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id + "/scale"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_heal_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id + "/heal"
        response = self.do_post_return_location(_url, _payload)
        return response

    def vnf_lcm_operate_instance_vnf(self, vnf_instance_id, _payload):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id + "/operate"
        response = self.do_post_return_location(_url, _payload)
        return response
    def vnf_lcm_get_vnf_instance_details(self, vnf_instance_id):
        _url = self.NSLCM_BASE_URL + "/" + vnf_instance_id
        response = self.do_get(_url)
        return response
