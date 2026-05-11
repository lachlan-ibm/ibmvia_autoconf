.. ibmvia-autoconf documentation master file, created by
   sphinx-quickstart on Tue Jul 19 14:23:54 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ibmvia-autoconf documentation!
##########################################
ibmvia-autoconf is an automation layer written on top of pyIVIA. This library should be used to apply 
YAML configuration files to a Verify Identity Access deployment.

This library is designed to work with both Appliance and Container based deployments, and is not idempotent.

Configuration is supplied in YAML syntax using a well-defined data structure (detailed in this doc).


Installation
============
You can install ``ibmvia-autoconf`` with ``pip``:

.. code-block:: console

    $ pip install ibmvia-autoconf


If you require the extra dependencies (for example using K8S secrets to store sensitive properties) you can install with:

.. code-block:: console

    $ pip install ibmvia-autoconf[kubernetes]


or


.. code-block:: console

    $ pip install ibmvia-autoconf[all]



.. _ibmvia_autoconf_architecture:

Architecture
============

Users should take care to ensure the configuration of these separate features are compatible (eg. conflicting ALC's
in a WebSEAL reverse proxy). Administrators will also have to define the ``webseal.runtime`` entry for many configuration
options even if the :ref:`WebSEAL Runtime Component<webseal_runtime_server>` is already configured.

Example configurations can be found in the ``examples`` directory with additional documentation in the 
`Examples / Getting Started <examples.html>`_ page.

Strategies on how administrators can attempt idempotency are documented `here <idempotency.html>`_.


Modules
_______

The configuration process is broken into six modules. Each module is responsible for configuring a subset of
Verify Identity Access features. The order of configuration is:

- base (Licensing, SSL Databases, Cluster Settings)
- appliance (if applicable)
- container (if applicable)
- federations
- webseal
- access control

This ordering has been chosen to allow for modules which depend on each-other to be deployed in the correct 
order. 

More complex deployment architectures can be achieved by running sequential ``config.yaml`` descriptors.


API Failure Tracking
____________________

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


Example Output (Human-Readable Format)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

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
Example Output (JSON Format)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``ISVA_CONFIGURATOR_LOG_FORMAT=json``:

.. code-block:: json

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



.. _ibmvia_autoconf_yaml_keywords:

YAML configuration keywords
============================

Each module expects a YAML object describing the desired configuration state. There are a number of useful features 
which can be used to make configuration files re-usable and version controlled. There are three keywords which 
can be used in configuration files:

 - ``!include``
    Used to include a YAML configuration file as the value of the given key. This file can be either an 
    absolute path or relative to the ``IVIA_CONFIG_BASE`` environment variable. eg::

                                                                                    container: !include base_config.yaml
                                                                                    webseal: !include webseal.yaml
                                                                                    access_control: !include aac.yaml

 - ``!secret``
    Used to set the value of the given key as a value read from the given Kubernetes Secret Namespace/Name,
    eg::

        admin_password: !secret default/isva-secrets:admin_secret

 - ``!environment``: 
    Used to set the value of the given key as the value read from the given environment variable,
    eg::

        admin_password: !environment IVIA_ADMIN_SECRET


.. _ibmvia_autoconf_env_vars:

Environment properties
======================

In addition to the supplied YAML configuration, some properties can alternatively be set as environment variables. If
these variables are set, they take priority over values set in configuration files.

- ``IVIA_CONFIG_BASE``
                        This variable is the root directory of all configuration files for the given Verify Identity Access 
                        Deployment. This can include: YAML configuration files; HTML template pages; JavaScript mapping
                        rules; XML configuration files.
                        
                        .. note:: If this environment variable is not set then the user's ``$HOME`` directory is used.

- ``IVIA_CONFIG_YAML``
                        This variable defines the YAML configuration file to deploy. This can be either relative
                        to the ``IVIA_CONFIG_BASE`` directory or an absolute file path. If this variable is not defined 
                        then the configuration will look for a file called ``config.yaml`` in the ``IVIA_CONFIG_BASE``
                        directory.

- ``IVIA_MGMT_BASE_URL``
                        This variable is the URL address that Verify Identity Access Local Management Interface is responding 
                        on. This should contain: the https scheme; the domain or IP address; and a port if not the 
                        standard (443) port. eg: ``https://127.0.0.2:9443``.

- ``IVIA_MGMT_USER``
                        The user to perform configuration as. This user should have sufficient permissions to configure 
                        all of the features in your YAML configuration file. If a username is not supplied then the 
                        ``IVIA_MGMT_PWD`` value is used as a bearer API access token.

- ``IVIA_MGMT_PWD``
                        The password or API access token required to authenticate.

- ``IVIA_MGMT_OLD_PWD``
                        If a password change is required then this variable defines the password for ``IVIA_MGMT_USER``
                        before the configuration is applied.

- ``IVIA_EXT_USER``
                        If external (federated) authentication to the management interface is configured, 
                        this property can be used to define the external user to perform configuration as
                        once the ``management_authorization`` feature has been configured.

- ``IVIA_EXT_PWD``
                        If external (federated) authentication to the management interface is configured, 
                        this property can be used to define the external password to authenticate with
                        once the ``management_authorization`` feature has been configured.

- - ``IVIA_PUBLISH_SNAPSHOT_SLEEP`` 
                        The number of seconds to delay after publishing a configuration snapshot. This property can 
                        be used to allow time for the configuration to be replicated in the filesystem or for the 
                        configuration container to stabilize after publishing a snapshot.

- ``IVIA_KUBERNETES_YAML_CONFIG``
                        This variable defines the Kubernetes cluster configuration file required to run ``kubectl``
                        commands. This configuration file should have sufficient permission in your cluster to restart 
                        deployments and pods in the namespace that Verify Identity Access is deployed to.
                        The file path can either be absolute or relative to the ``IVIA_CONFIG_BASE`` variable.

                        .. note:: This is only applicable for Container deployments using Kubernetes orchestration.

- ``KUBERNETES_CLIENT_SLEEP`` 
                        The number of seconds to delay after requesting a restart of the runtime containers managed by 
                        the automated configuration tool. Use this property to allow time for the runtime containers 
                        to fetch the latest snapshot and apply the configuration.

- ``IVIA_DOCKER_COMPOSE_CONFIG``
                        This variable defines the Docker-Compose deployment configuration file required to run
                        ``docker-compose`` commands for your Verify Identity Access deployment. This file path can 
                        either be absolute or relative to the ``IVIA_CONFIG_BASE`` variable.

                        .. note:: This is only applicable for Container deployments using Docker-Compose orchestration.

- ``IVIA_CONFIGURATOR_LOG_LEVEL``
                        This variable set the logging level for the autoconf tool. The default log level is ``INFO``. Valid 
                        values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.

- ``ISVA_CONFIGURATOR_LOG_FILE``
                        The path to the log file to write to. If not specified, logs will be written to stdout. This 
                        should be a fully qualified path.

- ``ISVA_CONFIGURATOR_LOG_FORMAT``
                        The format to use for the log messages. Default is `%(asctime)s - %(levelname)s - %(message)s"`.
                        If the format is set to ``json`` then the messages logged will be JSON parsible.

- ``IVIA_TRACK_API_FAILURES``
                        If set to ``true``, the autoconf tool will track API failures and summarize them before the tool 
                        exits. Default is ``true``.

- ``ISVA_CONFIGURATOR_LOG_FORMAT``
                        The format to use for the log messages. Default is `%(asctime)s - %(levelname)s - %(message)s"`.
                        If the format is set to ``json`` then the messages logged will be JSON parsible.

- ``IVIA_CONFIGURATOR_LOG_FILE``
                        The path to the log file to write to. If not specified, logs will be written to stdout. This 
                        should be a fully qualified path.


Detailed information on configuration object structure can be found in the submodule documentation

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   appliance
   container
   webseal
   access_control
   federations


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
