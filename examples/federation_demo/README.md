Deploying this example
#####################

This demonstrations documents the required configuration to use IBM Security Verify Access as either and 
Identity Provider (IDP) or a Service Provider in a SAML2.0 federated identity scenario. This demonstration requires
each provider to generate a metadata document for the SAML2.0 endpoints, which is then used in a subsequent 
configuration step.


Kubernetes environment
--------------------

To deploy the required containers we will be using a kubernetes distribution called microk8s. However any Kubernetes or OpenShift environment will work.

The configuration containers required elevated permissions in order to run.

We will be using the Verify Access Operator to manage the promotion of configurations to the runtime Reverse Proxy and Authorization containers.


Installing the Verify Access Operator
_____________________________________



Environment properties
----------------------
This demonstration will also require you to define some properties which are likely to change based on the demo

Update the hostname for the Reverse Proxy for the Identity Provider (default is `www.myidp.ibm.com`) and the Service Provider (default `www.mysp.ibm.com`)



Configuration Steps
-------------------
This demo must be run in four stages. 


The first two stages configure the Identity Provider and Service Provider.


The final two stages configures the IDP and SP partner relationships between the two deployments.

Create the Config Map required for the configurator, this will contain the mapping rules, PKCS12, PEM and YAML files for the deployment

kubectl create configmap fed-config --from-file=mapping_rules.zip --from-file=idp.pem --from-file=sp.pem --from-file=ldap.pem --from-file=postgresql.pem --from-file=federation_idp.yaml --from-file=federation_sp.yaml --from-file=federation_idp_partner.yaml --from-file=federation_sp_partner.yaml --from-file=idpkeys.p12 --from-file=spkeys.p12
kubectl create secret generic fed-env --from-env-file=fed.env

Configure IDP
_____________


Configure SP
____________


Configure IDP partner
_____________________


Configure SP Partner
____________________