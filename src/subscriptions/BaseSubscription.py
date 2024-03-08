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
import time
from custom.ETSI.BaseApi import BaseApi

class BaseSubscription(BaseApi):

    def __get_subscription_by_id(self, subscription_id, _vnf_subscription_base_url):
        response = self.do_get(_vnf_subscription_base_url)

        if self.state == 'FAIL':
            return response.json()
        
        subscription = ''
        for index, item in enumerate(response.json()):
            if 'id' in item:
                item_subscription_id = item['id']
                if item_subscription_id == subscription_id:
                    subscription = item
                    break
        return subscription
    
    def __delete_subscription(self, _subscription_id, _subscription_resource_url):
        _url = _subscription_resource_url + "/" + _subscription_id
        response = self.do_delete(_url)
        return response
    
    def get_subscriptions(self, _subscription_resource_url):
        response = self.do_get(_subscription_resource_url)
        return response
    
    def get_subscription_by_id(self, _subscription_id, _subscription_resource_url):
        return self.__get_subscription_by_id(_subscription_id, _subscription_resource_url)
    
    def delete_subscription(self, _subscription_id, _subscription_resource_url):
        return self.__delete_subscription(_subscription_id, _subscription_resource_url)
    
    def delete_subscription_force(self, _subscription_id, _subscription_resource_url, _time_out):
        r = self.__delete_subscription(_subscription_id, _subscription_resource_url)
        while (_time_out > 0):
            # Get subscription details from remote server.
            subscription = self.__get_subscription_by_id(_subscription_id, _subscription_resource_url)
            # If subscription still exists, loop and atempt to remove it.
            if subscription and isinstance(subscription, dict):
                # Delete subscription in the remote server.
                self.__delete_subscription(_subscription_id, _subscription_resource_url)
                _time_out -= 1
                time.sleep(1)
            else:
                break
        
        return subscription 
    
    '''
    Get subscription ids by type from remoteSubscription object.
    @param subscription_type - String value (e.g: VNFIND, VNFLCM).
    @param mano_subscription - dict of nfvo or vnfm subscription object.
    return - list of subscription ids
    '''
    def get_subscription_ids_by_type(self, subscription_type, mano_subscription):
        # Init subscription ids list.
        subscription_ids = list()
        
        # Get remoteSubscriptions list.
        mano_subscription_list = mano_subscription.get('remoteSubscriptions')

        #Iterate list and delete matched subscriptions.
        for index, item in enumerate(mano_subscription_list):
            # Fetch and compare the subscription type from remoteSubscription object.
            if not 'subscriptionType' in item:
                continue
            if item.get('subscriptionType') != subscription_type:
                continue
            #Get subscription id from remoteSubscription object.
            if not 'remoteSubscriptionId' in item:
                continue
            if not item.get('remoteSubscriptionId'):
                continue
            subscription_id = item.get('remoteSubscriptionId')
            subscription_ids.append(subscription_id)
            
        return subscription_ids