.. _base-module:

The base configurator is responsible for completing the first steps (SLA), activating licensed modules, importing 
PKI and system wide settings like date/time/networking.


.. _sla-first-steps:

SLA / First steps
=================
The configurator can be used to accept the Service License Agreement as well as the "first steps" LMI prompts, including 
enabling FIPS compliance. This is always done with the admin account using the default password.
Failing this step does not result in autoconfig aborting.


.. note::
   The accept_eula and complete_setup functions are used internally during first-time setup.


.. _lmi-password-update:

Password Update
===============


.. raw:: html
   :file: schema_html/base/admin_password.html

|br|

.. _system-settings:

Administrator Configuration
===========================


.. raw:: html
   :file: schema_html/base/admin_config.html

|br|

.. _ssl-database:

SSL Certificate Database
========================


.. raw:: html
   :file: schema_html/base/ssl_certificates.html

|br|

Administrator Account Management
================================


.. raw:: html
   :file: schema_html/base/account_management.html

|br|

Management Authorization
========================


.. raw:: html
   :file: schema_html/base/management_authorization.html

|br|

Management Authentication
=========================


.. raw:: html
   :file: schema_html/base/management_authentication.html

|br|

.. _module-activation:

Module Activation
=================


.. raw:: html
   :file: schema_html/base/module_activations.html

|br|

.. _advanced-tuning-parameters:

Advanced Tuning Parameters
==========================


.. raw:: html
   :file: schema_html/base/advanced_tuning_parameter.html

|br|

Configuration Snapshots
=======================


.. raw:: html
   :file: schema_html/base/snapshot.html

|br|

Extensions
==========


.. raw:: html
   :file: schema_html/base/extensions.html

|br|

Remote Syslog
=============


.. raw:: html
   :file: schema_html/base/remote_syslog.html

|br|