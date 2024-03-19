# etsi-mano-workflows
ETSI-MANO workflows

## Installation

### Mano Managed Entity Variables

#### 1. NFVO
| NAME | VALUE (from v3.2.1 and latest)| VALUE (uat30 version) | DESCRIPTION | REQUIRED |
| ------ | ------ | ------ | ------ | ------ |
| AUTH_MODE | `oauth_v2` |  | Two possible values: 'basic' or 'oauth_v2'. If 'oauth_v2' set as value, 'SIGNIN_REQ_PAH' and 'TOKEN_XPATH' configuration variables must be added as well (as in the next two rows). | Yes |
| BASE_URL | `/nfvo-webapp/` |`/ubi-etsi-mano/` | | Yes |
| BASE_URL_MS | `/nfvo-webapp/sol005/` | `/ubi-etsi-mano/sol005/` | | Yes |
| HTTP_PORT | `8100` | | | Yes |
| PROTOCOL | `http` | | | No (https by default)|
| SIGNIN_REQ_PATH | `http://192.168.1.23:8110/auth/realms/mano-realm/protocol/openid-connect/token` | | Keycloak server URL allows to get the NFVO authentication. | No (basic), Yes (oauth_v2)|
| TOKEN_XPATH | `/root/access_token` | | | No (basic), Yes (oauth_v2)|
| SOL005_VERSION | `2.7.1` | | | No |
| SOL003_VERSION | `2.7.1` | | | No |
| NS_PKG_FILTER_EXPRESSION | | | Example: '&filter=(eq,nsdOnboardingState,ONBOARDED)' | No |
| VNF_PKG_FILTER_EXPRESSION | | | This current filter value allows to get only the VNF Package where the attribute 'onboardingState' 'equals' 'ONBOARDED'. (e.g: '&filter=(eq,onboardingState,CREATED)') | No |

#### 2. VNFM
| NAME | VALUE (from v3.2.1 and latest)| VALUE (uat30 version) | DESCRIPTION | REQUIRED |
| ------ | ------ | ------ | ------ | ------ |
| BASE_URL | `/vnfm-webapp/` | `/ubi-etsi-mano/` | |Yes |
| BASE_URL_MS | `/vnfm-webapp/sol003/` | `/ubi-etsi-mano/sol003/` | | Yes |
| AUTH_MODE | `oauth_v2` | | Two possible values: 'basic' or 'oauth_v2'. If 'oauth_v2' set as value, 'SIGNIN_REQ_PAH' and 'TOKEN_XPATH' configuration variables must be added as well (as in the next two rows). | Yes |
| HTTP_PORT | `8089` | | |Yes |
| SIGNIN_REQ_PATH | `http://192.168.1.23:8110/auth/realms/mano-realm/protocol/openid-connect/token` | | Keycloak server URL allows to get the NFVO authentication. | No (basic), Yes (oauth_v2)|
| TOKEN_XPATH | `/root/access_token` | | | No (basic), Yes (oauth_v2)|
| CAPABILITIES | `100:ubi-v2.6.1` | | The capabilities allow to assign VNF Descriptor (VNF Package) to a specific VNFM which is going to be in charge of the VNF lifecycle. This variable values have to be matched with the values defined in the VNF Descriptor. |Yes |
| SOL003_VERSION | `2.7.1` | | | No |

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



