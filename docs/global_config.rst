.. _global-config:

The global configuration section documents configuration which is shared between the Access Control and Federation modules of Verify Access. This 
includes Advanced Configuration Properties, HTTP template pages, JavaScript mapping rules, Point of Contact profiles, Access Policies and Server Connections.


Access Policies
===============
Access policies can be applied to the deployment types:

* SAML 2.0 identity provider federation

* SAML 2.0 service provider partner to an identity provider federation

* OpenID Connect and API Protection Definition


.. autoclass:: src.verify_access_autoconf.federation.FED_Configurator.Access_Policies
    :members:


Attribute Sources
=================
Identity attribute sources for federated identities.


.. autoclass:: src.verify_access_autoconf.federation.FED_Configurator.Attribute_Sources
    :members:


Advanced Configuration Parameters
=================================
The Advanced Configuration Parameters entry is used to set module wide properties for authentication and authorization 
components. The list of available properties is dependant on the target version of Verify Access being configured. Administrators
are able to use the Verify Access assigned identifier or the name of the property.


.. autoclass:: src.verify_access_autoconf.access_control.AAC_Configurator.Advanced_Configuration
   :members:


HTTP Template Files
===================
This configuration option can be used to set files or directories containing HTML files which are compatible with the 
AAC and Federation templating engine. The directory structure of any directories to upload should follow the default 
top level directories. If you are defining a directory it should contain a trailing ``/``.


.. autoclass:: src.verify_access_autoconf.access_control.AAC_Configurator.Template_Files
   :members:


JavaScript Mapping Rules
========================
This configuration option can be used to upload different types or categories of JavaScript Mapping Rules. These rules 
are typically used to implement custom business logic for a particular integration requirement.


.. note:: Some types of mapping rules are defined elsewhere, eg OIDC pre/post token mapping rules must be defined with 
          the OIDC definition they are associated with.


.. autoclass:: src.verify_access_autoconf.access_control.AAC_Configurator.Mapping_Rules
   :members:


Point Of Contact
================
The point of contact profile is used to control how the runtime server communicates with the point of contact server (usually WebSEAL).


.. autoclass:: src.verify_access_autoconf.federation.FED_Configurator.Point_Of_Contact_Profiles
   :members:


Server Connections
==================
Server connections are used to connect to third party infrastructure such as LDAP registries, email servers, SMS servers, ect. These 
connections are used by other AAC components to provide authentication/authorization services.


.. autoclass:: src.verify_access_autoconf.access_control.AAC_Configurator.Server_Connections
   :members:


Runtime Server Configuration
============================
This property can be used to configure the runtime liberty server. This includes: configuring trace; managing endpoints/interfaces that
the runtime server can respond to requests; setting server configuration parameters (such as proxy settings, SSL configuration); and 
defining users in the runtime user registry.


.. autoclass:: src.verify_access_autoconf.access_control.AAC_Configurator.Runtime_Configuration
   :members: