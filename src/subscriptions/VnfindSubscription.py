# Copyright (C) 2019-2024  UBiqube
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
from custom.ETSI.subscriptions.BaseSubscription import BaseSubscription


class VnfindSubscription(BaseSubscription):
    SUBSCRIPTION_TYPE = 'VNFIND'
    VERSION = 'v1'
    SOL_VERSION = 'sol003'
    VNF_INDICATOR_SUB_RESOURCE_URL = SOL_VERSION + '/vnfind/' + VERSION + '/subscriptions'

    def get_subscriptions(self):
        return super().get_subscriptions(self.VNF_INDICATOR_SUB_RESOURCE_URL)
    
    def get_subscription_by_id(self, subscription_id):
        return super().get_subscription_by_id(self, subscription_id, self.VNF_INDICATOR_SUB_RESOURCE_URL)
    
    def delete_subscription(self, subscription_id):
        return super().delete_subscription(self, subscription_id, self.VNF_INDICATOR_SUB_RESOURCE_URL)
    
    def delete_subscription_force(self, subscription_id, timeout):
        return super().delete_subscription_force(subscription_id, self.VNF_INDICATOR_SUB_RESOURCE_URL, timeout)
        
    def get_subscription_ids_by_type(self, mano_subscription):
        return super().get_subscription_ids_by_type(self.SUBSCRIPTION_TYPE, mano_subscription)