# Deploying the Federation Cookbook

This demonstrations documents the required configuration to use IBM Verify Identity Access as either and 
Identity Provider (IDP) or a Service Provider in a SAML2.0 federated identity scenario. This demonstration requires
each provider to generate a metadata document for the SAML2.0 endpoints, which is then used in a subsequent 
configuration step.

## Setup and prerequisites

### Kubernetes environment

To deploy the required containers we will be using a kubernetes distribution called microk8s. However any 
Kubernetes or OpenShift environment will work.

The configuration containers required elevated permissions in order to run.

We will be using the Verify Identity Operator to manage the promotion of configurations to the runtime Reverse Proxy 
and Authorization containers.

You will also need to create or modify the DNS configuration for the cluster so that requests to `www.myidp.ibm.com` are
routed to the IDP reverse proxy container, and `www.mysp.ibm.com` are routed to the SP reverse proxy.



### Installing the Verify Access Operator
The Verify Access Operator can be installed into any Kubernetes environment from source code

```
kubectl create -f https://github.com/IBM-Security/verify-access-operator/releases/latest/download/bundle.yaml
```



### Environment properties
This demonstration will also require you to define some properties which are likely to change based on the demo

Update the hostname for the Reverse Proxy for the Identity Provider (default is `www.myidp.ibm.com`) and the Service 
Provider (default `www.mysp.ibm.com`)


```
cat > fed.env <<EOF
IDPKEYSP12_SECRET=Passw0rd
SPKEYSP12_SECRET=Passw0rd
IDP_HVDB_HOST=postgresql-idp
SP_HVDB_HOST=postgresql-sp
HVDB_PORT=5432
HVDB_USER=postgres
HVDB_PW=Passw0rd
HVDB_DB=isva
IDP_LDAP_HOST=openldap-idp
SP_LDAP_HOST=openldap-sp
LDAP_PORT=636
IVIA_BASE_CODE=$WGA_CODE
IVIA_AAC_CODE=$MGA_CODE
IVIA_FED_CODE=$FED_CODE
LDAP_BIND_DN=cn=root,secAuthority=Default
LDAP_BIND_PW=Passw0rd
LDAP_SEC_PW=Passw0rd
FED_ANON_PASSWORD=Passw0rd
TEST_PASSWORD=Passw0rd
RUNTIME_USER=easuser
RUNTIME_PASSWORD=passw0rd
IVIA_CONFIG_BASE=/verify_access_config
IVIA_MGMT_PASSWORD=admin
IVIA_CONFIGURATOR_LOG_LEVEL=ALL
IVIA_KUBERNETES_RESTART_SLEEP=60
IDP_LIVE_DEMO_CONFIG="lmiHostAndPort=https://isam.myidp.ibm.com,lmiAdminId=admin,lmiAdminPwd=Passw0rd,acHostAndPort=https://isva-idp-runtime:9443,websealHostNameAndPort=https://www.myidp.ibm.com,acUuidCookieName=ac.uuid"
SP_LIVE_DEMO_CONFIG="lmiHostAndPort=https://isam.mysp.ibm.com,lmiAdminId=admin,lmiAdminPwd=Passw0rd,acHostAndPort=https://isva-sp-runtime:9443,websealHostNameAndPort=https://www.mysp.ibm.com,acUuidCookieName=ac.uuid"
EOF

kubectl delete secret fed-env
kubectl create secret generic fed-env --from-env-file=fed.env
```



### Create Persistent Volume Claim
Create a Kubernetes PersistentVolumeClaim object with the idp and sp YAMl configuration files + the additional certificates, 
mapping rules and PKCS12 files. The names of these files should be the same as the PKI created in the previous section.

We will copy the files to the container once it has started, unpack the archive files, then start running the configuration
tool.

```
kubectl delete configmap fed-config
kubectl create configmap fed-config --from-file=federation_idp.yaml \
                                    --from-file=federation_idp_partner.yaml \
                                    --from-file=federation_sp.yaml \
                                    --from-file=idpkeys.p12 \
                                    --from-file=spkeys.p12 \
                                    --from-file=postgresql.pem \
                                    --from-file=ldap.pem \
                                    --from-file=sp.pem \
                                    --from-file=mapping_rules.zip
```



### Generate PKI
Use OpenSSL to generate the IDP and SP Public/Private RSA key pairs as well as X509 certificates.

```
openssl genrsa -passout pass:passw0rd -aes128 2048 > idp.key
openssl rsa -in idp.key -passin pass:passw0rd -out idp.key
openssl req -new -out idp.csr -key idp.key \
    -subj "/C=AU/O=IBM/OU=Security/CN=idp"
cat > idp.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment, cRLSign, keyCertSign
subjectAltName = @alt_names

[alt_names]
DNS.1 = www.myidp.ibm.com
DNS.2 = myidp.ibm.com

EOF
openssl x509 -req -signkey idp.key \
    -in idp.csr -out idp.pem -days 9999 -extfile idp.cnf
rm idp.cnf idp.csr
openssl genrsa -passout pass:passw0rd -aes128 2048 > sp.key
openssl rsa -in sp.key -passin pass:passw0rd -out sp.key
openssl req -new -out sp.csr -key sp.key \
    -subj "/C=AU/O=IBM/OU=Security/CN=sp"
cat > sp.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment, cRLSign, keyCertSign
subjectAltName = @alt_names

[alt_names]
DNS.1 = www.mysp.ibm.com
DNS.2 = mysp.ibm.com
EOF
openssl x509 -req -signkey sp.key \
    -in sp.csr -out sp.pem -days 9999 -extfile sp.cnf
rm sp.cnf sp.csr
openssl pkcs12 -export -out idpkeys.p12 -inkey idp.key -in idp.pem -passout pass:Passw0rd
openssl pkcs12 -export -out spkeys.p12 -inkey sp.key -in sp.pem -passout pass:Passw0rd
```


### Deploy Config Map
Create a Kubernetes ConfigMap object with the idp and sp YAMl configuration files + the additional certificates, 
mapping rules and PKCS12 files. The names of these files should be the same as the PKI created in the previous section.

```
kubectl delete configmap fed-config
kubectl create configmap fed-config --from-file=federation_idp.yaml \
                                    --from-file=federation_idp_partner.yaml \
                                    --from-file=federation_sp.yaml \
                                    --from-file=idpkeys.p12 \
                                    --from-file=spkeys.p12 \
                                    --from-file=postgresql.pem \
                                    --from-file=ldap.pem \
                                    --from-file=sp.pem \
                                    --from-file=mapping_rules.zip
```

### Deploy Verify Identity Access containers
Sample Kubernetes deployments have been provided in the `federation_demo_services.yaml` and `federation_demo_deployment.yaml` files.
Each file creates the required configuration, reverse proxy, runtime and supporting database/ldap containers for the IDP and 
SP deployments. The runtime containers are created (and managed) by the Verify Access Operator. The operator must already be
installed in you cluster for this to deploy successfully.

```
kubectl create -f federation_demo_services.yaml
kubectl create -f federation_demo_deployment.yaml
```


## Running the configuration tool

### Required files
This deployment example relies on a number of additional configuration files in order to be deployed
successfully. The required files include:

- JavaScript mapping rule: `mapping_rules.zip`
- PKCS12 Keystores: `idpkeys.p12` and `spkeys.p12`
- X.509 Certificates: `postgresql.pem`, `ldap.pem`, `idp.pem` and `sp.pem`
- Environments secrets: `fed.env`

The mapping rule files can be downloaded from the [federation demo] (https://www.github.com/lachlan-ibm) 
directory. The X.509 certificates (and corresponding keys) and `fed.env` should be generated and deployed to
the appropriate Kubernetes objects with the above commands.

### Configuration Steps
This demo must be run in four stages. 

The first two stages configure the Identity Provider and Service Provider.

The final two stages configures the IDP and SP partner relationships between the two deployments.

This can all be done using a Kubernetes Job, which can run the required configuration sequentially.

#### Configure IDP
Set up the Identity Provider (IdP).

```bash
source fed.env
export IVIA_CONFIG_BASE="$(pwd)" 
export IVIA_CONFIG_YAML=federation_idp.yaml
export IVIA_MGMT_BASE_URL=https://isva-idp-config:9443
python3 -m ibmvia_autoconf | tee idp_config.log
```


#### Configure SP
Set up the Service Provider (SP).

```bash
source fed.env
export IVIA_CONFIG_BASE="$(pwd)"
export IVIA_CONFIG_YAML=federation_sp.yaml
export IVIA_MGMT_BASE_URL=https://isva-sp-config:9443
python3 -m ibmvia_autoconf | tee sp_config.log
```

#### Configure IDP partner
Import the Service Provider's SAML 2.0 Partner metadata document to the IdP.

```bash
source fed.env
export IVIA_CONFIG_BASE="$(pwd)"
export IVIA_CONFIG_YAML=federation_idp_partner.yaml
export IVIA_MGMT_BASE_URL=https://isva-idp-config:9443
python3 -m ibmvia_autoconf | tee idp_partner.log
```



### Kubernetes job to run all configuration with PVC for MicroK8s
The following YAML fragment performs the above configuration steps as a Kubernetes job. It uses the 
Universal Base Image as the base container, it also unpacks some of the configuration files from
archive

```yaml
kind: PersistentVolumeClaim
metadata:
  name: ivia-autoconf-pvc
spec:
  storageClassName: microk8s-hostpath
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
---
apiVersion: batch/v1
kind: Job
metadata:
  name: fed-config
spec:
  template:
    spec:
      containers:
      - name: verify-identity-access-configurator
        image: registry.access.redhat.com/ubi9/ubi-minimal
        imagePullPolicy: Never
        volumeMounts:
        - name: fedconfigvol
          mountPath: /verify_access_config
        command:
        - "bash"
        - "-c"
        - |
          microdnf -y install python3 python3-pip
          pip install ibmvia_autoconf
          echo "Starting IDP Config"
          IVIA_CONFIG_YAML=federation_idp.yaml IVIA_MGMT_BASE_URL=https://isva-idp-config:9443 python3 -m ibmvia_autoconf | tee /verify_access_config/idp_config.log
          echo "Starting SP Config" && sleep 10
          IVIA_CONFIG_YAML=federation_sp.yaml IVIA_MGMT_BASE_URL=https://isva-sp-config:9443 python3 -m ibmvia_autoconf | tee /verify_access_config/sp_config.log
          echo "Starting IDP partner Config" && sleep 10
          IVIA_CONFIG_YAML=federation_idp_partner.yaml IVIA_MGMT_BASE_URL=https://isva-idp-config:9443 python3 -m ibmvia_autoconf | tee /verify_access_config/idp_partner.log
        envFrom:
        - secretRef:
            name: fed-env
      restartPolicy: Never
      volumes:
      - name: fed-config
        configMap:
          name: fed-config
      - name: fedconfigvol
        persistentVolumeClaim:
          claimName: ivia-mmfa-autoconf-pvc
      initContainers:
      - name: config-volume-builder
        image: registry.access.redhat.com/ubi9/ubi-minimal
        imagePullPolicy: Never
        volumeMounts:
        - mountPath: /verify_access_config
          name: fedconfigvol
        - mountPath: /tmp/fed_config
          name: fed-config
        command:
        - "bash"
        - "-c"
        - |
          microdnf -y install unzip
          cp /tmp/fed_config/*.{p12,pem,yaml} /verify_access_config/
          unzip /tmp/fed_config/mapping_rules.zip -d /verify_access_config/
  backoffLimit: 2
```
