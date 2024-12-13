Deploying this example
######################

This demonstrations documents the required configuration to use IBM Security Verify Access as a
Mobile Multi-Factor Authentication provider. This scenario configures a WebSEAL reverse proxy
to protect applications for mobile and browser based clients.


Kubernetes environment
----------------------

To deploy the required containers we will be using a kubernetes distribution called microk8s. However any Kubernetes or OpenShift environment will work.

The configuration containers required elevated permissions in order to run.

We will be using the Verify Access Operator to manage the promotion of configurations to the runtime Reverse Proxy and Authorization containers.



Installing the Verify Access Operator
-------------------------------------
The Verify Access Operator can be installed into any Kubernetes environment from source code

```
kubectl create -f https://github.com/IBM-Security/verify-access-operator/releases/download/v24.4.0/bundle.yaml
```



Environment properties
----------------------
This demonstration will also require you to define some properties which are likely to change based on the demo

Update the hostname for the Reverse Proxy for the Verify Access appliance (default is `www.myidp.ibm.com`)


```
cat > mmfa.env <<EOF
MMFAP12_SECRET=Passw0rd
HVDB_HOST=postgresql
HVDB_PORT=5432
HVDB_USER=postgres
HVDB_PW=Passw0rd
HVDB_DB=isva
LDAP_HOST=openldap
LDAP_PORT=636
ISVA_BASE_CODE=$WGA_CODE
ISVA_AAC_CODE=$MGA_CODE
ISVA_FED_CODE=$FED_CODE
LDAP_BIND_DN=cn=root,secAuthority=Default
LDAP_BIND_PW=Passw0rd
LDAP_SEC_PW=Passw0rd
TEST_PASSWORD=Passw0rd
RUNTIME_USER=easuser
RUNTIME_PASSWORD=passw0rd
ISVA_CONFIG_BASE=/verify_access_config
ISVA_MGMT_PASSWORD=admin
ISVA_CONFIGURATOR_LOG_LEVEL=ALL
ISVA_KUBERNETES_RESTART_SLEEP=60
LIVE_DEMO_CONFIG="lmiHostAndPort=https://isva-mmfa-config:9443,lmiAdminId=admin,lmiAdminPwd=admin,acHostAndPort=https://isva-mmfa-runtime:9443,websealHostNameAndPort=https://www.myidp.ibm.com,acUuidCookieName=ac.uuid"
EOF

kubectl delete secret mmfa-env
kubectl create secret generic mmfa-env --from-env-file=mmfa.env
```



Create Config Map
-----------------
Create a Kubernetes ConfigMap object with the idp and sp YAMl configuration files + the additional certificates, mapping rules and PKCS12 files. The names of these files should be the same as the PKI created in the previous section.

```
kubectl delete configmap mmfa-config
kubectl create configmap mmfa-config --from-file=mmfa_config.yaml \
                                    --from-file=mmfa.p12 \
                                    --from-file=postgresql.pem \
                                    --from-file=ldap.pem \
                                    --from-file=mapping_rules.zip
```



Creating PKI
------------
Use OpenSSL to generate the IDP and SP Public/Private RSA key pairs as well as X509 certificates.

```
openssl genrsa -passout pass:passw0rd -aes128 2048 > mmfa.key
openssl rsa -in mmfa.key -passin pass:passw0rd -out mmfa.key
openssl req -new -out mmfa.csr -key mmfa.key \
    -subj "/C=AU/O=IBM/OU=Security/CN=mmfa"
cat > mmfa.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment, cRLSign, keyCertSign
subjectAltName = @alt_names

[alt_names]
DNS.1 = www.myidp.ibm.com
DNS.2 = myidp.ibm.com

EOF
openssl x509 -req -signkey mmfa.key \
    -in mmfa.csr -out mmfa.pem -days 9999 -extfile mmfa.cnf
rm mmfa.cnf mmfa.csr
openssl genrsa -passout pass:passw0rd -aes128 2048 > mmfa.key
openssl rsa -in sp.key -passin pass:passw0rd -out mmfa.key
openssl req -new -out sp.csr -key sp.key \
    -subj "/C=AU/O=IBM/OU=Security/CN=mmfa"
```


Create Verify Access Containers
-------------------------------

Sample Kubernetes deployments have been provided in the `mmfa_demo_services.yaml` and `mmfa_demo_deployment.yaml` files.
Each file creates the required configuration, reverse proxy, runtime and supporting database/ldap containers for the IDP and 
SP deployments. The runtime containers are created (and managed) by the Verify Access Operator. The operator must already be
installed in you cluster for this to deploy successfully.

```
kubectl create -f mmfa_demo_services.yaml
kubectl create -f mmfa_demo_deployment.yaml
```



Configuration Steps
-------------------
Run the MMFA configuration yaml to deploy this scenario.


Kubernetes job to run all configuration
_______________________________________

```
apiVersion: batch/v1
kind: Job
metadata:
  name: mmfa-config
spec:
  template:
    spec:
      containers:
      - name: verify-identity-access-configurator
        image: autoconf:latest
        imagePullPolicy: Never
        volumeMounts:
        - name: mmfaconfigvol
          mountPath: /verify_access_config
        command:
        - "bash"
        - "-c"
        - |
          echo "Starting MMFA Config"
          ISVA_CONFIG_YAML=mmfa_config.yaml ISVA_MGMT_BASE_URL=https://isva-mmfa-config:9443 python3 -m ibmvia_autoconf;
        envFrom:
        - secretRef:
            name: mmfa-env
      restartPolicy: Never
      volumes:
      - name: mmfa-config
        configMap:
          name: mmfa-config
      - name: mmfaconfigvol
        emptyDir: {}
      initContainers:
      - name: config-volume-builder
        image: autoconf:latest
        imagePullPolicy: Never
        volumeMounts:
        - mountPath: /verify_access_config
          name: mmfaconfigvol
        - mountPath: /tmp/mmfa_config
          name: mmfa-config
        command:
        - "bash"
        - "-c"
        - |
          cp /tmp/mmfa_config/*.{p12,pem,yaml} /verify_access_config/
          unzip /tmp/mmfa_config/mapping_rules.zip -d /verify_access_config/
  backoffLimit: 2
```