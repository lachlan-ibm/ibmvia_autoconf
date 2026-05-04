# IBM Verify Identity Access Configuration Automation
This repository is used to configure IBM Verify Identity Access (IVIA), and IBM Security Verify Access (ISVA) using a 
yaml file of the required configuration. 

This project aims to be idempotent, ie if the configuration is run multiple times on the same appliance it should not 
break and should pick up any configuration changes in the yaml configuration file.


## Documentation
Documentation for using this library can be found on 
[Verify Identity Access Automated Configurator's GitHub pages](https://lachlan-ibm.github.io/ibmvia_autoconf/index.html).


## Example deployments
To get started several example deployments are available in the [Examples](examples/) directory. The example yaml files 
must be updated with deployment specific parameters, usually this is network addresses and IVIA activation codes.

# Setup
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
- `ISVA_CONFIGURATOR_LOG_LEVEL` :: The log level to use for the configurator. Default is `INFO`. Valid values are 
                                  `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `ISVA_CONFIGURATOR_LOG_FILE` :: The path to the log file to write to. If not specified, logs will be written to 
                                  stdout. This should be a fully qualified path.
- `ISVA_CONFIGURATOR_LOG_FORMAT` :: The format to use for the log messages. Default is `%(asctime)s - %(levelname)s - %(message)s"`.
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

## API Failure Tracking

IBM Verify Identity Access Automated Configurator includes built-in tracking of failed API requests. When enabled 
(default), the configurator will collect information about any API calls that fail during execution and print a 
comprehensive summary at the end.

Captures context for each failure:
  - Module name and operation being performed
  - Error message from the API response
  - API endpoint that was called
  - HTTP status code
  - Full response content/data
  - Request payload/parameters sent
  - Timestamp of the failure
- Outputs summary grouped by module
- Supports both human-readable and JSON output formats
- Can be disabled via environment variable

### Configuration
- **Enable/Disable**: Set `IVIA_TRACK_API_FAILURES=false` to disable tracking (enabled by default)
- **JSON Output**: When `ISVA_CONFIGURATOR_LOG_FORMAT=json`, the summary will be output in JSON format

### Example Output (Human-Readable Format)
```
================================================================================
API FAILURE SUMMARY - 3 Failed Request(s)
================================================================================

Module: access_control (2 failure(s))
--------------------------------------------------------------------------------
  1. Operation: create_policy
     Error: Policy name already exists
     API Endpoint: /iam/access/v8/policies
     Status Code: 409
     Response: {'error': 'DUPLICATE_NAME', 'message': 'Policy name already exists'}
     Request Data: {'name': 'MyPolicy', 'type': 'authorization'}
     Timestamp: 2026-04-02T03:15:00.123Z

  2. Operation: update_pip
     Error: Connection timeout
     API Endpoint: /iam/access/v8/pips/123
     Status Code: 504
     Response: {'error': 'GATEWAY_TIMEOUT'}
     Timestamp: 2026-04-02T03:16:30.456Z

Module: webseal (1 failure(s))
--------------------------------------------------------------------------------
  1. Operation: create_junction
     Error: Backend server unreachable
     API Endpoint: /wga/reverseproxy/junctions
     Status Code: 502
     Response: {'error': 'BAD_GATEWAY', 'backend': 'https://backend.example.com'}
     Request Data: {'junction_point': '/app', 'server': 'backend.example.com'}
     Timestamp: 2026-04-02T03:18:00.012Z

================================================================================
```

### Example Output (JSON Format)
When `ISVA_CONFIGURATOR_LOG_FORMAT=json`:
```json
{
  "api_failure_summary": {
    "total_failures": 3,
    "by_module": {
      "access_control": 2,
      "webseal": 1
    }
  },
  "failures": [
    {
      "timestamp": "2026-04-02T03:15:00.123Z",
      "module": "access_control",
      "operation": "create_policy",
      "error_message": "Policy name already exists",
      "api_endpoint": "/iam/access/v8/policies",
      "status_code": 409,
      "response_content": {"error": "DUPLICATE_NAME", "message": "Policy name already exists"},
      "request_data": {"name": "MyPolicy", "type": "authorization"}
    },
    {
      "timestamp": "2026-04-02T03:16:30.456Z",
      "module": "access_control",
      "operation": "update_pip",
      "error_message": "Connection timeout",
      "api_endpoint": "/iam/access/v8/pips/123",
      "status_code": 504,
      "response_content": {"error": "GATEWAY_TIMEOUT"},
      "request_data": null
    },
    {
      "timestamp": "2026-04-02T03:18:00.012Z",
      "module": "webseal",
      "operation": "create_junction",
      "error_message": "Backend server unreachable",
      "api_endpoint": "/wga/reverseproxy/junctions",
      "status_code": 502,
      "response_content": {"error": "BAD_GATEWAY", "backend": "https://backend.example.com"},
      "request_data": {"junction_point": "/app", "server": "backend.example.com"}
    }
  ]
}
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


