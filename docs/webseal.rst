WebSEAL Reverse Proxy Configuration
###################################
This section covers the WebSEAL configuration of a Verify Identity Access deployment. This includes configuring the reverse proxy
policy server and user registry.

Administrators can also use this section to cover WebSEAL specific functionality such as HTTP transformation rules, 
client certificate mapping, federated user registries.


Example
=======

.. code-block:: yaml

                webseal:
                  runtime:
                    policy_server: "ldap"
                    user_registry: "ldap"
                    ldap:
                      host: "openldap"
                      port: 636
                      dn: !secret default/isva_secrets:ldap_bind_dn
                      dn_password: !secret default/isva_secrets:ldap_bind_pw
                      key_file: "lmi_trust_store"
                    clean_ldap: True
                    domain: "Default"
                    admin_user: !secret default/isva_secrets:sec_user
                    admin_password: !secret default/isva_secrets:sec_pw
                    admin_cert_lifetime: 1460
                    ssl_compliance: "fips"
                  reverse_proxy:
                  - name: "default"
                    host: "isvaruntime"
                    http:
                      enabled: "no"
                    https:
                      enabled: "yes"
                      port: "9443"
                    domain: "Default"
                    ldap:
                      ssl: "yes"
                      port: 636
                      key_file: "lmi_trust_store"
                    aac_configuration:
                      hostname: "isvaruntime"
                      port: 9443
                      junction: "/mga"
                      user: !secret default/isva_secrets:runtime_user
                      password: !secret default/isva_secrets:runtime_pw
                      reuse_certs: True
                      reuse_acls: True
                    stanza_configuration:
                    - stanza: "acnt-mgt"
                      entry_id: "enable-local-response-redirect"
                      value: "yes"
                      operation: "update"
                    - stanza: "local-response-redirect"
                      entry_id: "local-response-redirect-uri"
                      value: "/mga/sps/authsvc?PolicyId=urn:ibm:security:authentication:asf:password"
                      operation: "update"
                  pdadmin:
                    users:
                    - name: "testuser"
                      dn: !secret default/isva_secrets:test_dn
                      password: !secret default/isva_secrets:test_pw


.. _webseal_reverse_proxy:

WebSEAL Reverse Proxy Instances
===============================


.. raw:: html
   :file: schema_html/webseal/reverse_proxy.html

|br|

.. _pdadmin:

Policy Directory Admin
======================


.. raw:: html
   :file: schema_html/webseal/pdadmin.html

|br|

.. _webseal_client_cert_map:

Client Certificate Mapping
==========================


.. raw:: html
   :file: schema_html/webseal/client_cert_mapping.html

|br|

.. _webseal_jct_mapping:

Junction Mapping
================


.. raw:: html
   :file: schema_html/webseal/junction_mapping.html

|br|

.. _webseal_url_mapping:

URL Mapping
===========


.. raw:: html
   :file: schema_html/webseal/url_mapping.html

|br|

.. _webseal_user_mapping:

User Mapping
============


.. raw:: html
   :file: schema_html/webseal/user_mapping.html

|br|

.. _webseal_fsso:

Forms Based Single Sign-On
==========================


.. raw:: html
   :file: schema_html/webseal/fsso.html

|br|

.. _webseal_http_transformations:

HTTP Transformation Rules
=========================


.. raw:: html
   :file: schema_html/webseal/http_transformations.html

|br|

.. _webseal_kerberos:

Kerberos
========


.. raw:: html
   :file: schema_html/webseal/kerberos.html

|br|

.. _webseal_pwd_strength:

Password Strength Rules
=======================


.. raw:: html
   :file: schema_html/webseal/password_strength.html

|br|

.. _webseal_rsa_config:

RSA SecurID Authentication
==========================


.. raw:: html
   :file: schema_html/webseal/rsa.html

|br|

.. _webseal_runtime_server:

Runtime Component
=================


.. raw:: html
   :file: schema_html/webseal/runtime.html

|br|

API Access Control
==================


.. raw:: html
   :file: schema_html/webseal/api_access_control.html

