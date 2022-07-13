# etsi-mano-workflows
ETSI-MANO workflows

## Installation

### Mano Managed Entity Variables

#### NFVO
| NAME | VALUE |
| ------ | ------ |
| BASE_URL | /ubi-etsi-mano/ |
| HTTP_PORT | 8100 |
| SOL005_VERSION | 2.7.1 |

#### VNFM
| NAME | VALUE |
| ------ | ------ |
| BASE_URL | /ubi-etsi-mano/ |
| HTTP_PORT | 8089 |


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
ln -s /opt/fmc_repository/etsi-mano-workflows/Python/src/ etsi-mano-sdk
chown -R ncuser:ncuser etsi-mano-sdk
```



