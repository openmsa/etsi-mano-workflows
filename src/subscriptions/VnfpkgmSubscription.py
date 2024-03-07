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
import logging
import requests
from requests.exceptions import HTTPError
from urllib3.exceptions import InsecureRequestWarning
from custom.ETSI.BaseApi import BaseApi
from custom.ETSI.subscriptions.BaseSubscription import BaseSubscription
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

FORMAT = "%(asctime)-15s %(clientip)s %(user)-8s %(message)s"
FILENAME= './manoSubscriptionVnfpkgm.log'
logging.basicConfig(format=FORMAT, filename=FILENAME, level=logging.DEBUG)



class VnfpkgmSubscription(BaseSubscription):

    SUBSCRIPTION_TYPE = 'VNF'
    VERSION = 'v1'
    SOL_VERSION = "sol003"
    VNFPKGM_SUB_RESOURCE_URL = SOL_VERSION + '/vnfpkgm/' + VERSION + '/subscriptions'

    def get_subscriptions(self):
        return super().get_subscriptions(self.VNFPKGM_SUB_RESOURCE_URL)
    
    def get_subscription_by_id(self, subscription_id):
        return super().get_subscription_by_id(self, subscription_id, self.VNFPKGM_SUB_RESOURCE_URL)
    
    def delete_subscription(self, subscription_id):
        return super().delete_subscription(self, subscription_id, self.VNFPKGM_SUB_RESOURCE_URL)
    
    def delete_subscription_force(self, subscription_id, timeout):
        return super().delete_subscription_force(subscription_id, self.VNFPKGM_SUB_RESOURCE_URL, timeout)
        
    def get_subscription_ids_by_type(self, mano_subscription):
        return super().get_subscription_ids_by_type(self.SUBSCRIPTION_TYPE, mano_subscription)