Container Configuration
########################

This module contains documentation for system level configuration applicable for Container based Verify Identity Access
deployments. Container configuration is defined under the ``container`` top level key. At a minimum an administrator
should define the ``mgmt_base_url``, ``mgmt_user`` and ``mgmt_pwd`` keys (or define the applicable
environment variables). These keys should be defined at the top level of the configuration file.



Example
=======


.. code-block:: yaml

   mgmt_base_url: "https://127.0.0.1:9443"
   mgmt_user: "admin"
   mgmt_pwd: "Passw0rd"
   container:
     admin_cfg:
       session_timeout: 720
     account_management:
       users:
       - name: "cfgsvc"
         operation: "update"
         password: !secret default/isva-secrets:cfgsvc-passwd
     management_authorization:
       authorization_enforcement: True
       roles:
       - operation: update
         name: "Configuration Service"
         users:
         - name: "cfgsvc"
           type: "local"
         features:
         - name: "shared_volume"
           access: "w"
     ssl_certificates:
     - name: "lmi_trust_store"
       signer_certificates:
       - "postgres.crt"
       - "ldap.crt"
     - name: "rt_profile_keys"
       signer_certificates:
       - "postgres.crt"
       personal_certificates:
       - p12_file: "rt.mmfa.p12"
         secret: !secret default/isva-secrets:rt-p12-passwd
     cluster:
       host: "postgresql"
       port: 5432
       type: "Postgresql"
       user: "postgres"
       password: !secret default/isva-secrets:postgres-passwd
       ssl: True
       db_name: "isva"


.. _container:

Container specific configuration
================================
This section covers the Container specific configuration of Verify Identity Access deployments. Typically this involves setting
an external HVDB connection; and enabling the management authorization feature to permit a service account to publish
configuration snapshots which can be subsequently fetched by other containers in the deployment.


.. _managing-container-deployments:

Managing Container Deployments
==============================
As configuration is applied to a Verify Identity Access deployment, a snapshot is generated and published to a well known
endpoint, where it can be fetched and unpacked by the runtime containers. The runtime containers are only able to unpack aac
snapshot during first-boot; therefore they must be restarted in order to pick up a new configuration.

The autoconf module has some capacity to manage the restarting of runtime containers so that configuration can be incremental. To
be able to do this, the process running the autoconf module must have sufficient permission to restart the containers. This can be 
done by checking the permissions of the docker socket; or attaching a RBAC policy to the service account delegated to the pod 
running in OpenShift/Kubernetes.


Snapshot Publishing
--------------------
The configuration snapshot is the asset used by Verify Identity Access runtime containers to deploy business logic. The process of publishing
a new snapshot; pushing it to the runtime containers; and then restarting the contains can be a slow process. The autoconf module allows admins 
to skip these publish steps for incremental snapshots (as successive pending changes are committed). This allows the autoconf tool to run faster
at the cost of not having a snapshot available to runtime containers as the tool progresses.

The default option is to not publish incremental snapshots: ``incremental_snapshot: False``. 
To publish incremental snapshots admins can include the following YAML:

.. code-block:: yaml

  container:
    incremental_snapshot: True
    docker_compose_yaml: "docker-compose.yaml"
    compose_services:
    - iviawrprp1
    - iviaruntime
    - iviadsc
    - iviadsc-replica


This will push the updated snapshot to each of the listed containers as successive pending changes are committed.

Kubernetes / OpenShift
----------------------
If Verify Identity Access is deployed with Kubernetes, then the autoconf module can be used to promote a configuration 
snapshot. The ``kubernetes`` module is used to request restarts of the reverse proxy, runtime and DSC deployments. If this 
functionality is used then the user running the Kubernetes commands must have sufficient privilege to restart the containers. 
An example of a deployment configuration is:

.. code-block:: yaml

  container:
    incremental_snapshot: True
    k8s_namespace: "default"
    k8s_deployments:
    - "isamwrp_1"
    - "isamwrp_2"
    - "isamruntime"
    - "isamdsc_1"
    - "isamdsc_2"

This feature uses the ``IVIA_PUBLISH_SNAPSHOT_SLEEP`` environment variable to allow time for the configuration to be unpacked 
and the runtime services to start/stabilize. The default idle interval is 15 seconds.

Docker-Compose
--------------
If Verify Identity Access is deployed with Docker-Compose, then ``docker-compose`` cli tool can be used to manage runtime
containers when a snapshot needs to be promoted. The configurator can use the compose service names to request a restart 
of runtime containers. If this functionality is used then the user running the configurator should have sufficient 
privilege to restart docker containers. 
An example of a compose deployment configuration is::

                                                     container:
                                                       compose_services:
                                                         - "isvawrprp1"
                                                         - "isvaruntime"
                                                       docker_compose_yaml: "iamlab/docker-compose.yaml"



Docker or Podman
----------------
If IBM Verify Identity Access is deployed directly to a container runtime, then the docker/podman socket can be used
to request a restart of runtime containers. If this functionality is used then the user running the configurator should 
have sufficient privilege to restart docker containers.

.. code-block:: yaml

  containers:
  - iviawrp-pod1
  - iviaruntime-pod
  - iviadsc-pod

.. _runtime-database-configuration:

Database and Distribued Session Cache Configuration
===================================================


.. raw:: html
   :file: schema_html/container/cluster.html

|br|


.. include:: base.rst


Global Configuration
====================
These configuration properties are common to the Access Control and Federation modules. You must have at least one of 
these modules activated in order to set these configuration properties.


.. include:: global_config.rst
