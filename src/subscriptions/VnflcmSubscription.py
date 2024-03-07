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
import requests
from requests.exceptions import HTTPError
from urllib3.exceptions import InsecureRequestWarning
from custom.ETSI.BaseApi import BaseApi
from custom.ETSI.subscriptions.BaseSubscription import BaseSubscription
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class VnflcmSubscription(BaseSubscription):
    SUBSCRIPTION_TYPE = 'VNFLCM'
    VERSION = 'v1'
    VNFLCM_SUB_RESOURCE_URL = 'vnflcm/' + VERSION + '/subscriptions'

    def get_subscriptions(self):
        return super().get_subscriptions(self.VNFLCM_SUB_RESOURCE_URL)
    
    def get_subscription_by_id(self, subscription_id):
        return super().get_subscription_by_id(self, subscription_id, self.VNFLCM_SUB_RESOURCE_URL)
    
    def delete_subscription(self, subscription_id):
        return super().delete_subscription(self, subscription_id, self.VNFLCM_SUB_RESOURCE_URL)
    
    def delete_subscription_force(self, subscription_id, timeout):
        return super().delete_subscription_force(subscription_id, self.VNFLCM_SUB_RESOURCE_URL, timeout)
    
    def get_subscription_ids_by_type(self, mano_subscription):
        return super().get_subscription_ids_by_type(self.SUBSCRIPTION_TYPE, mano_subscription)