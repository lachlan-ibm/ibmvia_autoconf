.. _ibmvia_autoconf_env_vars:

Environment properties
======================

In addition to the supplied YAML configuration, some properties can alternatively be set as environment variables.
If these variables are set, they take priority over values set in configuration files.

.. csv-table::
   :header: "Variable", "Default", "Purpose"
   :widths: 34, 16, 45

   ``IVIA_CONFIG_BASE``, ``$HOME``, Root directory for all configuration files
   ``IVIA_CONFIG_YAML``, ``config.yaml``, YAML configuration file to deploy
   ``IVIA_MGMT_BASE_URL``, *(required)*, Management interface URL
   ``IVIA_MGMT_USER``, *(none)*, "Admin user; omit to use ``IVIA_MGMT_PWD`` as a bearer token"
   ``IVIA_MGMT_PWD``, *(required)*, Password or bearer API access token
   ``IVIA_MGMT_OLD_PWD``, *(none)*, Previous password if a password change is required
   ``IVIA_EXT_USER``, *(none)*, External (federated) user after management_authorization is configured
   ``IVIA_EXT_PWD``, *(none)*, External (federated) password
   ``IVIA_PUBLISH_SNAPSHOT_SLEEP``, ``0``, Seconds to wait after publishing a snapshot
   ``IVIA_KUBERNETES_YAML_CONFIG``, *(none)*, "Kubernetes cluster config file for kubectl (K8s only)"
   ``KUBERNETES_CLIENT_SLEEP``, ``0``, "Seconds to wait after requesting a container restart (K8s only)"
   ``IVIA_DOCKER_COMPOSE_CONFIG``, *(none)*, Docker Compose config file (Docker Compose only)
   ``IVIA_CONFIGURATOR_LOG_LEVEL``, ``INFO``, "Log level: ``DEBUG`` ``INFO`` ``WARNING`` ``ERROR`` ``CRITICAL``"
   ``IVIA_CONFIGURATOR_LOG_FORMAT``, *(standard)*, "Log format string, or json for JSON output"
   ``IVIA_CONFIGURATOR_LOG_FILE``, stdout, Fully-qualified path to write logs to
   ``IVIA_TRACK_API_FAILURES``, ``true``, Collect and summarize failed API calls on exit
   ``IVIA_HASHIVAULT_BASE``, *(none)*, Hashicorp Vaule base URL to fetch secrets from
   ``IVIA_HASHIVAULT_TOKEN``, *(none)*, token to fetch secrets from the Hashicorp Vault service


Configuration
~~~~~~~~~~~~~

``IVIA_CONFIG_BASE``
    Root directory of all configuration files for the deployment. Can contain YAML files, HTML templates,
    JavaScript mapping rules, and XML files.

    .. note:: Defaults to the user's ``$HOME`` directory if not set.

``IVIA_CONFIG_YAML``
    YAML configuration file to deploy. Can be an absolute path or relative to ``IVIA_CONFIG_BASE``.
    Defaults to ``config.yaml`` inside ``IVIA_CONFIG_BASE``.


Connection
~~~~~~~~~~

``IVIA_MGMT_BASE_URL``
    URL of the Verify Identity Access Local Management Interface, including scheme, host, and non-standard port.
    Example: ``https://127.0.0.2:9443``

``IVIA_MGMT_USER``
    Admin user to perform configuration as. Omit to treat ``IVIA_MGMT_PWD`` as a bearer API access token.

``IVIA_MGMT_PWD``
    Password or bearer API access token for authentication.

``IVIA_MGMT_OLD_PWD``
    Previous password for ``IVIA_MGMT_USER``, required only when a password change is being applied.


External authentication
~~~~~~~~~~~~~~~~~~~~~~~

``IVIA_EXT_USER``
    External (federated) user to act as after the ``management_authorization`` feature has been configured.

``IVIA_EXT_PWD``
    External (federated) password for ``IVIA_EXT_USER``.


Container orchestration
~~~~~~~~~~~~~~~~~~~~~~~

``IVIA_PUBLISH_SNAPSHOT_SLEEP``
    Seconds to wait after publishing a configuration snapshot, to allow replication or container stabilisation.

``IVIA_KUBERNETES_YAML_CONFIG``
    Kubernetes cluster config file for ``kubectl`` commands. Must have permission to restart deployments and pods
    in the Verify Identity Access namespace. Absolute path or relative to ``IVIA_CONFIG_BASE``.

    .. note:: Applies only to Container deployments using Kubernetes orchestration.

``KUBERNETES_CLIENT_SLEEP``
    Seconds to wait after requesting a runtime container restart, to allow containers to fetch and apply the
    latest snapshot.

    .. note:: Applies only to Container deployments using Kubernetes orchestration.

``IVIA_DOCKER_COMPOSE_CONFIG``
    Docker Compose config file for ``docker-compose`` commands. Absolute path or relative to ``IVIA_CONFIG_BASE``.

    .. note:: Applies only to Container deployments using Docker Compose orchestration.


Logging
~~~~~~~

``IVIA_CONFIGURATOR_LOG_LEVEL``
    Logging level for the autoconf tool. Default: ``INFO``.
    Valid values: ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.

``IVIA_CONFIGURATOR_LOG_FORMAT``
    Format string for log messages. Default: ``%(asctime)s - %(levelname)s - %(message)s``.
    Set to ``json`` for JSON-parseable output.

``IVIA_CONFIGURATOR_LOG_FILE``
    Fully-qualified path to a log file. If not set, logs are written to stdout.

``IVIA_TRACK_API_FAILURES``
    Set to ``true`` (default) to collect failed API calls and print a summary on exit.


Vault
~~~~~
``IVIA_HASHIVAULT_BASE``
    HashiCorp Vault base URL to fetch secrets when running a configuration yaml.
    This is used along with the provided token by the vault sdk to fetch secrets.

``IVIA_HASHIVAULT_TOKEN``
    Token to fetch secrets from the HashiCorp Vault service.
    This is used along with the provided base url by the vault sdk to fetch secrets. 