Idempotency
###########

Idempotency is the concept of being able to rerun a configuration and only made modifications where
the underlying configuration has changed, eg: renewing a X509 certificate; rolling an API key; updating an
IP address for a backend service.

This configuration tool intentionally does not try to achieve idempotency by itself. It will blindly attempt to
apply the supplied configuration as it is written. However it is possible for administrators to achieve some 
level of idempotency themselves. The rest of this document will discuss various features/components of 
Verify Identity Access deployments and how configurations files cane be structured to achieve idempotency.


System / Base Configuration
============================
SSL Databases:
Most of the automation logic for importing and managing certificates is idempotent without the autoconf tool.
The tool will try to upload every certificate you list; if the certificate already exists it is not imported.



Reverse Proxy and Runtime Policy Server
=======================================
Starting from IVIA v11.0.3, it is possible to force reconfigure the policy server. Before this, to re-configure the
policy server administrators first had to unconfigure all of the webseal reverse proxy instances. 

Stanza based configuration files
________________________________

IVIA makes use of stanza files quite extensively:

.. code-block::

    [stanza]
    key = value
    another = value
    another = second_value


Being able to track and define this structure can be quite challenging. A simple approach is to use the ordering 
of a configuration file to enforce a state. If the first operation is to delete a ``stanza`` then the subsequent operation
is to rebuild it with the values you want; then you ensure that the file only ever contains the key/value pairs you define.


Advanced Access Control and Federations
=======================================


Authentication policies and mechanisms
______________________________________

