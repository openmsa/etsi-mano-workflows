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


class DescriptorGraphGeneration(BaseApi):

    ADMIN_URL = 'v3'

    def vnf_graph_tolopology_generation(self, vnf_id):
        _url = self.ADMIN_URL + '/plan/vnf/2d/' + vnf_id
        response = self.do_get(_url)
        return response

    def ns_graph_tolopology_generation(self, nsd_id):
        _url = self.ADMIN_URL + "/plan/ns/2d/" + nsd_id
        response = self.do_get(_url)
        return response

