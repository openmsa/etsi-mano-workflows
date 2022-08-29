# etsi-mano-workflows
ETSI-MANO workflows

## Installation

### Mano Managed Entity Variables

#### NFVO
| NAME | VALUE | DESCRIPTION | Required|
| ------ | ------ | ----- | ------ |
| BASE_URL | /ubi-etsi-mano/ | | Yes |
| HTTP_PORT | 8100 | | Yes |
| PROTOCOL | http | | No (http by default)|
| SOL005_VERSION | 2.7.1 | | No |
| AUTH_MODE | basic | Two possible values: 'basic' or 'oauth_v2'. If 'oauth_v2' setted as value, 'SIGNIN_REQ_PAH' and 'TOKEN_XPATH' configuration variables must be added as well (as in the next two rows). | Yes |
| SIGNIN_REQ_PATH | http://192.168.1.23:8110/auth/realms/mano-realm/protocol/openid-connect/token  | Keyclok server URL allows to get the NFVO authentication. | No (basic), Yes (oauth_v2)|
| TOKEN_XPATH | /root/access_token | | No (basic), Yes (oauth_v2)|
| NS_PKG_FILTER_EXPRESSION | | Example: '&filter=(eq,nsdOnboardingState,ONBOARDED)' | No |
| VNF_PKG_FILTER_EXPRESSION | | This current filter value allows to get only the VNF Package where the attribute 'onboardingState' 'equals' 'ONBOARDED'. (e.g: '&filter=(eq,onboardingState,CREATED)') | No |

#### VNFM
| NAME | VALUE | DESCRIPTION |Required|
| ------ | ------ | ----- | ------ |
| BASE_URL | /ubi-etsi-mano/ | |Yes |
| HTTP_PORT | 8089 | |Yes |


### Workflows installation

```sh
cd /opt/fmc_repository/
git clone https://github.com/openmsa/etsi-mano-workflows.git
chown -R ncuser:ncuser ./etsi-mano-workflows
cd /opt/fmc_repository/Process/
ln -s ../etsi-mano-workflows etsi-mano-workflows
chown -R ncuser:ncuser etsi-mano-workflows
```

### Python libraries
#### For custom modules create softlink according to [the guide](https://ubiqube.com/wp-content/docs/2.4.1/developer-guide/developer-guide-single.html#_how_to_extend_the_sdk)

```sh
cd /opt/fmc_repository/Process/PythonReference/custom
ln -s /opt/fmc_repository/etsi-mano-workflows/src/ ETSI 
chown -R ncuser:ncuser ETSI
```



