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


If you require the extra dependencies (for example using K8S secrets to store sensitive properties) you can 
install the optional targets ``kubernetes``, ``docker-compose``, or ``all``:

.. code-block:: console

    $ pip install ibmvia-autoconf[kubernetes]


or


.. code-block:: console

    $ pip install ibmvia-autoconf[all]



.. _ibmvia_autoconf_architecture:

Architecture
============

This python module is built on-top of the pyivia factory model. A well known API is used to discover the version being deployed, an the module runs the recipe you provide as yaml.

Example configurations can be found in the `examples <https://github.com/ibm-verify/ibm-verify-identity-access-automated-configurator/tree/development/examples>`_ directory with additional documentation in the 
`Examples / Getting Started <examples.html>`_ page.

Strategies on how administrators can attempt idempotency are documented `here <idempotency.html>`_.

The module supports using external secret providers (like Kubernetes or Hashicorp Vault) via `keyword <yamlkeywords.html>`_ replacement.

A number of `environment properties <envvars.html>`_ are also available to set log level and destination.


Modules
_______

The configuration process is broken into five modules. Each module is responsible for configuring a subset of
Verify Identity Access features. You can only set ``appliance`` **or** ``container`` as the top level key.

The order of configuration is:

- Appliance or Container [system/global properties]
- Federations
- Webseal (Reverse Proxy)
- Advanced Access Control

This ordering has been chosen to allow for modules which depend on each-other to be deployed in the correct 
order. eg. Creating federations before defining the reverse proxy object namespace properties.

Configuration is run in the order defined; this allows for delete-then-recreate logic to impose a level of `idempontency* <idempotency.html>`_.

More complex deployment architectures can be achieved by running sequential ``config.yaml`` descriptors.

Detailed information on configuration object structure can be found in the submodule documentation

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   envvars
   yamlkeywords
   examples
   appliance
   container
   webseal
   access_control
   federations



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

When ``IVIA_CONFIGURATOR_LOG_FORMAT=json``:

.. code-block:: json

    {
      "type": "ibmvia-autoconf",
      "host": "ivia-config-5ccc54dcf-nvxf5",
      "timestamp": "2026-04-02T03:18:00.012Z",
      "message": "API Failure Summary - 3 failed request(s)",
      "ibm_threadId": "4150",
      "loglevel": "1",
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



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
