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
import os

class ManoProtocolsVersion():

    MANO_PROTOCOL_BASE_DIR = os.path.dirname(os.path.realpath(__file__)) + '/mano-proto'
    MANO_PROTO_RESOURCE_PATH = "resources"
    MANO_PROTO_FILENAME = "mano-versions.json" 

    def get_fragment_versions(self, protocol, protocol_version, fragment):
        mano_version_file     = self.MANO_PROTOCOL_BASE_DIR + "/" + protocol_version + "/" + self.MANO_PROTO_RESOURCE_PATH + "/" + protocol_version + "/" + self.MANO_PROTO_FILENAME
        data = dict()        
        with open(mano_version_file) as f:
            data = json.load(f)
            
        #loop in the protocal object list.
        for d in data:
            #
            _version  = d.get('version')
            _protocol = d.get('protocol')
            
            if _protocol == protocol and _version == protocol_version:
                fragment_list = d.get('protocols')
                for fragment_obj in fragment_list:
                    frag = fragment_obj.get('fragment')
                    header_v = fragment_obj.get('version')
                    
                    if frag == fragment:
                        frag_v = header_v[:1]
                        return {'fragment_version': frag_v,'header_version': header_v}
        return {}
