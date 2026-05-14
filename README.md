# IBM Verify Identity Access Configuration Automation
This repository is used to configure IBM Verify Identity Access (IVIA), and IBM Security Verify Access (ISVA) using a 
yaml file of the required configuration. 

This project aims to allow administrators of a Verify Identity Access (IVIA) or IBM Security Verify Access (ISVA) 
deployment. The configuration is applied using the pyivia python module, which in turn uses the rest API. The 
[examples](https://lachlan-ibm.github.io/ibmvia_autoconf/examples.html) provides in-depth guides on how to use 
this automation tool.


## Documentation
Documentation for using this library can be found on 
[Verify Identity Access Automated Configurator's GitHub pages](https://lachlan-ibm.github.io/ibmvia_autoconf/index.html).


# Setup
## Optional Extras
This library uses the pip extras feature to install the kubernetes or docker-compose dependencies if they are required. 
The Kubernetes extra might be requyired if you are using the autoconf tool to restart the runtime containers, or if you 
are using a Secrets object to store parts of the configuration.

To install an extra, use the following syntax:
```bash
pip install ibmvia_autoconf[kubernetes]
```

Valid optional extra targets include: `kubernetes`, `docker-compose`, and `all`

## Environment
- `IVIA_CONFIG_BASE` :: directory which contains the YAML configuration file as well as any http template pages, PKI, 
                      mapping rules, ect.
- *depreciated* `ISVA_CONFIG_BASE` = directory which contains the YAML configuration file as well as any http template 
                      pages, PKI, mapping rules, ect.
- `IVIA_CONFIG_YAML` :: path to IVIA configuration yaml file. Path should be relative to `IVIA_CONFIG_BASE`
- *depreciated* `ISVA_CONFIG_YAML` :: path to IVIA configuration yaml file. Path should be relative to `IVIA_CONFIG_BASE`
- `IVIA_MGMT_BASE_URL` :: address to access IVIA LMI, eg. https://\<isva appliance\>:\<isva port\>. This property can 
                      also be specified in the configuration yaml file. If present, this property will take precedence.
- *depreciated* `ISVA_MGMT_BASE_URL` :: address to access IVIA LMI, eg. https://\<isva appliance\>:\<isva port\>. This 
                      property can also be specified in the configuration yaml file. If present, this property will 
                      take precedence.
- `IVIA_MGMT_USER` :: The user to perform configuration as. If not supplied then the provided password is used as an API 
                      access token.
- *depreciated* `ISVA_MGMT_USER` :: The user to perform configuration as. If not supplied then the provided password is 
                      used as an API access token.
- `IVIA_MGMT_PWD` :: administrator password for the administrator account performing configuration. This property can 
                      also be specified in the configuration yaml file. If present, this property will take precedence.
- *depreciated* `ISVA_MGMT_PWD` :: Password for the administrator account performing configuration. This 
                      property can also be specified in the configuration yaml file. If present, this property will 
                      take precedence.
- `IVIA_MGMT_OLD_PWD` :: If a password change for the administrator account (eg. from the default) is required, the old 
                      password can be specified with this environment variable. If present the administrator's password 
                      will be changed from `MGMT_OLD_PASSWORD` to `MGMT_PASSWORD`
- *depreciated* `ISVA_MGMT_OLD_PWD` :: if a password change for the administrator account (eg. from the default) is 
                      required, the old password can be specified with this environment variable. If present the 
                      administrator's password will be changed from `MGMT_OLD_PASSWORD` to `MGMT_PASSWORD`
- `IVIA_PUBLISH_SNAPSHOT_SLEEP` (optional) :: number of seconds to deplay after publishing a configuration snapshot.
                                              This property can be used to allow time for the configuration to be 
                                              replicated in the filesystem or for the configuration container to stabilize
                                              after publishing a snapshot.
- `IVIA_KUBERNETES_YAML_CONFIG` (optional) :: path to Kubernetes configuration yaml for kubernetes deployments. 
  - Note: If your kubernetes cluster requires mutual authentication (TLS) then a pem certificate file must also be 
          available to IBM VIA Configurator
  - Note: When run from a Kubernetes cluster a Service Account can be used in place of a YAML configuration file
- *depreciated* `ISVA_KUBERNETES_YAML_CONFIG` (optional) :: path to Kubernetes configuration yaml for kubernetes 
                      deployments. 
- `KUBERNETES_CLIENT_SLEEP` (optional) :: number of seconds to delay after requesting a restart of the runtime 
                                          containers managed by the automated configuration tool. Use this property to
                                          allow time for the runtime containers to fetch the latest snapshot and apply 
                                          the configuration.
- `IVIA_EXT_USER` :: The user to continue configuration as once the Management Authentication configuration has been 
                      applied. This may be required if you are using an external LDAP registry or OIDC identity provider
                      for management authentication. If external authentication has previously been configured, then
                      the credentials should be set as the `IVIA_MGMT_USER` and `IVIA_MGMT_PWD` properties.
- `IVIA_EXT_PWD` :: The administrator password (or API token) to authenticate to the IVIA LMI as `IVIA_EXT_USER`.
- `IVIA_CONFIGURATOR_LOG_LEVEL` :: The log level to use for the configurator. Default is `INFO`. Valid values are 
                                  `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `IVIA_CONFIGURATOR_LOG_FILE` :: The path to the log file to write to. If not specified, logs will be written to 
                                  stdout. This should be a fully qualified path.
- `IVIA_CONFIGURATOR_LOG_FORMAT` :: The format to use for the log messages. Default is `%(asctime)s - %(levelname)s - %(message)s"`.
                                If the format is set to ``json`` then the messages logged will be JSON parsible.
- `IVIA_TRACK_API_FAILURES` :: Enable or disable API failure tracking. Default is `true`. Set to `false` to disable.
                               When enabled, a summary of all failed API requests will be printed at the end of
                               execution. If `ISVA_CONFIGURATOR_LOG_FORMAT` is set to `json`, the summary will be
                               output in JSON format.


## Deployment
### Local environment
IBM Verify Identity Access Configuration Automation is simple to run locally. 
1. Install the required python packages from [PyPi](https://pypi.org/project/ibmvia-autoconf/). 
2. Set the required environment variables
3. Invoke the python module from the command line.
```bash
python -m ibmvia_autoconf
```

### Docker (Compose)
- Requires the `docker-compose` pip package.
IBM Verify Identity Access Automated Configurator can also be run within a docker container. Use to 
[Dockerfile](Dockerfile) to build a local docker image.

The docker container can be built and run with the following command executed from the top level directory of the 
configurator source code. When starting the container the required environment variables must be set and the docker 
container must be able to route to the IVIA appliances/containers which are to be configured.

```
docker build --no-cache --force-rm -t verify-identity-access-configurator .

docker run --volume /path/to/config/yaml:/config \
            --env "IVIA_CONFIGURATION_BASE_DIR=/config" \
            --env IVIA_MGMT_BASE_URL="https://<mgmt address>:<mgmt port>" \
            --env "IVIA_MGMT_PASSWORD=Passw0rd1!" \
            verify-identity-access-configurator
```


### Kubernetes
- Requires the `kubernetes` pip package.
IBM Verify Identity Access Automated Configurator can be run from within a Kubernetes cluster. This is useful if there 
are routing issues between the deployment host and the kubernetes external addresses this option will allow for 
configuration using the kubernetes internal network.

Here is an example Kubernetes batch" object which deploys a container to apply a configuration to a cluster.
> note This requires a user to create the `verify-config` ConfigMap object with the required configuration files plus 
any additional Secrets which are referenced as environment variables.

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

# Troubleshooting install
In some python environments you may encounter erros like the following
```
AttributeError: cython_sources
```
To resolve this, install `setuptools` and then install `ibmvia_autoconf` with the `--no-build-isolation`
flag:
```
pip install setuptools
pip install --no-build-isolation ibmvia_autoconf
```


