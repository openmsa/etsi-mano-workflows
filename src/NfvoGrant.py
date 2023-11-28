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
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from custom.ETSI.BaseApi import BaseApi


class NfvoGrant(BaseApi):

    GRANT_URL = 'admin/grant'

    def nfvo_grant_delete(self, _grantId):
        _url = self.GRANT_URL + "/" + _grantId
        response = self.do_delete(_url)
        return response

    def nfvo_grant_get(self):
        _url = self.GRANT_URL
        response = self.do_get(_url)
        return response

    def nfvo_grant_all_delete(self):
        _url = self.GRANT_URL + "/all"
        response = self.do_delete(_url)
        return response