# IBM Verify Identity Access Configuration Automation
This repository is used to configure IBM Verify Identity Access (IVIA), and IBM Security Verify Access (ISVA) using a yaml file of the required configuration. 

This project aims to be idempotent, ie if the configuration is run multiple times on the same appliance it should not break and should pick up any configuration changes in the yaml configuration file.


## Documentation
Documentation for using this library can be found on [Verify Identity Access Automated Configurator's GitHub pages](https://lachlan-ibm.github.io/ibmvia_autoconf/index.html).


## Example deployments
To get started several example deployments are available in the [Examples](examples/) directory. The example yaml files must be updated with deployment specific parameters, usually this is network addresses and IVIA activation codes.

# Setup
## Environment
- `IVIA_CONFIG_BASE` = directory which contains the YAML configuration file as well as any http template pages, PKI, mapping rules, ect.
- *depreciated* `ISVA_CONFIG_BASE` = directory which contains the YAML configuration file as well as any http template pages, PKI, mapping rules, ect.
- `IVIA_CONFIG_YAML` = path to IVIA configuration yaml file. Path should be relative to `IVIA_CONFIG_BASE`
- *depreciated* `ISVA_CONFIG_YAML` = path to IVIA configuration yaml file. Path should be relative to `IVIA_CONFIG_BASE`
- `IVIA_MGMT_BASE_URL` = address to access IVIA LMI, eg. https://\<isva appliance\>:\<isva port\>. This property can also be specified in the configuration yaml file. If present, this property will take precedence.
- *depreciated* `ISVA_MGMT_BASE_URL` = address to access IVIA LMI, eg. https://\<isva appliance\>:\<isva port\>. This property can also be specified in the configuration yaml file. If present, this property will take precedence.
- `IVIA_MGMT_USER` = The user to perform configuration as. If not supplied the `admin` user is used.
- *depreciated* `ISVA_MGMT_USER` = The user to perform configuration as. If not supplied the `admin` user is used.
- `IVIA_MGMT_PWD` = administrator password for the administrator account performing configuration. This property can also be specified in the configuration yaml file. If present, this property will take precedence.
- *depreciated* `ISVA_MGMT_PWD` = administrator password for the administrator account performing configuration. This property can also be specified in the configuration yaml file. If present, this property will take precedence.
- `IVIA_MGMT_OLD_PWD` = if a password change for the administrator account (eg. from the default) is required, the old password can be specified with this environment variable. If present the administrator's password will be changed from `MGMT_OLD_PASSWORD` to `MGMT_PASSWORD`
- *depreciated* `ISVA_MGMT_OLD_PWD` = if a password change for the administrator account (eg. from the default) is required, the old password can be specified with this environment variable. If present the administrator's password will be changed from `MGMT_OLD_PASSWORD` to `MGMT_PASSWORD`
- `IVIA_KUBERNETES_YAML_CONFIG` (optional) = path to Kubernetes configuration yaml for kubernetes deployments. 
  - Note: If your kubernetes cluster requires mutual authentication (TLS) then a pem certificate file must also be available to IBM VIA Configurator
  - Note: When run from a Kubernetes cluster a Service Account can be used in place of a YAML configuration file
- *depreciated* `ISVA_KUBERNETES_YAML_CONFIG` (optional) = path to Kubernetes configuration yaml for kubernetes deployments. 

## Deployment
### Local environment
IBM Verify Identity Access Configuration Automation is simple to run locally. 
1. Install the required python packages from [PyPi](https://pypi.org/project/ibmvia-autoconf/). 
2. Set the required environment variables
3. Invoke the python module from the command line.
```bash
python -m ibmvia_autoconf
```

### Docker
IBM Verify Identity Access Automated Configurator can also be run within a docker container. Use to [Dockerfile](Dockerfile) to build a local docker image.

The docker container can be built and run with the following command executed from the top level directory of the configurator source code. When starting the container the required environment variables must be set and the docker container must be able to route to the IVIA appliances/containers which are to be configured.

```
docker build --no-cache --force-rm -t verify-identity-access-configurator .

docker run --volume /path/to/config/yaml:/config \
            --env "IVIA_CONFIGURATION_BASE_DIR=/config" \
            --env IVIA_MGMT_BASE_URL="https://<mgmt address>:<mgmt port>" \
            --env "IVIA_MGMT_PASSWORD=Passw0rd1!" \
            verify-identity-access-configurator
```


### Kubernetes
IBM Verify Identity Access Automated Configurator can be run from within a Kubernetes cluster. This is useful if there are routing issues between the deployment host and the kubernetes external addresses this option will allow for configuration using the kubernetes internal network.

Here is an example Kubernetes batch" object which deploys a container to apply a configuration to a cluster.
> note This requires a user to create the `verify-config` ConfigMap object with the required configuration files plus any additional Secrets which are referenced as environment variables.

```
apiVersion: batch/v1
kind: Job
metadata:
  name: verify-identity-access-configurator
spec:
  template:
    spec:
      containers:
      - name: verify-identity-access-configurator
        image: python:latest
        command: 
        - "bash"
        - "-c"
        - |
          pip install ibmvia-autoconf
          python3 -m ibmvia_autoconf
        volumeMounts:
        - name: verify-access-config-vol
          mountPath: /verify_access_config
        envFrom:
        - secretRef:
            name: verify-access-autoconf-env
      restartPolicy: Never
      volumes:
      - name: verify-config
        configMap:
      - name: verify-access-config-vol
        emptyDir: {}
      initContainers:
      - name: config-volume-builder
        image: python:latest
        volumeMounts:
        - mountPath: /verify_access_config
          name: verify-access-config-vol
        - mountPath: /tmp/verify_access_config
          name: verify-config
        command:
        - "bash"
        - "-c"
        - |
          apt update && apt install -y unzip;
          cp /tmp/verify_access_config/*.{p12,pem,yaml} /verify_access_config/
          unzip /tmp/verify_access_config/mapping_rules.zip -d /verify_access_config/
  backoffLimit: 4
```

# Building

To build locally:
```sh
mkdir .pyenv
virtualenv .pyenv
source .pyenv/bin/activate
pip install -r dev-requirements.txt
python setup.py sdist bdist_wheel
```
The generated wheel can then be installed into a docker container and used in any supported container runtime.
