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


class NfvoVnfmSubscription(BaseApi):

    SUBSCRIPTION_URL = 'admin/server'

    STATUS = {"NOT_STARTED": False,
              "REMOVED": False,
              "STARTED": False,
              "SUCCESS": True,
              "FAILED": True,
              }

    def subscribe(self, _payload):
        _url = self.SUBSCRIPTION_URL
        response = self.do_post(_url, _payload)
        return response
    
    def unsubscribe(self, server_id):
        _url = self.SUBSCRIPTION_URL + '/' + server_id
        response = self.do_delete(_url)
        return response
    

    def subscribe_get_status(self, server_id):
        _url = self.SUBSCRIPTION_URL
        response = self.do_get(_url)
        
        subscription = ''
        for index, item in enumerate(response.json()):
            if 'id' in item:
                item_server_id = item['id']
                if item_server_id == server_id:
                    subscription = item
                    break
        return subscription

    def subscribe_completion_wait(self, server_id, timeout=60):
        subscription = self.subscribe_get_status(server_id)
        state = subscription['serverStatus']

        while (timeout > 0):
            subscription = self.subscribe_get_status(server_id)
            state = subscription['serverStatus']
            timeout -= 1
            time.sleep(1)
            if self.STATUS.get(state):
                break
            else:
                continue

        return subscription 
