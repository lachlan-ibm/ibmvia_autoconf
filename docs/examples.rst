Example Verify Identity Access Configurations (Getting Started)
###############################################################

First Steps
===========

Container deployment
--------------------
The container deployment used for this demo can be found in the `Verify Identity Access <https://github.com/IBM-Security/verify-access-container-deployment>`_ 
docker-compose sample deployment code.

The first steps configuration file defines some initial configuration that is required for all Verify Identity Access deployments.
These steps include:

- Accepting the software license agreement and initial management configuration.
- Configuring service accounts for publishing snapshots to Runtime Containers.
- Importing PKI for the LDAP Runtime Server and High-Volume Runtime Database.
- Applying module licenses for the WebSEAL, Advanced Access Control and Federation modules.
- Configuring the WebSEAL Runtime Policy Server / User Registry.

.. collapse:: Expand to see code examples of configuration.


    Set the following properties as environment variables for the process running the configuration tool:

    .. code-block:: bash


       export IVIA_CONFIG_BASE="${HOME}/dockershare/ibmvia_autoconf"
       export IVIA_CONFIG_YAML=first_steps.yaml
       export IVIA_MGMT_BASE_URL="https://isam.myidp.ibm.com"
       export IVIA_MGMT_USER=admin
       export IVIA_MGMT_PWD=betterThanPassw0rd
       export IVIA_MGMT_OLD_PWD=admin
       export IVIA_BASE_CODE="webseal activation code"
       export IVIA_AAC_CODE="access control activation code"
       export IVIA_FED_CODE="federations activation code"
       export LDAP_BIND_PASSWORD=betterThanPassw0rd
       export LDAP_SEC_PASSWORD=betterThanPassw0rd

    .. note:: Module acivation codes can be replaced with a trial license. See :ref:`instana demo<Installation of the Instana monitoring agent>` for trial license config example.
    .. note:: This deployment uses ``isam.myidp.ibm.com`` as a domain name for the management interface. You might need to set a host file entry for your Operating System.
    |br|
    ``first_steps.yaml`` should be a file that exist in the working directory of the 
    user running the configuration tool. The content of this file is expectd to be:

     .. include:: ../examples/first_steps.yaml
        :literal:

    Run the configuration tool in a shell using python

    .. code-block:: bash

        python -m ibmvia_autoconf
    
|br|

Appliance deployment
--------------------
The first steps configuration file defines some initial configuration that is required for all Verify Identity Access deployments.
These steps include:

- Accepting the software license agreement and initial management configuration.
- Setting network configuration (routes, ip addresses, dns).
- Applying module licenses for the WebSEAL, Advanced Access Control and Federation modules.
  - if you do not have product activation codes, you can request a trial license from the `trial site <https://isva-trial.verify.ibm.com>`_.
- Configuring the WebSEAL Runtime Policy Server / User Registry.


.. collapse:: Expand to see code examples of configuration.


    Set the following properties as environment variables for the process running the configuration tool:

    .. code-block:: bash

       export IVIA_CONFIG_BASE="${HOME}/ibmvia_autoconf/examples"
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

    .. note:: Module acivation codes can be replaced with a trial license. See :ref:`instana demo<Installation of the Instana monitoring agent>` for trial license config example.
    |br|
    ``appliance_first_steps.yaml`` should be a file that exist in the working directory of the 
    user running the configuration tool. The content of this file is expectd to be:

    .. include:: ../examples/appliance_first_steps.yaml
       :literal:

    Run the configuration tool in a shell using python

    .. code-block:: bash

        python -m ibmvia_autoconf
|br|

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

You can run this configuration script on a deployment which has already been activated / licensed, eg.
by running :ref:`First Steps`.

The deployment can be tested with the ``testuser`` IVIA user account. The user is created in the reverse 
proxy user registry, and can have password control and other account management capabilities applied.

Once you have this scenario working you should try the "Identifier First Authetication" scenario for 
advanced login user experiences, include MMFA, passkey, and password authentication.

.. collapse:: Expand for code example of webseal reverse proxy configuration

    Set the following properties as environment variables for the process running the configuration tool:

    .. code-block:: bash

          export IVIA_CONFIG_BASE="${HOME}/ibmvia_autoconf/examples"
          export IVIA_CONFIG_YAML=webseal_authsvc_login.yaml
          export IVIA_MGMT_BASE_URL="https://192.168.42.101"
          export IVIA_MGMT_USER=admin
          export IVIA_MGMT_PWD=betterThanPassw0rd
          export LDAP_BIND_DN="cn=root,secAuthority=Default"
          export LDAP_BIND_PWD=betterThanPassw0rd
          export LDAP_SEC_PWD=sec_master
          export LDAP_SEC_PWD=betterThanPassw0rd
          export AAC_RUNTIME_USER=easuser
          export AAC_RUNTIME_PW=betterThanPassw0rd
          export TEST_BIND_DN="cn=testuser,dc=ibm,dc=com"
          export TEST_BIND_PW=betterThanPassw0rd

    ``webseal_authsvc_login.yaml``:

    .. include:: ../examples/webseal_authsvc_login.yaml
       :literal:

|br|

Container image pipeline
=========================

This configuration example will demonstrate how administrators can set up a "pipeline" of configuration
steps to build out a deployment. This is especially useful in staged (development/production) environments
where a Verify Identity Access deployment might be tested in several different sandboxed environments 
before it is pushed to a production environment.

This workflow builds on a configuration snapshot (golden image), which can be used to scale out a 
Verify Identity Access deployment. The first steps involve completing steps which are required for all 
environments, such as accepting EULA, activating Verify Identity Access modules, or importing static 
resources such as JavaScript mapping rules/HTML template files. Once this configuration has been completed, 
the generated snapshot file can be reused to bootstrap Verify Identity Access deployments in downstream 
environments.

In the dev configuration step, connections to external services (database, user registry, ect) 
are modified to connect to temporary services, so deployment can be incrementally tested before being 
deployed.

.. note:: To make managing and promoting configuration snapshots simple, you should make use of the 
          ``SNAPSHOT_ID`` environment property when running configuration containers, eg: ``base`` for 
          the base snapshot, ``dev`` for the test environment, and ``published`` for production.


Base Snapshot
-------------
This configuration will accept the EULA, activate the modules of Verify Identity Access and enable OIDC 
authentication to the management interface. Giving federated users access to the management interface can 
be useful for compliance reasons (eg. ability to set mulit-factor authentication), however it can present 
some challenges. 

If contact with the identity provier is lost, there is no mechanism to regain access the the management 
interface (or corresponding snapshot). Container deployments also often make use of the management 
authorization feature to manage access for the ``cfgsvc`` account, which is responsible for pulling 
images from the configuration service. Admins must ensure that federated admin users are in the appropriate 
groups and that group-to-feature management authorization mapping is performed for external users 
(``adminGroup`` and ``adminWrite`` groups in this example).

.. collapse:: Code example for base image snapshot configuration


    Set the following properties as environment variables for the process running the configuration tool:

    .. code-block:: bash

       export IVIA_CONFIG_YAML=base_image.yaml
       export IVIA_MGMT_BASE_URL="https://isam.myidp.ibm.com"
       export IVIA_BASE_CODE="webseal activation code"
       export IVIA_AAC_CODE="access control activation code"
       export IVIA_FED_CODE="federations activation code"
       export OIDC_API_TOKEN=TODO
       export OIDC_CLIENT_ID=clientId
       export OIDC_CLIENT_SECRET=clientSecret
       export OIDC_WELL_KNOWN=https://www.myidp.ibm.com/.well-known/openid-configuration
       export LDAP_PKI_DIR="$HOME/dockershare/openldap"
       export HVDB_PKI_DIR="$HOME/dockershare/postgres"

    .. note:: This deployment makes use of the PKI files created for the docker-compose example deployment. You may need to update the ``ssl_certificates`` files for your environment.
    .. note:: This deployment uses ``isam.myidp.ibm.com`` as a domain name for the management interface. 
            You might need to set a host file entry for your Operating System.
    |br|
    ``base_image.yaml`` should be a file that exist in the working directory of the 
    user running the configuration tool. The content of this file is expectd to be:

    .. include:: ../examples/snapshot_pipeline/base_image.yaml
       :literal:

    Run the configuration tool in a shell using python

    .. code-block:: bash

        python -m ibmvia_autoconf

|br|

Development Environment
-----------------------
This configuration step will set up the WebSEAL Reverse Proxy runtime environment and create a 
reverse proxy instance to test with. This configuration will also re-import the required PKI for
the dev environment's LDAP and HVDB connections.

.. collapse:: Code example for dev image snapshot configuration


    Set the following properties as environment variables for the process running the configuration tool:


    .. code-block:: bash

       export IVIA_CONFIG_YAML=dev_image.yaml
       export IVIA_MGMT_BASE_URL="https://isam.myidp.ibm.com"
       export LDAP_PWD="Passw0rd"
       export RUNTIME_USER="easuser"
       export RUNTIME_PWD="passw0rd"
       python -m ibmvia_autoconf

    ``dev_image.yaml``:

    .. include:: ../examples/snapshot_pipeline/dev_image.yaml
       :literal:

|br|

Production Environment
----------------------
This configuration step will deploy the development snapshot image to a production environment, updating
the required PKI for connections to the HVDB and LDAP services.

.. collapse:: Code example for prod image snapshot configuration


    To run this configuration you should define the following properties:

    .. code-block:: bash

       export IVIA_CONFIG_YAML=prod_image.yaml
       export IVIA_MGMT_BASE_URL="https://isam.myidp.ibm.com"
       export IVIA_MGMT_PWD="apiKeyGoesHere"
       python -m ibmvia_autoconf

    ``prod_image.yaml``:

    .. include:: ../examples/snapshot_pipeline/prod_image.yaml
       :literal:

|br|

Installation of the Instana monitoring agent
============================================

The Instana monitoring example defines a Verify Identity Access deployment where a third party infrastructure monitoring tool (Instana)
is installed onto a Verify Identity Access appliance using a `Verify Identity Access Extension <https://exchange.xforce.ibmcloud.com/hub>`_. This 
extension allows administrators to collect detailed system information (CPU, RAM, Disk, Networking) during runtime. This example 
assumes that you have a valid Instana tenant and have downloaded the latest `Agent RPM <https://packages.instana.io/agent/download>`_ 
for JDK 11. The configuration steps performed include:

- Applying the module licenses
  - a temporary IBM Verify Identity Access License can be obtained from the `trial site <https://isva-trial.verify.ibm.com>`_ (requires a W3ID)
- Set static networking properties
  - Static IPv4 addresses
  - Gateway (default route) settings
  - Set DNS properties
- Install the Instana extension
- Configure the WebSEAL RTE (Policy Server/User Registry)

.. collapse:: Expand to see code example of Instana agent installation on Verify Identity Access


    .. include:: ../examples/instana_monitor.yaml
       :literal:

|br|

Mobile Multi-Factor Authentication Cookbook
===========================================

The MMFA example follows the legacy cookbook deployment guide. This guide will configure Verify Identity Access to 
demonstrate the transaction signing, context-base access and risk-based access capabilities of the product.


Before you start
----------------
To successfully run this demo there are some pre-requisites which your environment must meet.

* Deploy the user registry (ISDS/LDAP) and runtime database (HVDB).

  * Temporary services can be deployed using the verify access demo containers, an exampele deployment is 
    available `here <https://github.com/IBM-Security/verify-access-container-deployment/blob/master/kubernetes/ivia-minikube.yaml>`_.

* [Optional] Deploy the Verify Identity Access Operator to manage runtime containers and configuration snapshots.
* Deploy the configuration, web reverse proxy, and runtime Verify Identity Access containers.

  * An example deployment of configuration, reverse proxy and runtime containers with the Operator on OpenShift can be 
    found `here <https://github.com/IBM-Security/verify-access-container-deployment/blob/master/openshift/alt-deployment-configs/operator/oshift-ivia-operator-template.yaml>`_

* Generate any additional PKI for reverse proxy instances, ect.

  * This demo assumes you will generate a key/certificate for the reverse proxy that is signed by an external Certificate Authority

  * Update the ``ssl_certificates.zip`` archive with any keys, certificates that are required.

* Obtain a copy of the template files and mapping rules used by this demo. The latest version of these files is
  available `here <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/mmfa_demo>`_.
* Create the Kubernetes ConfigMaps and Secrets required for this demo.
* Update your local environment to resolve the domain ``mmfa.myidp.ibm.com`` to the web reverse proxy interface and port
* Download the Glowroot agent and extension files from `IBM AppXchange <https://apps.xforce.ibmcloud.com>`_

  .. note:: This is often as simple as updating your hosts file to map this domain to your wrp container or ingress route.

More detailed steps to create the required keys, certificates and kubernetes objects can be found in 
the `MMFA demo readme <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/mmfa_demo/README.md>`_.

.. _example_mmfa_yaml:

Mobile Multi-Factor Authentication scenario configuration:
----------------------------------------------------------

.. collapse:: Expand to see the code example of mmfa scenario deployment.

    This section contains code examples for running the ``ibmvia_autoconf`` tool in a
    Kubernetes Job.

    Create a Persistent Volume Claim for the configurator, unpack the configuration files for this
    scenario and install the ibmvia-autoconf tool using an init-container.

    The Job then simply applies the configuration defined in the ``mmfa_config.yaml`` file sourced from
    the defined ``mmfaconfigvol`` ConfigMap, created as follows:

    .. code-block:: bash

        kubectl create configmap mmfaconfigvol --from-file=mmfa_config.yaml --from-file=mapping_rules.zip \
                --from-file=reverse_proxy.zip --from-file=ssl_certificates.zip --from-file=template_files.zip

    .. collapse:: Expand for YAML deloyment of ibmvia_autoconf on microk8s

        .. include:: ../examples/mmfa_demo/mmfa_demo_configurator.yaml
            :literal:

    |br|

    This configuration requires a number of secrets to be defined. The above job expects to be able to
    read the secret values from a Kubernetes Secret object called ``ivia-mmfa-autoconf-env``. This object
    can be created as follows:
    ``kubectl create secret ivia-mmfa-autoconf-env --from-env-file=mmfa.env``

    .. collapse:: Expand for mmfa scenario secrets configuration required for mmfa.env:

        .. include:: ../examples/mmfa_demo/mmfa.env.example
            :literal:

    |br|

    The mmfa scenario creates two reverse proxy instances, which seperates tcp traffic between browser 
    and mmfa device runtime flows. Administrators should update integrations with external services (eg.
    push notification providers) with real values.

    .. collapse:: Expand for mmfa scenario configuration:

        .. include:: ../examples/mmfa_demo/mmfa_config.yaml
            :literal:

|br|

Testing it out
--------------

This demo scenario makes use of the ``mmfa.myidp.ibm.com`` domain. This can be set via a hose file entry
in your Operating System.

`Mobile demo sample app https://mmfa.myidp.ibm.com/app/mobile-demo/ <https://mmfa.myidp.ibm.com/app/mobile-demo/>`_

`Scim user self care demo https://mmfa.myidp.ibm.com/scim/demo.html <https://mmfa.myidp.ibm.com/scim/demo.html>`_

`User self care (device registrtaions) https://mmfa.myidp.ibm.com/mga/sps/mmfa/user/mgmt/html/mmfa/usc/manage.html <https://mmfa.myidp.ibm.com/mga/sps/mmfa/user/mgmt/html/mmfa/usc/manage.html>`_

`Device registration management https://mmfa.myidp.ibm.com/mga/sps/mga/user/mgmt/html/device/device_selection.html <https://mmfa.myidp.ibm.com/mga/sps/mga/user/mgmt/html/device/device_selection.html>`_


Federation Cookbook
===================

The Federation example follows the legacy cookbook deployment guide. This guide configures the SAML and OIDC Federated
identity capabilities of Verify Identity Access. For this demo, both the IDP and SP roles are performed by Verify Identity Access, either 
can be substituted with a different identity provider or consumer, as long as they are compliant with the relevant 
identity standard.

To successfully run this demo there are some pre-requisites which your environment must meet.


Before you start
----------------

* Create the PKI for the IDP and SP deployments.

   * Demo assumes self-signed certificates
   * Require keys and certificates for: IDP wrp, SP wrp, IDP LDAP, SP LDAP, IDP runtime database, 
     SP runtime database

* Obtain a copy of the required JavaScript mapping rules for this demo. The latest version of these files is 
  available `here <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/federation_demo>`_.
* Create the Kubernetes ConfigMaps and Secrets required for this demo.
* Create the configuration, web reverse proxy, and runtime Verify Identity Access containers.

   * This demo requires the IDP and SP to both have wrp and runtime containers deployed.

* Update your local environment to resolve the domain ``www.myidp.ibm.com`` to the IDP web reverse proxy interface 
  and port; and ``www.mysp.ibm.com`` to the SP reverse proxy interface and port.

  .. note:: This is often as simple as updating your hosts file to map this domain to your wrp container or ingress route.

More detailed steps to create the required keys, certificates and kubernetes objects can be found in 
the `Federation demo readme <https://github.com/lachlan-ibm/ibmvia_autoconf/tree/stable/examples/federation_demo/README.md>`_.


.. _example_idp_yaml:

IdP Configuration
-----------------

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/federation_demo/federation_idp.yaml
      :literal:

|br|

.. _example_sp_yaml:

SP Configuration
----------------

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/federation_demo/federation_sp.yaml
      :literal:

|br|

.. _example_idp_partner_yaml:

IdP Partner Configuration
--------------------------

.. collapse:: Click to see the YAML configuration.

   .. include:: ../examples/federation_demo/federation_idp_partner.yaml
      :literal:

|br|

Trying it out
-------------

* Create a test user using the demo User Self Care enrollment policy on the IdP deployment

* Test the Federated authentication:

  * IdP initiated SSO

  * SP initiated SSO

.. |br| raw:: html

      <br>

.. _trial-site: https://isva-trial.verify.ibm.com/
