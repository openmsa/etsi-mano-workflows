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
import time
from requests.exceptions import HTTPError
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from custom.ETSI.BaseApi import BaseApi


class VnfLcmOpOccsSol003(BaseApi):

    VNF_LCM_OP_OCCS_URL = "vnflcm/v1/vnf_lcm_op_occs"

    STATUS = {"STARTING": False,
              "PROCESSING": False,
              "COMPLETED": True,
              "FAILED_TEMP": True,
              "PARTIALLY_COMPLETED": True,
              "FAILED": True,
              "ROLLING_BACK": False,
              "ROLLED_BACK": True 
              } 

    def vnf_lcm_op_occs_operation_status_get(self, vnf_lcm_op_occ_id):
        _url = self.VNF_LCM_OP_OCCS_URL + "/" + vnf_lcm_op_occ_id
        response = self.do_get(_url)
        return response

    def vnf_lcm_op_occs_completion_wait(self, vnf_lcm_op_occ_id, timeout=60):
        vnf_lcm_op_occs = self.vnf_lcm_op_occs_operation_status_get(vnf_lcm_op_occ_id)
        state = vnf_lcm_op_occs.json()['operationState']

        while (timeout > 0):
            vnf_lcm_op_occs = self.vnf_lcm_op_occs_operation_status_get(vnf_lcm_op_occ_id)
            state = vnf_lcm_op_occs.json()['operationState']
            timeout -= 1
            time.sleep(1)
            if self.STATUS.get(state):
                break
            else:
                continue 

        return vnf_lcm_op_occs

    '''
    Get vnf_lcm_op_occs_id based on vnf_lcm_instance_id.
    '''
    def vnf_lcm_op_occs_get_id(self, vnf_lcm_instance_id):
        _url = self.VNF_LCM_OP_OCCS_URL
        response = self.do_get(_url)

        vnf_lcm_op_occ_id = ''

        for vnf_lcm_op_occs in response.json():
            vnf_instance_id = vnf_lcm_op_occs["vnfInstanceId"]

            if vnf_instance_id == vnf_lcm_instance_id:
                vnf_lcm_op_occ_id = vnf_lcm_op_occs['id']

        return vnf_lcm_op_occ_id

