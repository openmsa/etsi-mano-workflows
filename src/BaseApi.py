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
import os
import json
import requests
import base64
import hashlib
from requests.exceptions import HTTPError
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class BaseApi():

    headers =  {}             
    STATE = {"Informational": range(100,200),
             "Successful":    range(200,300),
             "Redirection":   range(300,400),
             "Client_Error":  range(400,500),
             "Server_Error":  range(500,600)
             }

    def __init__(self, hostname, port='80', root_url='/ubi-etsi-mano/', sol_version='2.6.1'):
        self.hostname = hostname
        self.port     = port
        self.base_url = "http://" + hostname + ":" + port + root_url
        self.state    = ""
        self.sol_version    = sol_version
    def do_get(self, _url):
        _url     = self.base_url + _url
        response = requests.request("GET", url=_url, headers=self.headers,
                                    data={}, verify=False)
        return self.r_check(response)
    
    def do_post(self, _url, _payload):
        _url     = self.base_url + _url
        _payload = json.dumps(_payload)
        response = requests.request("POST", url=_url, headers=self.headers,
                                    data=_payload, verify=False)
        return self.r_check(response)
   
    # this just duplicates do_post
    # check https://docs.python-requests.org/en/master/user/quickstart/#response-headers 
    def do_post_return_location(self, _url, _payload):
        _url     = self.base_url + _url
        _payload = json.dumps(_payload)
        response = requests.request("POST", url=_url, headers=self.headers,
                                    data=_payload, verify=False)
        return self.r_check(response)

    def do_patch(self, _url, _payload):
        _url                 = self.base_url + _url
        _headers             = self.headers
        _payload             = json.dumps(_payload)
        response = requests.request("PATCH", url=_url, headers=_headers,
                                    data=_payload, verify=False)
        # check the current step
        if response.status_code == 412:
            _etag    = json.loads(response.content)['detail'].split()[-1]
            _headers = self.headers
            _headers["If-Match"] = _etag
            response = requests.request("POST", url=_url, headers=_headers,
                                        data=_payload, verify=False)
        return self.r_check(response)

    def do_put(self, _url, _filename, descriptor_id):
        _url               = self.base_url + _url
        if descriptor_id is not None:
            _headers           = {**self.headers, 'X-Descriptor-Id': descriptor_id}
        else:
            _headers = self.headers
        del _headers['Content-Type']
        _headers['Accept'] = 'application/json'
        _name              = _filename.split('/')[-1] 
        _files             = {'file': ('_name', open(_filename, 'rb'))}
        response = requests.request("PUT", url=_url, headers=_headers,
                                    files=_files, verify=False)
        return self.r_check(response)
    
    def do_delete(self, _url):
        _url     = self.base_url + _url
        response = requests.request("DELETE", url=_url, headers=self.headers,
                                    data={}, verify=False)
        return self.r_check(response)

    def _get_token_from_keycloak(self, username, password, keycloak_url):
        _headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        _data_urlencode = {'grant_type': 'client_credentials', 'client_id': username, 'client_secret': password}
        
        response = requests.request("POST", url=keycloak_url.strip(), headers=_headers, data=_data_urlencode, verify=False)
        r_json = response.json()
        return r_json.get('access_token')

    def set_parameters(self, username, password, auth_mode='basic', keycloak_url='http://mano-auth:8080/auth/realms/mano-realm/protocol/openid-connect/token', content_type='application/json', data={}):
        self.username  = username
        self.password  = password
        userpass       = f"{username}:{password}"
        base64userpass = base64.b64encode(userpass.encode()).decode()
        authorization  = f'Basic {base64userpass}'
        	
        if auth_mode == 'oauth_v2' or auth_mode == 'oauth2':
            #Get token from keycloak server.
            userpass = self._get_token_from_keycloak(username, password, keycloak_url)
            authorization  = f'Bearer {userpass}'
        
        self.headers['Content-Type'] = content_type
        self.headers.update(Authorization=authorization)

    def r_check(self, _response):
        if _response.status_code in self.STATE["Informational"]:
            self.state = "WARNING"
        elif _response.status_code in self.STATE["Successful"]:
            self.state = "ENDED"
        elif _response.status_code in self.STATE["Redirection"]:
            self.state = "WARNING"
        elif _response.status_code in self.STATE["Client_Error"]:
            self.state = "FAIL"
        elif _response.status_code in self.STATE["Server_Error"]:
            self.state = "FAIL"
        else:
            self.state = "FAIL"
        return _response
