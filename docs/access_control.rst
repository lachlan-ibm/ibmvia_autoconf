Advanced Access Control Configuration
#####################################
This configuration module is used to apply configuration to the runtime Liberty server. This includes configuring the 
runtime authorization server, context-based access, SCIM, FIDO2, Authentication, Context-Based Access and MMFA.


Example
=======

.. code-block:: yaml

                  access_control:
                     authentication:
                        policies:
                        - name: "Username Password"
                           description: "Username and password authentication policy."
                           enabled: true
                           uri: "urn:ibm:security:authentication:asf:password"
                           policy: "<Policy xmlns=\"urn:ibm:security:authentication:policy:1.0:schema\" PolicyId=\"urn:ibm:security:authentication:asf:password\"><Description>Username and password authentication policy.</Description><Step type=\"Authenticator\"><Authenticator AuthenticatorId=\"urn:ibm:security:authentication:asf:mechanism:password\"/></Step><Actions><Action On=\"null\" type=\"null\"><AttributeAssignments/></Action></Actions></Policy>"
                        mechanisms:
                        - name: "Username Password"
                          type: "Username Password"
                          description: "Username password authentication"
                          uri: "urn:ibm:security:authentication:asf:mechanism:password"
                          properties:
                          - usernamePasswordAuthentication.enableLastLogin: "false"
                          - usernamePasswordAuthentication.loginFailuresPersistent: "false"
                          - usernamePasswordAuthentication.maxServerConnections: "16"
                          - usernamePasswordAuthentication.mgmtDomain: "Default"
                          - usernamePasswordAuthentication.sslServerStartTLS: "false"
                          - usernamePasswordAuthentication.useFederatedDirectoriesConfig: "false"
                          - usernamePasswordAuthentication.userSearchFilter: "(|(objectclass=ePerson)(objectclass=Person))"
                          - usernamePasswordAuthentication.ldapBindDN: "cn=root,secAuthority=Default"
                          - usernamePasswordAuthentication.ldapHostName: "openldap"
                          - usernamePasswordAuthentication.ldapBindPwd: "Passw0rd"
                          - usernamePasswordAuthentication.ldapPort: "636"
                          - usernamePasswordAuthentication.sslEnabled: "true"
                          - usernamePasswordAuthentication.sslTrustStore: "lmi_trust_store"
                          attributes:
                          - selector: "mobile"
                            name: "mobileNumber"
                            namespace: "urn:ibm:security:authentication:asf:mechanism:password"
                          - selector: "mail"
                            name: "emailAddress"
                            namespace: "urn:ibm:security:authentication:asf:mechanism:password"


.. _api_protection:

API Protection
==============
OIDC API protection configuration for definitions and clients. This is capable of creating OpenBanking and FAPI compliant
defintions and clients.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.API_Protection
   :members:


Attribute Sources
=================

To set Attribute sources, see the entry in the `Appliance <appliance.html#attribute-sources>`_ or 
`Container <container.html#attribute-sources>`_ documentation.


.. _authentication:

Authentication
==============
This section describes how to create authentication policies and mechanisms. Authentication policies can be used in 
risk-based access or context-based access policies to conditionally enforce additional authentication/authorization 
requirements.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Authentication
   :members:


.. _access_control:

Context Based Access Control
============================
This section covers the configuration of the Context Based Access policy engine of a Verify Identity Access deployment. 
Context based access policies are capable of defining conditional authentication requirements based on administrator
defined requirements (such as device registration status, ip reputation, authentication method enrollment for a user).


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Access_Control
   :members:


Risk Profiles
=============
Risk profiles provide administrators with a mechanism to calculate the "risk" of an authentication request
based on administrator-defined attributes. For example: creating a risk profile which examines the IPv4 
address of an incoming request to identify the location (continent, country, region, etc.) that the request
is coming from, and conditionally enforcing addition authentication requirements for more "risky" requests.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Risk_Profiles
   :members:


Attributes
==========
Attributes allow an administrator to source information about a user from a number of different sources
to build up credential attributes, which can then be used by subsequent authentication/authorization flows.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Attributes
   :members:


Obligations
===========
Obligations are used to enforce business requirements (such as registering a device) during an authorization
flow before permitting access.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Obligations
   :members:


Point Of Contact
================

To configure Point of Contact profiles, see the entry in the `Appliance <appliance.html#point-of-contact>`_ or 
`Container <container.html#point-of-contact>`_ documentation.


Policy Information Points
=========================
Policy Information Points allow administrators to integrate third party information sources to provide additional
context to an authorization policy before making a decision to permit/deny access.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Policy_Information_Points
   :members:


.. _access_control_template_file:

HTTP Template Files
===================

To upload HTTP template files, see the entry in the `Appliance <appliance.html#http-template-files>`_ or 
`Container <container.html#http-template-files>`_ documentation.


.. _access_control_mapping_rule:

JavaScript Mapping Rules
========================

To upload JavaScript mapping rules, see the entry in the `Appliance <appliance.html#javascript-mapping-rules>`_ or 
`Container <container.html#javascript-mapping-rules>`_ documentation.


.. _access_control_push_notification:

Push Notification Service
=========================
This configuration option can be used to integrate with Apple/Google mobile push notification service.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Push_Notification_Provider
   :members:


Mobile Multi-Factor Authentication
==================================
Configure MMFA capabilities. These properties are used as a discovery mechanism for devices which have been
registered for a user; and is capable of initiating or completing an "out of band" authentication/authorization challenge.


.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Mobile_Multi_Factor_Authentication
   :members:


.. _access_control_server_connections:

Server Connections
==================

To configure third party Server Connections, see the entry in the `Appliance <appliance.html#server-connections>`_ or 
`Container <container.html#server-connections>`_ documentation.


Advanced Configuration Parameters
=================================

To set Advanced Configuration Properties, see the entry in the `Appliance <appliance.html#advanced-configuration-properties>`_ or 
`Container <container.html#advanced-configuration-properties>`_ documentation.


SCIM
====
This configuration property is used to configure Verify Identity Access to integrate with either a LDAP server or a Verify Identity Access User 
Registry (WebSEAL runtime component) using the System for Cross-Domain Identity Management interfaces. This allows 
administrators to create/manage users, as well as provide attributes to other Verify Identity Access authentication components.

.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.System_CrossDomain_Identity_Management
   :members:


FIDO2
=====
The FIDO2 configuration property is used to create and manage FIDO2 relying parties and their associated verification
documents (metadata) as well as any custom logic applied in a JavaScript mediator.

.. autoclass:: src.ibmvia_autoconf.access_control.AAC_Configurator.Fast_Identity_Online2
   :members:


Runtime Server Configuration
============================

To set Runtime Server properties, see the entry in the `Appliance <appliance.html#runtime-server-configuration>`_ or 
`Container <container.html#runtime-server-configuration>`_ documentation.
