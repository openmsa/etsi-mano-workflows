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


class NfviVim(BaseApi):

    VIM_URL = 'admin/vim'

    def nfvi_vim_register(self, _payload):
        _url = self.VIM_URL + '/register'
        response = self.do_post(_url, _payload)
        return response

    def nfvi_vim_delete(self, _vimId):
        _url = self.VIM_URL + "/" + _vimId
        response = self.do_delete(_url)
        return response

    def nfvi_vim_get(self):
        _url = self.VIM_URL
        response = self.do_get(_url)
        return response

    def nfvi_vim_register_update(self, vimId, _payload):
        _url = self.VIM_URL + '/' + vimId
        response = self.do_patch(_url, _payload)
        return response