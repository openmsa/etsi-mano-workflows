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
import time
import json
import requests
from requests.exceptions import HTTPError
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from custom.ETSI.BaseApi import BaseApi


class NsLcmOpOccsSol005(BaseApi):

    NS_LCM_PO_OCCS = "sol005/nslcm/v1/ns_lcm_op_occs"

    STATUS = {"STARTING": False,
              "PROCESSING": False,
              "COMPLETED": True,
              "FAILED_TEMP": True,
              "PARTIALLY_COMPLETED": True,
              "FAILED": True,
              "ROLLING_BACK": False,
              "ROLLED_BACK": True 
              }

    def ns_lcm_op_occs_operation_status_get(self, ns_lcm_op_occ_id):
        _url = self.NS_LCM_PO_OCCS + "/" + ns_lcm_op_occ_id
        response = self.do_get(_url)
        return response

    def ns_lcm_op_occs_completion_wait(self, ns_lcm_op_occ_id, timeout=60):
        ns_lcm_op_occs = self.ns_lcm_op_occs_operation_status_get(ns_lcm_op_occ_id)
        state = ns_lcm_op_occs.json()['operationState']

        while (timeout > 0):
            ns_lcm_op_occs = self.ns_lcm_op_occs_operation_status_get(ns_lcm_op_occ_id)
            state = ns_lcm_op_occs.json()['operationState']
            timeout -= 1
            time.sleep(1)
            if self.STATUS.get(state):
                break
            else:
                continue 

        return ns_lcm_op_occs
