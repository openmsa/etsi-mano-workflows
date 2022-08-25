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

