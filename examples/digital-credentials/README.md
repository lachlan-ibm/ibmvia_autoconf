# Deploying the Digital Credentials Cookbook
This example demonstrates how IBM Verify Identity Access can be used to issue and verify digital credentials to employees/users.

This deployment will use the IBM Verify Identiy Access appliance platform to host the Digital Credentials and OIDC OP containers.

## Pre-requisites

- IBM Verify Digital Credentials License
- IBM Verify Identity Access License
- Deploy IVIA (appliance) and activate the WebSEAL, Digital Credentials and Federation modules

# Generate PKI
The services used for this deployment all need certificates and keys to secure communications. They also need to be able to establish trust with eachother. To achieve this we will use a mock Certificat Authority (CA) which will issue certificates for the reverse proxy, OIDC OP service, and the Digital Credential service. This section describes how to generate the required PKI artifacts; and add the required X509 extensions to each of the certificates issued to each service.

## CA
The mock Certificate Authority will be used to issue certificates for the reverse proxy, OIDC OP service, and the Digital Credential service. This section describes how to generate the required PKI artifacts; and add the Basic Constraints and Key Usage X509 extensions.

Note:: The private key is encrypted with a simple password, this should be changed in your environment

```bash
# Generate self signed certificate + key with Key Usage extension
openssl req -x509 -subj "/C=AU/O=IBM/OU=Security/CN=ivia.ca" -newkey rsa:2048 -keyout $PKI_DIR/ivia-ca.key -out $PKI_DIR/ivia-ca.pem -passout pass:Passw0rd -days 365 -addext extendedKeyUsage=serverAuth,clientAuth -addext keyUsage=keyCertSign,cRLSign -addext "basicConstraints=critical,CA:TRUE"
# Wrap key and X509 in PKCS12 container

openssl pkcs12 -export -out $PKI_DIR/ivia-ca.p12 -inkey $PKI_DIR/ivia-ca.key -in $PKI_DIR/ivia-ca.pem -passout pass:Passw0rd -passin pass:Passw0rd
```

## WebSEAL Reverse Proxy
The reverse proxy will be configured to use the mock CA certificate, and requires the Subject Alt Name and Key Usage X509 extensions.

Note:: The private key is encrypted with a simple password, this should be changed in your environment

```bash
cat > $PKI_DIR/dc.v3.ext <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = iviadc

[v3_req]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
basicConstraints = CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = iviadc
EOF
openssl req -new -nodes -keyout $PKI_DIR/ivia-dc.key -out $PKI_DIR/ivia-dc.csr -config $PKI_DIR/dc.v3.ext
openssl x509 -req -in $PKI_DIR/ivia-dc.csr -CA $PKI_DIR/ivia-ca.pem -CAkey $PKI_DIR/ivia-ca.key -CAcreateserial -out $PKI_DIR/ivia-dc.pem -days 365 -extensions v3_req -extfile $PKI_DIR/dc.v3.ext -passin pass:Passw0rd
rm -rf $PKI_DIR/dc.v3.ext
openssl ecparam -name prime256v1 -genkey -noout -out $PKI_DIR/oid4vci_nonce_private_key.pem

```

## Digital Credential Service
The Digital Credentials service will be configured to use the mock CA certificate, and requires the Subject Alt Name X509 extension. The Digital Credential service also requires a private key for signing the nonce.

Note:: The private key is encrypted with a simple password, this should be changed in your environment

```bash
cat > $PKI_DIR/dc.v3.ext <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = iviadc

[v3_req]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
basicConstraints = CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = iviadc
EOF
openssl req -new -nodes -keyout $PKI_DIR/ivia-dc.key -out $PKI_DIR/ivia-dc.csr -config $PKI_DIR/dc.v3.ext
openssl x509 -req -in $PKI_DIR/ivia-dc.csr -CA $PKI_DIR/ivia-ca.pem -CAkey $PKI_DIR/ivia-ca.key -CAcreateserial -out $PKI_DIR/ivia-dc.pem -days 9999 -extensions v3_req -extfile $PKI_DIR/dc.v3.ext -passin pass:Passw0rd
rm -rf $PKI_DIR/dc.v3.ext
openssl ecparam -name prime256v1 -genkey -noout -out $PKI_DIR/oid4vci_nonce_private_key.pem
```

## OIDC OP Service
The OIDC OP service will be configured to use the mock CA certificate, and requires the Subject Alt Name X509 extension.

Note:: The private key is encrypted with a simple password, this should be changed in your environment

```bash
cat > $PKI_DIR/op.v3.ext <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = iviadcop

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = iviadcop
EOF
openssl req -new -nodes -keyout $PKI_DIR/ivia-op.key -out $PKI_DIR/ivia-op.csr -config $PKI_DIR/op.v3.ext
openssl x509 -req -in $PKI_DIR/ivia-op.csr -CA $PKI_DIR/ivia-ca.pem -CAkey $PKI_DIR/ivia-ca.key -CAcreateserial -out $PKI_DIR/ivia-op.pem -days 9999 -extensions v3_req -extfile $PKI_DIR/op.v3.ext -passin pass:Passw0rd
```

# Create Configuration Archives for OP and DC containers
To run the OIDC OP and Digital Credentials containers on an IVIA appliance, the configuration files + additional JavaScript, PKI, ect. needs to be uploaded to a volume. This volume is then mounted to the container's file system when the container starts.

For the OIDC OP contaienr you will need:
- X509 certificate for LDAP service
- x509 certificate for postgresql service
- X590 CA certificate 
- provider.yml:: Configuration file for OP container
- pretoken.js:: Pre-token mapping rule
- preauth_notifytxcode.js:: 
- preauth_userauth.js:: 
- ropc.js:: Mapping rule for ROPC flow

> [!IMPORTANT] The PKI should be added to a directory called `keystore` in the configuration archive.

For the Digital Credential container you will need:
- x509 certificate for postgresql service
- X590 CA certificate 
- config.yaml:: Configuration file for Digital Credentials container
- license.txt:: License file for Digital Credentials container

> [!NOTE] There are a number of hard-coded host names and secrets in these configuration files. These properties
           will need to be updated to match your environment. The configuration files are provided as examples only.

## Zip Configuration Archives
To create the archive (zip) files, change to the directory containing the configuration files and add the required files to the archive:

```bash
cd op_config
zip -r op-config.zip keystore ldap.pem provider.yml pretoken.js preauth_notifytxcode.js preauth_userauth.js ropc.js
cd ../dc_config
zip -r dc-config.zip ivia-ca.pem ivia-dc.pem ivia-dc.key oid4vci_nonce_private_key.pem config.yaml license.txt
```

# Configure the IBM Verify Identity Access Appliance
Update the environment variables with values required for your deployment. Make sure you have copies of the required LUA http transformation rules, extension files for the OP and DC containers; and the PKI files for the mock CA and the Reverse Proxy PKCS12 (certificate and key for TLS connections to WebSEAL).

The IVIA extensions for the DC and OP contaienrs can be downloaded from the [IBM App Xchange](https://apps.xforce.ibmcloud.com/).

You will also need to get a copy of the X509 certificate used to verify connections to `icr.io` or the contaienr registry taht you will be using to fetch the OP and DC containers from.

> [!NOTE] This certificate changes relatively frequently.

This demo assumes you will be able to use the domain name `www.myidp.ibm.com` for the reverse proxy interface of the IVIA appliance. If you are using different domain names, you will need to update the configuration files accordingly. Typically this is dome by using the `hosts` file in your operating system. For example, on Linux or MacOS, you can add the following lines to the `/etc/hosts` file; or for Windows modify the `C:\Windows\System32\drivers\etc\hosts` file:
```
192.168.42.101 lmi.myidp.ibm.com
192.168.42.102 www.myidp.ibm.com
```
The IP addresses are the IP addresses of the IVIA appliance and the reverse proxy respectively. You will need to update these IP addresses to match the IP addresses of your IVIA appliance and reverse proxy.

This example makes use of the internal LDAP registry and Database services of the IVIA appliance. If you are using an external LDAP registry or Database service, you will need to update configuration files in both IVIA and the hosted containers accordingly.

Run the automated configuration tool to configure the IBM Verify Identity Access Appliance:

```bash
# source dc.env # Update hard coded secrets with values required for your deployment
export IVIA_CONFIG_BASE="$(pwd)"
export IVIA_MGMT_PWD="admin"
export IVIA_CONFIG_YAML=digital_cred_demo.yaml
export IVIA_MGMT_BASE_URL=https://lmi.myidp.ibm.com
export IVIA_CONFIG_YAML=dc_op_config.yaml
export WRP_ADDRESS="192.168.42.102"
python3 -m ibmvia_autoconf | tee dc_demo.log
```