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
configuration snapshots which can be subsequently fetched by other containers in` the deployment.


.. _managing-container-deployments:

Managing Container Deployments
==============================

Kubernetes / OpenShift
----------------------
If Verify Identity Access is deployed with Kubernetes, then ``kubectl`` cli tool can be used to promote a configuration snapshot. There are
two ways to do this: One, use Kubernetes to restart the deployments; Two, use the automated service from the legacy
"all-in-one" container. It is recommended to use Kubernetes to rollout restarts to deployments where possible.

The ``kubectl rollout restart`` command can be used to restart reverse proxy, runtime and DSC deployments. The configurator
can use deployment names to request a restart of all of the pods associated with a deployment. If this functionality is
used then the user running the Kubernetes commands must have sufficient privilege to restart the containers. An example
of a deployment configuration is::

                                 container:
                                   k8s_deployments:
                                     namespace: "default"
                                     configuration:
                                     - "isamconfig"
                                     webseal:
                                     - "isamwrp_1"
                                     - "isamwrp_2"
                                     runtime:
                                     - "isamruntime"
                                     dsc:
                                     - "isamdsc_1"
                                     - "isamdsc_2"


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
