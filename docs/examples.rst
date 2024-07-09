Example Verify Access Configurations (Getting Started)
######################################################

First Steps (container deployment)
==================================

The first steps configuration file defines some initial configuration that is required for all Verify Access deployments.
These steps include:

- Accepting the software license agreement and initial management configuration.
- Configuring service accounts for publishing snapshots to Runtime Containers.
- Importing PKI for the LDAP Runtime Server and High-Volume Runtime Database.
- Applying module licenses for the WebSEAL, Advanced Access Control and Federation modules.
- Configuring the WebSEAL Runtime Policy Server / User Registry.

To run this configuration you should define the following properties, where the "current directory" contains the PKI for the LDAP and HVDB services:

.. code-block:: bash

   export ISVA_CONFIG_BASE="current directory"
   export ISVA_CONFIG_YAML=first_steps.yaml
   export ISVA_MGMT_BASE_URL="https://192.168.42.101"
   export ISVA_MGMT_USER=admin
   export ISVA_MGMT_PWD=betterThanPassw0rd
   export ISVA_MGMT_OLD_PWD=admin
   export ISVA_BASE_CODE="webseal activation code"
   export ISVA_AAC_CODE="access control activation code"
   export ISVA_FED_CODE="federations activation code"
   export LDAP_BIND_PASSWORD=betterThanPassw0rd
   export LDAP_SEC_PASSWORD=betterThanPassw0rd

The container deployment used for this demo can be found in the `Verify Access<https://github.com/IBM-Security/verify-access-container-deployment>`_ 
sample code.


.. include:: ../examples/first_steps.yaml
   :literal:


First Steps (appliance deployment)
==================================

The first steps configuration file defines some initial configuration that is required for all Verify Access deployments.
These steps include:

- Accepting the software license agreement and initial management configuration.
- Setting network configuration (routes, ip addresses, dns).
- Applying module licenses for the WebSEAL, Advanced Access Control and Federation modules.
- Configuring the WebSEAL Runtime Policy Server / User Registry.

To run this configuration you should define the following properties:

.. code-block:: bash

   export ISVA_CONFIG_YAML=appliance_first_steps.yaml
   export ISVA_MGMT_BASE_URL="https://192.168.42.101"
   export ISVA_MGMT_USER=admin
   export ISVA_MGMT_PWD=betterThanPassw0rd
   export ISVA_MGMT_OLD_PWD=admin
   export ISVA_BASE_CODE="webseal activation code"
   export ISVA_AAC_CODE="access control activation code"
   export ISVA_FED_CODE="federations activation code"
   export LDAP_BIND_PASSWORD=betterThanPassw0rd
   export LDAP_SEC_PASSWORD=betterThanPassw0rd


.. include:: ../examples/appliance_first_steps.yaml
   :literal:


Container golden image pipeline
===============================

This configuration example will demonstrate how administrators can set up a "pipeline" of configuration
steps to build out a deployment. This is especially useful in staged (development/production) environments
where a Verify Access deployment might be tested in several different sandboxed environments before it is 
pushed to a production environment.

This workflow builds on a configuration snapshot (golden image), which can be used to scale out a Verify 
Access deployment. The first steps involve completing steps which are required for all environments, such 
as accepting EULA, activating Verify Access modules, or importing static resources such as JavaScript 
mapping rules/HTML template files. Once this configuration has been completed, the generated snapshot 
file can be reused to bootstrap Verify Access deployments in downstream environments.


Base Snapshot
_____________
This configuration will accept the EULA, activate the modules of Verify Access and enable OIDC authentication
to the management interface.

To run this configuration you should define the following properties:

.. code-block:: bash

   export ISVA_CONFIG_YAML=golden_base_image.yaml
   export ISVA_MGMT_BASE_URL="https://192.168.42.101"
   export ISVA_MGMT_USER=admin
   export ISVA_MGMT_PWD=betterThanPassw0rd
   export ISVA_MGMT_OLD_PWD=admin
   export ISVA_BASE_CODE="webseal activation code"
   export ISVA_AAC_CODE="access control activation code"
   export ISVA_FED_CODE="federations activation code"


.. include:: ../examples/snapshot_pipeline/base_image.yaml
   :literal:


Development Environment
_______________________
This configuration step will set up the WebSEAL Reverse Proxy runtime environment and create a 
reverse proxy instance to test with. This configuration will also re-import the required PKI for
the dev environment's LDAP and HVDB connections.

To run this configuration you should define the following properties:

.. code-block:: bash

   export ISVA_CONFIG_YAML=dev_env_image.yaml
   export ISVA_MGMT_BASE_URL="https://192.168.42.101"
   export ISVA_MGMT_PWD="apiKeyGoesHere"
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

   export ISVA_CONFIG_YAML=prod_env_image.yaml
   export ISVA_MGMT_BASE_URL="https://192.168.42.101"
   export ISVA_MGMT_PWD="apiKeyGoesHere"


.. include:: ../examples/snapshot_pipeline/prod_env_image.yaml
   :literal:


WebSEAL Reverse Proxy using Advanced Access Control authentication
==================================================================

The WebSEAL / AAC deployment defines a Verify Access deployment with a single WebSEAL reverse proxy. This proxy is
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

The Instana monitoring example defines a Verify Access deployment where a third party infrastructure monitoring tool (Instana)
is installed onto a Verify Access appliance using a `Verify Access Extension <https://exchange.xforce.ibmcloud.com/hub>`_. This 
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

The MMFA example follows the legacy cookbook deployment guide.

There are a few steps which are required for running this configuration. You must:

* Create the PKI for the Verify Access appliance

* Deploy the Verify Access runtime containers required for the MMFA cookbook.

* Run the :ref:`MMFA<example_mmfa_yaml>` configuration to set up the multi-factor mobile authentication scenario

* Test the MMFA authentication capabilities out


.. _example_mmfa_yaml:

Mobile Multi-Factor Authentication Configuration:
_________________________________________________

.. include:: ../examples/mmfa_demo/mmfa_config.yaml
   :literal:


Federation Cookbook
===================

The Federation example follows the legacy cookbook deployment guide

There are a few steps which are required for running this configuration. You must:

* Create PKI for IDP and SP deployments [self-signed demonstration provide]

* Deploy the IdP and SP container deployments from the :ref:`IAMExploring<https://www.github.com/iamexploring/container-deployment>`

* Obtain an version appropriate copy of the required JavaScript mapping rules

* Run the :ref:`IdP<example_idp_yaml>` configuration to create the Federations on the IdP

* Run the :ref:`SP<example_sp_yaml>` configuration to create the Federations on the SP

* Run the :ref:`IdP partner<example_idp_partner_yaml>` configuration to create the Federation Partners on the IdP.

* Create a test user using the demo User Self Care enrollment policy on the IdP deployment

* Test the Federated authentication:

  * IdP initiated SSO
  
  * SP initiated SSO


.. _example_idp_yaml:

IdP Configuration:
__________________

.. include:: ../examples/federation_demo/federation_idp.yaml
   :literal:

.. _example_sp_yaml:

SP Configuration:
_________________

.. include:: ../examples/federation_demo/federation_sp.yaml
   :literal:

.. _example_idp_partner_yaml:

IdP Partner Configuration:
__________________________

.. include:: ../examples/federation_demo/federation_idp_partner.yaml
   :literal: