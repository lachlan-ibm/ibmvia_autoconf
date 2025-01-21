Example Verify Identity Access Configurations (Getting Started)
######################################################

First Steps (container deployment)
==================================

The first steps configuration file defines some initial configuration that is required for all Verify Identity Access deployments.
These steps include:

- Accepting the software license agreement and initial management configuration.
- Configuring service accounts for publishing snapshots to Runtime Containers.
- Importing PKI for the LDAP Runtime Server and High-Volume Runtime Database.
- Applying module licenses for the WebSEAL, Advanced Access Control and Federation modules.
- Configuring the WebSEAL Runtime Policy Server / User Registry.

To run this configuration you should define the following properties, where the "current directory" contains the PKI for the LDAP and HVDB services:

.. code-block:: bash

   export IVIA_CONFIG_BASE="current directory"
   export IVIA_CONFIG_YAML=first_steps.yaml
   export IVIA_MGMT_BASE_URL="https://192.168.42.101"
   export IVIA_MGMT_USER=admin
   export IVIA_MGMT_PWD=betterThanPassw0rd
   export IVIA_MGMT_OLD_PWD=admin
   export IVIA_BASE_CODE="webseal activation code"
   export IVIA_AAC_CODE="access control activation code"
   export IVIA_FED_CODE="federations activation code"
   export LDAP_BIND_PASSWORD=betterThanPassw0rd
   export LDAP_SEC_PASSWORD=betterThanPassw0rd

The container deployment used for this demo can be found in the `Verify Identity Access <https://github.com/IBM-Security/verify-access-container-deployment>`_ 
sample code.


.. include:: ../examples/first_steps.yaml
   :literal:


First Steps (appliance deployment)
==================================

The first steps configuration file defines some initial configuration that is required for all Verify Identity Access deployments.
These steps include:

- Accepting the software license agreement and initial management configuration.
- Setting network configuration (routes, ip addresses, dns).
- Applying module licenses for the WebSEAL, Advanced Access Control and Federation modules.
- Configuring the WebSEAL Runtime Policy Server / User Registry.

To run this configuration you should define the following properties:

.. code-block:: bash

   export IVIA_CONFIG_YAML=appliance_first_steps.yaml
   export IVIA_MGMT_BASE_URL="https://192.168.42.101"
   export IVIA_MGMT_USER=admin
   export IVIA_MGMT_PWD=betterThanPassw0rd
   export IVIA_MGMT_OLD_PWD=admin
   export IVIA_BASE_CODE="webseal activation code"
   export IVIA_AAC_CODE="access control activation code"
   export IVIA_FED_CODE="federations activation code"
   export LDAP_BIND_PASSWORD=betterThanPassw0rd
   export LDAP_SEC_PASSWORD=betterThanPassw0rd


.. include:: ../examples/appliance_first_steps.yaml
   :literal:


Container golden image pipeline
===============================

This configuration example will demonstrate how administrators can set up a "pipeline" of configuration
steps to build out a deployment. This is especially useful in staged (development/production) environments
where a Verify Identity Access deployment might be tested in several different sandboxed environments before it is 
pushed to a production environment.

This workflow builds on a configuration snapshot (golden image), which can be used to scale out a Verify Identity 
Access deployment. The first steps involve completing steps which are required for all environments, such 
as accepting EULA, activating Verify Identity Access modules, or importing static resources such as JavaScript 
mapping rules/HTML template files. Once this configuration has been completed, the generated snapshot 
file can be reused to bootstrap Verify Identity Access deployments in downstream environments.


Base Snapshot
_____________
This configuration will accept the EULA, activate the modules of Verify Identity Access and enable OIDC authentication
to the management interface.

To run this configuration you should define the following properties:

.. code-block:: bash

   export IVIA_CONFIG_YAML=golden_base_image.yaml
   export IVIA_MGMT_BASE_URL="https://192.168.42.101"
   export IVIA_MGMT_USER=admin
   export IVIA_MGMT_PWD=betterThanPassw0rd
   export IVIA_MGMT_OLD_PWD=admin
   export IVIA_BASE_CODE="webseal activation code"
   export IVIA_AAC_CODE="access control activation code"
   export IVIA_FED_CODE="federations activation code"


.. include:: ../examples/snapshot_pipeline/base_image.yaml
   :literal:


Development Environment
_______________________
This configuration step will set up the WebSEAL Reverse Proxy runtime environment and create a 
reverse proxy instance to test with. This configuration will also re-import the required PKI for
the dev environment's LDAP and HVDB connections.

To run this configuration you should define the following properties:

.. code-block:: bash

   export IVIA_CONFIG_YAML=dev_env_image.yaml
   export IVIA_MGMT_BASE_URL="https://192.168.42.101"
   export IVIA_MGMT_PWD="apiKeyGoesHere"
   export LDAP_PWD="Passw0rd"
   export RUNTIME_USER="easuser"
   export RUNTIME_PWD="passw0rd"


.. include:: ../examples/snapshot_pipeline/dev_env_image.yaml
   :literal:


Production Environment
______________________
This configuration step will deploy the development snapshot image to a production environment, updating
the required PKI for connections to the HVDB and LDAP services.

To run this configuration you should define the following properties:

.. code-block:: bash

   export IVIA_CONFIG_YAML=prod_env_image.yaml
   export IVIA_MGMT_BASE_URL="https://192.168.42.101"
   export IVIA_MGMT_PWD="apiKeyGoesHere"


.. include:: ../examples/snapshot_pipeline/prod_env_image.yaml
   :literal:


WebSEAL Reverse Proxy using Advanced Access Control authentication
==================================================================

The WebSEAL / AAC deployment defines a Verify Identity Access deployment with a single WebSEAL reverse proxy. This proxy is
configured to perform authentication using the AAC authentication capabilities. The configuration steps performed
include:

- Creating a WebSEAL Reverse Proxy instance
- Integrating the AAC/Federation runtime to provide authentication to WebSEAL
- Enable the Username/Password authentication mechanism
- Create a demo user in the WebSEAL User Registry
- Update the default WebSEAL login page to use AAC


.. include:: ../examples/webseal_authsvc_login.yaml
   :literal:


Installation of the Instana monitoring agent
============================================

The Instana monitoring example defines a Verify Identity Access deployment where a third party infrastructure monitoring tool (Instana)
is installed onto a Verify Identity Access appliance using a `Verify Identity Access Extension <https://exchange.xforce.ibmcloud.com/hub>`_. This 
extension allows administrators to collect detailed system information (CPU, RAM, Disk, Networking) during runtime. This example 
assumes that you have a valid Instana tenant and have downloaded the latest `Agent RPM <https://packages.instana.io/agent/download>`_ 
for JDK 11. The configuration steps performed include:

- Applying the module licenses
- Set static networking properties
  - Static IPv4 addresses
  - Gateway (default route) settings
  - Set DNS properties
- Install the Instana extension
- Configure the WebSEAL RTE (Policy Server/User Registry)


.. include:: ../examples/instana_monitor.yaml
   :literal:


Mobile Multi-Factor Authentication Cookbook
===========================================

The MMFA example follows the legacy cookbook deployment guide. This guide will configure Verify Identity Access to 
demonstrate the transaction signing, context-base access and risk-based access capabilities of the product.

To successfully run this demo there are some pre-requisites which your environment must meet.

Before you start
________________

- Deploy the user registry (ISDS/LDAP) and runtime database (HVDB).
   - Temporary services can be deployed using the verify access demo containers, an exampele deployment is 
     available `here <https://gist.github.com/lachlan-ibm>`_.
- [Optional] Deploy the Verify Identity Access Operator to manage runtime containers and configuration snapshots.
- Deploy the configuration, web reverse proxy, and runtime Verify Identity Access containers.
   - An example deployment of configuration, reverse proxy and runtime containers can be 
     found `here <https://gist.github.com/lachlan-ibm>`_
- Generate any additional PKI for reverse proxy instances, ect.
   - This demo assumes you will generate a key/certificate for the reverse proxy that is signed by an external 
     Certificate Authority
- Obtain a copy of the template files and mapping rules used by this demo. The latest version of these files is
  available `here <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/mmfa_demo>`_.
- Create the Kubernetes ConfigMaps and Secrets required for this demo.
- Update your local environment to resolve the domain ``www.myidp.ibm.com`` to the web reverse proxy interface and port

  .. note:: This is often as simple as updating your hosts file to map this domain to your wrp container or ingress route.

More detailed steps to create the required keys, certificates and kubernetes objects can be found in 
the `MMFA demo readme <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/mmfa_demo/README.md>`_.


.. _example_mmfa_yaml:

Mobile Multi-Factor Authentication Configuration:
_________________________________________________

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/mmfa_demo/mmfa_config.yaml
      :literal:


Testing it out
______________

``https://www.myidp.ibm.com/mga/sps/mmfa?TO=DO``


Federation Cookbook
===================

The Federation example follows the legacy cookbook deployment guide. This guide configures the SAML and OIDC Federated
identity capabilities of Verify Identity Access. For this demo, both the IDP and SP roles are performed by Verify Identity Access, either 
can be substituted with a different identity provider or consumer, as long as they are compliant with the relevant 
identity standard.

To successfully run this demo there are some pre-requisites which your environment must meet.


Before you start
________________

- Create the PKI for the IDP and SP deployments.
   - Demo assumes self-signed certificates
   - Require keys and certificates for: IDP wrp, SP wrp, IDP LDAP, SP LDAP, IDP runtime database, 
     SP runtime database
- Obtain a copy of the required JavaScript mapping rules for this demo. The latest version of these files is 
  available `here <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/federation_demo>`_.
- Create the Kubernetes ConfigMaps and Secrets required for this demo.
- Create the configuration, web reverse proxy, and runtime Verify Identity Access containers.
   - This demo requires the IDP and SP to both have wrp and runtime containers deployed.
- Update your local environment to resolve the domain ``www.myidp.ibm.com`` to the IDP web reverse proxy interface 
  and port; and ``www.mysp.ibm.com`` to the SP reverse proxy interface and port.

  .. note:: This is often as simple as updating your hosts file to map this domain to your wrp container or ingress route.

More detailed steps to create the required keys, certificates and kubernetes objects can be found in 
the `Federation demo readme <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/federation_demo/README.md>`_.


.. _example_idp_yaml:

IdP Configuration:
__________________

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/federation_demo/federation_idp.yaml
      :literal:

.. _example_sp_yaml:

SP Configuration:
_________________

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/federation_demo/federation_sp.yaml
      :literal:

.. _example_idp_partner_yaml:

IdP Partner Configuration:
__________________________

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/federation_demo/federation_idp_partner.yaml
      :literal:

Trying it out
_____________

* Create a test user using the demo User Self Care enrollment policy on the IdP deployment

* Test the Federated authentication:

  * IdP initiated SSO

  * SP initiated SSO
