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

.. raw:: html
   :file: schema_html/access_control/api_protection.html

|br|

Attribute Sources
=================

To set Attribute sources, see the entry in the `Appliance <appliance.html#attribute-sources>`_ or 
`Container <container.html#attribute-sources>`_ documentation.


.. _authentication:

Authentication
==============


.. raw:: html
   :file: schema_html/access_control/authentication.html

|br|

.. _access_control:

Context Based Access
====================


.. raw:: html
   :file: schema_html/access_control/access_control.html

|br|

Attributes
==========

.. raw:: html
   :file: schema_html/access_control/attributes.html

|br|

Obligations
===========


.. raw:: html
   :file: schema_html/access_control/obligations.html

|br|

Point Of Contact
================

To configure Point of Contact profiles, see the entry in the `Appliance <appliance.html#point-of-contact>`_ or 
`Container <container.html#point-of-contact>`_ documentation.


Policy Information Points
=========================


.. raw:: html
   :file: schema_html/access_control/policy_information_points.html

|br|

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


.. raw:: html
   :file: schema_html/access_control/push_notification_provider.html

|br|

Mobile Multi-Factor Authentication
==================================


.. raw:: html
   :file: schema_html/access_control/mmfa.html

|br|

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


.. raw:: html
   :file: schema_html/access_control/scim.html

|br|

FIDO2
=====

.. raw:: html
   :file: schema_html/access_control/fido2.html

|br|

Runtime Server Configuration
============================

To set Runtime Server properties, see the entry in the `Appliance <appliance.html#runtime-server-configuration>`_ or 
`Container <container.html#runtime-server-configuration>`_ documentation.
