Appliance Configuration
#######################

This module contains documentation for system level configuration applicable for Appliance (VM) based Verify Identity 
Access deployments. Container configuration is defined under the ``container`` top level key. At a minimum an administrator
should define the ``mgmt_base_url``, ``mgmt_user`` and ``mgmt_pwd`` keys (or define the applicable
environment variables). These keys should be defined at the top level of the configuration file.


Example
=======

.. code-block:: yaml

  mgmt_base_url: "https://192.168.42.101:443"
  mgmt_user: "admin"
  mgmt_pwd: "Passw0rd"
  appliance:
    admin_cfg:
      session_timeout: 720
    activation: #Module activation codes
      webseal: !environment IVIA_BASE_CODE
      access_control: !environment IVIA_AAC_CODE
      federation: !environment IVIA_FED_CODE
    network:
      routes:
      - enabled: True
        comment: "Default route"
        address: "default"
        gateway: "192.168.42.1"
        interface: "1.1"
      interfaces:
      - label: "1.1"
        comment: "Default Interface"
        enabled: True
        ipv4:
          dhcp:
            enabled: False
            allow_management: False
            provides_default_route: False
          addresses:
          - address: "192.168.42.101"
            mask_or_prefix: "24"
            broadcast_address: "192.168.42.255"
            allow_management: True
            enabled: True
          - address: "192.168.42.102"
            mask_or_prefix: "24"
            broadcast_address: "192.168.42.255"
            allow_management: False
            enabled: True
        ipv6:
          dhcp:
            enabled: False
            allowManagement: False
      dns:
        auto: False
        primary_server: "9.9.9.9"


.. _appliance:

Appliance specific configuration
================================
This section covers the configuration options which are only available on appliance or Virtual Machine deployments of 
Verify Identity Access.


.. include:: base.rst



FIPS Compliance
===============


.. raw:: html
   :file: schema_html/base/fips.html

|br|

.. _appliance-networking:

Networking
==========

    .. note:: Care must be taken when configuring network interfaces to ensure that 
              the interface used to configure the appliance is not changed (as this 
              will result in the automation tool failing).

    .. note:: Network interfaces can only be updated, they cannot be created.


.. raw:: html
   :file: schema_html/appliance/networking.html

|br|

.. _appliance-date-time:

Date / Time settings
====================


.. raw:: html
   :file: schema_html/appliance/date_time.html

|br|

.. _cluster-configuration:

Cluster Configuration
=====================

    .. note:: PKI required to connect to any servers should be defined in the the `ssl_certificates` property.

.. raw:: html
   :file: schema_html/appliance/cluster.html

|br|

.. _managed-containers:

Managed Containers
==================


.. raw:: html
   :file: schema_html/appliance/managed_containers.html

|br|

.. _global-configuration:

Global Configuration
====================
These configuration properties are common to the Access Control and Federation modules. You must have at least one of 
these modules activated in order to set these configuration properties.


.. include:: global_config.rst
