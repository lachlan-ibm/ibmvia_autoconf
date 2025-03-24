#!/bin/python
"""
@copyright: IBM
"""
import sys
import os
import logging
import json
import requests
import pyivia
import time
import typing

from .appliance import Appliance_Configurator as APPLIANCE
from .container import Docker_Configurator as CONTAINER
from .access_control import AAC_Configurator as AAC
from .webseal import WEB_Configurator as WEB
from .federation import FED_Configurator as FED
from .util.data_util import FILE_LOADER, optional_list
from .util.configure_util import deploy_pending_changes, creds, old_creds, mgmt_base_url, config_yaml
from .util.constants import HEADERS, LOG_LEVEL

logging.basicConfig(stream=sys.stdout, level=os.environ.get(LOG_LEVEL, logging.DEBUG))
_logger = logging.getLogger(__name__)

class IVIA_Configurator(object):
    #Only restart containers if we import PKI or apply a license
    needsRestart = False

    def old_password(self, config_file):
        rsp = requests.get(mgmt_base_url(config_file), auth=old_creds(config_file), headers=HEADERS, verify=False)
        if rsp.status_code == 403:
            return False
        return True


    def lmi_responding(self, config_file):
        url = mgmt_base_url(config_file)
        for _ in range(12):
            try:
                rsp = requests.get(url, verify=False, allow_redirects=False, timeout=6)
                _logger.debug("\trsp.sc={}; rsp.url={}".format(rsp.status_code, rsp.headers.get('Location', 'NULL')))
                if rsp.status_code == 302 and 'Location' in rsp.headers and '/core/login' in rsp.headers['Location']:
                    _logger.info("LMI returning login page")
                    return True
            except:
                pass # Wait and try again
            _logger.debug("\t{} not responding yet".format(url))
            time.sleep(15)
        return False


    class Admin_Password(typing.TypedDict):
        '''
        Example:: 

            mgmt_user: 'administrator'
            mgmt_pwd: 'S3cr37Pa55w0rd!'
            mgmt_old_pwd: 'administrator'

        .. note:: These properties are overridden by ``IVIA_MGMT_*`` environment variables

        '''

        mgmt_user: str
        'Administrator user to run configuration as.'

        mgmt_pwd: str
        'Secret to authenticate as the Administrator user.'

        mgmt_old_pwd: str
        'Password to update for the Administrator user.'

    def set_admin_password(self, old, new):

        response = self.factory.get_system_settings().sysaccount.update_admin_password(old_password=old[1], password=new[1])
        if response.success == True:
            _logger.info("Successfully updated admin password")
        else:
            _logger.error("Failed to update admin password:/n{}".format(response.data))


    def accept_eula(self):
        rsp = self.factory.get_system_settings().first_steps.set_sla_status()
        if rsp.success == True:
            _logger.info("Accepted SLA")
        else:
            _logger.error("Failed to accept SLA:\n{}".format(rsp.data))


    class FIPS(typing.TypedDict):
        '''

        Example::

                fips:
                  fips_enabled: True
                  tls_v10_enabled: False
                  tls_v11_enabled: False

        '''

        fips_enabled: bool
        'Enable FIPS 140-2 Mode.'
        tls_v10_enabled: bool
        'Allow TLS v1.0 for LMI sessions.'
        tls_v11_enabled: bool
        'Allow TLS v1.1 for LMI sessions'

    def fips(self, config):
        if config != None and config.appliance and config.appliance.fips and \
                config.appliance.fips.fips_enabled == True:
            fips_settings = self.factory.get_system_settings().fips.get_settings().json
            if fips_settings.get("fipsEnabled", False) == False:
                response = self.factory.get_system_settings().fips.update_settings(**config.appliance.fips)
                if response.success == True:
                    _logger.info("Successfully enabled FIPS mode.")
                else:
                    _logger.error("Failed to enable FIPS mode using config:\n{}\n{}".format(
                                                json.dumps(fips_settings, indent=4), response.data))


    def complete_setup(self):
        if self.factory.get_system_settings().first_steps.get_setup_status().json.get("configured", True) == False:
            rsp = self.factory.get_system_settings().first_steps.set_setup_complete()
            assert rsp.status_code == 200, "Did not complete setup"
            deploy_pending_changes(self.factory, self.config, restartContainers=False)
            _logger.info("Completed setup")

    def _apply_trial_cert(self, config):
        trialCert = optional_list(FILE_LOADER.read_file(config.activations.trial_license))[0]
        rsp = self.factory.get_system_settings().licensing.trial_activation(trialCert['path'])
        if rsp.success == True:
            _logger.info("Successfully applied trial license.")
        else:
            _logger.error("Failed to activate Verify Access modules with supplied trail license:\n{}\n{}".format(
                                trialCert['path'], rsp.data))

    def _apply_license(self, module, code):
        # Need to activate appliance
        rsp = self.factory.get_system_settings().licensing.activate_module(code)
        if rsp.success == True:
            _logger.info("Successfully applied {} license".format(module))
            self.needsRestart = True
        else:
            _logger.error("Failed to apply {} license:\n{}".format(module, rsp.data))

    def _activateBaseAppliance(self, config):
        if config.activation is not None and config.activation.webseal is not None:
            _logger.debug("Activating base module")
            self._apply_license("wga", config.activation.webseal)

    def _activateAdvancedAccessControl(self, config):
        if config.activation is not None and config.activation.access_control is not None:
            _logger.debug("Activating access control module")
            self._apply_license("mga", config.activation.access_control)

    def _activateFederation(self, config):
        if config.activation is not None and config.activation.federation is not None:
            _logger.debug("Activating federations module")
            self._apply_license("federation", config.activation.federation)



    class Module_Activations(typing.TypedDict):
        '''
        Example::

                  activation:
                    webseal: "example"
                    access_control: !secret verify-access/isva-secrets:access_control_code
                    federation: !environment ISVA_ACCESS_CONTROL_CODE


                  activation:
                    trial_license: issued/trial.pem

        '''

        trial_license: typing.Optional[str]
        'Trial license file issued from https://isva-trial.verify.ibm.com/'
        webseal: typing.Optional[str]
        'License code for the WebSEAL Reverse Proxy module.'
        access_control: typing.Optional[str]
        'License code for the Advanced Access Control module.'
        federation: typing.Optional[str]
        'License for the Federations module.'

    def activate_appliance(self, config):
        system = self.factory.get_system_settings()
        activations = system.licensing.get_activated_modules().json
        _logger.debug("Existing activations: {}".format(activations))
        if config.activations != None and config.activations.trial_license != None:
            self._apply_trial_cert(config)
        else:
            if not any(module.get('id', None) == 'wga' and module.get('enabled', "False") == "True" for module in activations):
                self._activateBaseAppliance(config)
            if not any(module.get('id', None) == 'mga' and module.get('enabled', "False") == "True" for module in activations):
                self._activateAdvancedAccessControl(config)
            if not any(module.get('id', None) == 'federation' and module.get('enabled', "False") == "True" for module in activations):
                self._activateFederation(config)
        _logger.debug("Appliance activated")


    def _import_signer_certs(self, database, parsed_file):
        ssl = self.factory.get_system_settings().ssl_certificates
        rsp = ssl.import_signer(database, os.path.abspath(parsed_file['path']), label=parsed_file['name'])
        if rsp.success == True:
            _logger.info("Successfully uploaded {} signer certificate to {}".format(
                parsed_file['name'], database))
            self.needsRestart = True
        else:
            _logger.error("Failed to upload {} signer certificate to {} database\n{}".format(
                parsed_file['name'], database, rsp.data))


    def _load_signer_certificates(self, database, server, port, label):
        ssl = self.factory.get_system_settings().ssl_certificates
        rsp = ssl.load_signer(database, server, port, label)
        if rsp.success == True:
            _logger.info("Successfully loaded {} signer certificate to {}".format(
                str(server) + ":" + str(port), database))
            self.needsRestart = True
        else:
            _logger.error("Failed to load {} signer certificate to {}/n{}".format(
                str(server) + ":" + str(port), database, rsp.data))


    def _import_personal_cert(self, db_name, cert):
        ssl = self.factory.get_system_settings().ssl_certificates
        personal_parsed_file = optional_list(FILE_LOADER.read_file(cert.p12_file))[0]
        rsp = ssl.import_personal(db_name, 
                                    file_path=os.path.abspath(personal_parsed_file['path']), 
                                    password=cert.get("secret", ""))
        if rsp.success == True:
            _logger.info("Successfully uploaded {} personal certificate to {}".format(
                personal_parsed_file['name'], db_name))
            self.needsRestart = True
        else:
            _logger.error("Failed to upload {} personal certificate to {}\n{}".format(
               personal_parsed_file['path'], db_name, rsp.data))


    class SSL_Certificates(typing.TypedDict):
        '''
        Example::

                  ssl_certificates:
                  - name: "lmi_trust_store"
                    personal_certificates:
                    - path: "ssl/lmi_trust_store/personal.p12"
                      secret: "S3cr37"
                    signer_certificates:
                    - "ssl/lmi_trust_store/signer.pem"
                  - name: "rt_profile_keys"
                    signer_certificates:
                    - "ssl/rt_profile_keys/signer.pem"
                  - kdb_file: "my_keystore.kdb"
                    stash_file: "my_keystore.sth"

        '''

        class Personal_Certificate(typing.TypedDict):
            path: str
            'Path to file to import as a personal certificate.'
            secret: typing.Optional[str]
            'Optional secret to decrypt personal certificate.'

        class Load_Certificate(typing.TypedDict):
            server: str
            'Domain name or address of web service.'
            port: int
            'Port Web service is listening on.'
            label: str
            'Name of retrieved X509 certificate alias in SSL database.'

        name: typing.Optional[str]
        'Name of SSL database to configure. If database does not exist it will be created. Either ``name`` or ``kdb_file`` must be defined.'
        kdb_file: typing.Optional[str]
        'Path to the .kdb file to import as a SSL database. Required if importing a SSL KDB.'
        stash_file: typing.Optional[str]
        'Path to the .sth file for the specified ``kdb_file``. Required if ``kdb_file`` is set.'
        signer_certificates: typing.Optional[typing.List[str]]
        'List of file paths for signer certificates (PEM or DER) to import.'
        personal_certificates: typing.Optional[typing.List[Personal_Certificate]]
        'List of file paths for personal certificates (PKCS#12) to import.'
        load_certificates: typing.Optional[typing.List[Load_Certificate]]
        'Load X509 certificates from a TCPS endpoints.'

    def import_ssl_certificates(self, config):
        ssl_config = config.ssl_certificates
        ssl = self.factory.get_system_settings().ssl_certificates
        if ssl_config:
            old_databases = [d['id'] for d in ssl.list_databases().json]
            for database in ssl_config:
                if database.name != None: # Create the database
                    if database.name not in old_databases:
                        rsp = ssl.create_database(database.name, db_type='kdb')
                        if rsp.success == True:
                            _logger.info("Successfully created {} SSL Certificate database".format(
                                database.name))
                        else:
                            _logger.error("Failed to create {} SSL Certificate database".format(
                                database.name))
                            continue
                elif database.kdb_file != None and database.sth_file != None: #Import the database
                    kdb_f = optional_list(FILE_LOADER.read_file(database.kdb_file))[0]
                    sth_f = optional_list(FILE_LOADER.read_file(database.sth_file))[0]
                    rsp = ssl.import_database(kdb_file=kdb_f.get("path"), sth_file=sth_f.get("path"))
                    if rsp.success == True:
                        _logger.info("Successfully imported {} SSL KDB file".format(database.kdb_file))
                    else:
                        _logger.error("Failed to import {} SSL KDB file:\n{}\n{}".format(database.kdb_file,
                                        json.dumps(database, indent=4), rsp.data))
                else:
                    _logger.error("SSL Database config provided but cannot be identified: {}".format(
                                                                                json.dumps(database, indent=4)))
                if database.personal_certificates:
                    for cert in database.personal_certificates:
                        self._import_personal_cert(database.name, cert)
                if database.signer_certificates:
                    for fp in database.signer_certificates:
                        signer_parsed_files = FILE_LOADER.read_files(fp)
                        for parsed_file in signer_parsed_files:
                            self._import_signer_certs(database.name, parsed_file)
                if database.load_certificates:
                    for item in database.load_certificates:
                        self._load_signer_certificates(database.name, item.server, item.port, item.label)
        if self.needsRestart == True:
            deploy_pending_changes(self.factory, self.config)
            self.needsRestart == False


    class Admin_Config(typing.TypedDict):
        '''
        Examples::

                   admin_cfg:
                     session_timeout: 7200
                     sshd_client_alive: 300
                     console_log_level: "AUDIT"
                     accept_client_certs: true

        The complete list of properties that can be set by this key can be found in the `pyivia <https://lachlan-ibm.github.io/pyivia/systemsettings.html#pyivia.core.system.adminsettings.AdminSettings.update>`_ documentation.
        '''
        min_heap_size: typing.Optional[int]
        'The minimum heap size, in megabytes, for the JVM.'
        max_heap_size: typing.Optional[int]
        'The minimum heap size, in megabytes, for the JVM.'
        session_timeout: typing.Optional[int]
        'The length of time, in minutes, that a session can remain idle before it is deleted (valid values``0 - 720``). A default value of ``120`` is used.'
        session_inactive_timeout: typing.Optional[int]
        'The length of time, in minutes, that a session can remain idle before it is deleted (valid values = ``-1 - 720``). A default value of ``30`` is used. A value of ``-1`` disables the inactivity timeout.'
        http_port: typing.Optional[int]
        'The TCP port on which the LMI will listen.'
        https_port: typing.Optional[int]
        'The SSL port on which the LMI will listen. A default value of ``443`` is used.'
        sshd_port: typing.Optional[int]
        'The port on which the SSH daemon will listen. A default value of ``22`` is used. Please note that if using the appliance clustering capability all nodes in the cluster must be configured to use the same port for the SSH daemon.'
        sshd_client_alive: typing.Optional[int]
        'The number of seconds that the server will wait before sending a null packet to the client. A value of ``-1`` means using the default timeout settings.'
        swap_size: typing.Optional[int]
        'The amount of allocated swap space, in Megabytes. There must be enough disk space on the active partition to store the swap file, otherwise an error will be logged in the system log file and the default amount of swap space will be used. (only present in the response if a value has been set).'
        min_threads: typing.Optional[int]
        'The minimum number of threads which will handle LMI requests. A default value of ``6`` is used.'
        max_threads: typing.Optional[int]
        'The maximum number of threads which will handle LMI requests. A default value of ``6`` is used.'
        max_pool_size: typing.Optional[int]
        'The maximum number of connections for the connection pool. The default value is ``100``.'
        lmi_debugging_enabled: typing.Optional[bool]
        'A boolean value which is used to control whether LMI debugging is enabled or not. By default debugging is disabled.'
        validate_client_cert_identity: typing.Optional[bool]
        'The console messaging level of the LMI (valid values include ``INFO``, ``AUDIT``, ``WARNING``, ``ERROR`` and ``OFF``). A default value of ``OFF`` is used.'
        exclude_csrf_checking: typing.Optional[str]
        'A comma-separated string which lists the users for which CSRF checking should be disabled. Regular expressions are accepted, and any embedded commas should be escaped with the " character. This option is required if you wish to access a Web service, using client certificates for authentication, from a non-browser based client. An example might be ``cn=scott,o=ibm,c=us,cn=admin,o=dummyCorp,c=*``.'
        enabled_server_protocols: typing.Optional[int]
        'Specifies which secure protocols will be accepted when connecting to the LMI. The supported options include: ``TLS``, ``TLSv1``, ``TLSv1.1`` and ``TLSv1.2``.'
        enabled_tls: typing.Optional[typing.List[str]]
        'List of Enabled TLS protocols for the local management interface. Valid values include ``TLSv1``, ``TLSv1.1`` and ``TLSv1.2``.'
        console_log_level: typing.Optional[str]
        'The console messaging level of the LMI (valid values include ``INFO``, ``AUDIT``, ``WARNING``, ``ERROR`` and ``OFF``). A default value of ``OFF`` is used.'
        accept_client_certs: typing.Optional[bool]
        'A boolean value which is used to control whether SSL client certificates are accepted by the local management interface. By default SSL client certificates are accepted.'
        log_max_files: typing.Optional[int]
        'The maximum number of log files that are retained. The default value is ``2``.'
        log_max_size: typing.Optional[int]
        'The maximum size (in MB) that a log file can grow to before it is rolled over. The default value is ``20``'
        http_proxy: typing.Optional[str]
        'The proxy ``<host>:<port>`` to be used for HTTP communication from the LMI. The port component is optional and will default to ``80``.'
        https_proxy: typing.Optional[str]
        'The proxy ``<host>:<port>`` to be used for HTTPS communication from the LMI. The port component is optional and will default to ``443``.'
        login_header: typing.Optional[str]
        'This is a customizable header that is displayed when accessing the login page in a web browser and after logging in via SSH. Multiple lines of text can be specified by using the sequence "n", which will be interpreted as a line break.'
        login_msg: typing.Optional[str]
        'This is a customizable message that is displayed when accessing the login page in a web browser and after logging in via SSH. Multiple lines of text can be specified by using the sequence "n", which will be interpreted as a line break.'
        access_log_fmt: typing.Optional[str]
        'The template string to use for the LMI access.log file. If not set the access log is disabled (default).'
        lmi_msg_timeout: typing.Optional[int]
        'This is a timeout (in seconds) for notification messages that appear in the LMI. A value of ``0`` indicates that the messages should not timeout. The default value is ``5`` seconds.'
        valid_verify_domains: typing.Optional[str]
        'This is a space separated list of valid domains for IBM Security Verify. These domains are used by the IBM Security Verify wizard to ensure that only valid hostnames are used.'

    def admin_config(self, config):
        if config.admin_config != None:
            rsp = self.factory.get_system_settings().admin_settings.update(**config.admin_config)
            if rsp.success == True:
                _logger.info("Successfully set admin config")
            else:
                _logger.error("Failed to set admin config using:\n{}\n{}".format(
                    json.dumps(config.admin_config), rsp.data))


    def _system_users(self, users):
        for user in users:
            rsp = None
            if user.operation == "add":
                rsp = self.factory.get_system_settings().sysaccount.create_user(
                        user=user.name, password=user.password, groups=user.groups)
            elif user.operation == "update":
                if user.password != None:
                    rsp = self.factory.get_system_settings().sysaccount.update_user(
                            user.name, password=user.password)
                    if rsp.success == True:
                        _logger.info("Successfully update password for {}".format(user.name))
                    else:
                        _logger.error("Failed to update password for {}:\n{}".format(
                            user.name, rsp.data))
                if user.groups != None:
                    for g in user.groups:
                        rsp = self.factory.get_system_settings().sysaccount.add_user(
                                group=g, user=user.name)
                        if rsp.success == True:
                            _logger.info("Successfully added {} to {} group".format(
                                user.name, g))
                        else:
                            _logger.error("Failed to add {} to {} group:\n{}".format(
                                user.name, g, rsp.data))
            elif user.operation == "delete":
                rsp = self.factory.get_system_settings().sysaccount.delete_user(user.name)
                if rsp.success == True:
                    _logger.info("Successfully removed user {}".format(user.name))
                else:
                    _logger.error("Failed to remove system user {}:\n{}".format(
                        user.name, rsp.data))

    def _system_groups(self, groups):
        for group in groups:
            rsp = None
            if group.operation == "add" or group.operation == "update":
                rsp = self.factory.get_system_settings().sysaccount.create_group(group.id)
            elif group.operation == "delete":
                rsp = self.factory.get_system_settings().sysaccount.delete_group(group.id)
            else:
                _logger.error("Operation {} is not permitted for groups".format(group.operation))
                continue
            if rsp.success == True:
                _logger.info("Successfully {} group {}".format(group.operation, group.id))
            else:
                _logger.error("Failed to {} group {}:\n{}\n{}".format(
                    group.operation, group.id, json.dumps(group, indent=4), rsp.data))

            if group.operation == "update":
                for user in group.users:
                    rsp = self.factory.get_system_settings().sysaccount.add_user(user=user, group=group.id)
                    if rsp.success == True:
                        _logger.info("Successfully added {} to group {}".format(user, group.id))
                    else:
                        _logger.error("Failed to add user {} to group {}:\n{}\n{}".format(
                            user, group.id, json.dumps(group, indent=4), rsp.data))


    class Account_Management(typing.TypedDict):
        '''
        Example::

                account_management:
                  users:
                  - name: !secret default/isva-secrets:cfgsvc_user
                    operation: "update"
                    password: !secret default/isva-secrets:cfgsvc_secret
                    groups:
                    - "aGroup"
                    - "anotherGroup"
                 groups:
                 - name: "adminGroup"
                   operation: "update"
                   users:
                   - "admin"
                   - "anotherUser"

        '''
        class Management_User(typing.TypedDict):
            operation: str
            'Operation to perform with user. ``add`` | ``update`` | ``delete``.'
            name: str
            'Name of the user to create, remove or update.'
            password: typing.Optional[str]
            'Password to authenticate as user. Required if creating user.'
            groups: typing.Optional[typing.List[str]]
            'Optional list of groups to add user to.'


        class Management_Group(typing.TypedDict):
            '''
            .. note:: Groups are created before users; therefore if a user is being created and added to a group then this should be done in the user configuration entry.
            '''
            operation: str
            'Operation to perform with group. ``add`` | ``update`` | ``delete``.'
            id: str
            'Name of group to create.'
            users: typing.Optional[typing.List[str]]
            'Optional list of users to add to group.'

        users: typing.Optional[typing.List[Management_User]]
        'Optional list of management users to configure'
        groups: typing.Optional[typing.List[Management_Group]]
        'Optional list of management groups to configure.'

    def account_management(self, config):
        if config.account_management != None:
            if config.account_management.groups != None:
                self._system_groups(config.account_management.groups)
            if config.account_management.users != None:
                self._system_users(config.account_management.users)


    def _add_auth_role(self, role):
        if role.operation == "delete":
            rsp = self.factory.get_system_settings().mgmt_authorization.delete_role(role.name)
            if rsp.success == True:
                _logger.info("Successfully removed {} authorization role".format(role.name))
            else:
                _logger.error("Failed to remove {} authorization role:\n{}".format(
                    role.name, rsp.data))
        elif role.operation in ["add", "update"]:
            configured_roles = self.factory.get_system_settings().mgmt_authorization.get_roles().json
            exists = False
            for r in configured_roles:
                if r['name'] == role.name:
                    exits = True
                    break
            rsp = None
            if exits == True:
                rsp = self.factory.get_system_settings().mgmt_authorization.update_role(
                        name=role.name, users=role.users, groups=role.groups, features=role.features)
            else:
                rsp = self.factory.get_system_settings().mgmt_authorization.create_role(
                        name=role.name, users=role.users, groups=role.groups, features=role.features)
            if rsp.success == True:
                _logger.info("Successfully configured {} authorization role".format(role.name))
            else:
                _logger.error("Failed to configure {} authorization role:\n{}".format(
                    role.name, rsp.data))
        else:
            _logger.error("Unknown operation {} for role configuration:\n{}".format(
                role.operation, json.dumps(role, indent=4)))


    class Management_Authorization(typing.TypedDict):
        '''
        Example::

               management_authorization:
                 authorization_enforcement: True
                 roles:
                 - operation: update
                   name: "Configuration Service"
                   users:
                   - name: "cfgsvc"
                     type: "local"
                   features:
                   - name: "shared_volume"
                     access: "w"

        '''

        class Role(typing.TypedDict):
            class User(typing.TypedDict):
                name: str
                'Name of user'
                type: str
                'Type of user. ``local`` | ``remote``.'

            class Group(typing.TypedDict):
                name: str
                'name of group.'
                type: str
                'Type of group. ``local`` | ``remote``.'

            class Feature(typing.TypedDict):
                name: str
                'Name of feature.'
                access: str
                'Access to grant to feature. ``r`` | ``w``.'

            operation: str
            'Operation to perform on authorization role. ``add`` | ``remove`` | ``update``.'
            name: str
            'Name of role.'
            users: typing.Optional[typing.List[User]]
            'Optional list of users to add to role.'
            groups: typing.Optional[typing.List[Group]]
            'Optional list of groups to add to role.'
            features: typing.List[Feature]
            'List of features to authorize users / groups for.'

        authorization_enforcement: bool
        'Enable role based authorization for this deployment.'

        roles: typing.Optional[typing.List[Role]]
        'Optional list of roles to modify for role based authorization.'

    def management_authorization(self, config):
        if config.management_authorization != None and config.management_authorization.roles != None:
            for role in config.management_authorization.roles:
                self._add_auth_role(role)
            if config.management_authorization.authorization_enforcement:
                rsp = self.factory.get_system_settings().mgmt_authorization.enable(
                        enforce=config.management_authorization.authorization_enforcement)
                if rsp.success == True:
                    _logger.info("Successfully enabled role based authorization")
                else:
                    _logger.error("Failed to enable role based authorization:\n{}".format(rsp.data))


    class Management_Authentication(typing.TypedDict):
        '''
        Example::

                management_authentication:
                  auth_type: "federation"
                  oidc:
                    client_id: "27d55f1c-285a-11ef-81ec-14755ba358db"
                    client_secret: "SDFGc3ffFSD3m4Xtg1"
                    discovery_endpoint: "https://verify.ibm.com/.well-known/openid-configuration"
                    require_pkce: true
                    enable_admin_group: false
                    enable_tokenmapping: false

        '''

        class LDAP(typing.TypedDict):
            host: str
            'Specifies the name of the LDAP server. '
            port: str
            'Specifies the port over which to communicate with the LDAP server.'
            ssl: bool
            'Specifies whether SSL is used when the system communicates with the LDAP server.'
            key_database: str
            'Specifies the name of the key database file (without any path information). This parameter is required if ``ssl`` is ``true``'
            cert_label: str
            'Specifies the name of the certificate within the Key database that is used if client authentication is requested by the LDAP server.'
            user_attribute: str
            'Specifies the name of the LDAP attribute which holds the supplied authentication user name of the user.'
            group_member_attribute: str
            'Specifies the name of the LDAP attribute which is used to hold the members of a group. '
            base_dn: str
            'Specifies the base DN which is used to house all administrative users.'
            admin_group_dn: str
            'Specifies the DN of the group to which all administrative users must belong.'
            anon_bind: bool
            'Specifies whether the LDAP user registry supports anonymous bind. If set to false, ``bind_dn`` and ``bind_password`` are required.'
            bind_dn: typing.Optional[str]
            'Specifies the DN of the user which will be used to bind to the registry. This user must have read access to the directory. This parameter is required if anon_bind is ``false``'
            bind_password:typing.Optional[str]
            'Specifies the password which is associated with the bind_dn. This parameter is required if anon_bind is ``false``.'
            debug: bool
            'Specifies whether the capturing of LDAP debugging information is enabled or not.'
            enable_usermapping: bool
            'Specifies whether mapping of the incoming client certificate DN is enabled.'
            usermapping_script: str
            'Specifies the javascript script that will map the incoming client certificate DN. The script will be passed a Map containing the certificate dn, rdns, principal, cert, san and the user_attribute, group_member_attribute and base_dn from this configuration. If not specified a default script is used. Only valid if ``enable_usermapping`` is ``true``.'
            enable_ssh_pubkey_auth: typing.Optional[bool]
            'Specifies whether or not users in the LDAP server can log in via SSH using SSH public key authentication. If this value is not provided, it will default to ``false``.'
            ssh_pubkey_auth_attribute: str
            'Specifies the name of the LDAP attribute which contains a user\'s public key data. This field is required if SSH public key authentication is enabled.'

        class OIDC(typing.TypedDict):
            client_id: str
            'The OIDC Client Identifier.'
            client_secret: str
            'The OIDC Client Secret.'
            discovery_endpoint: str
            'The OIDC Discovery (well-known) endpoint.'
            enable_pkce: bool
            'Specifies whether the Public key Code Exchange extension is enforced.'
            enable_admin_group: bool
            'Specifies whether a user must be a member of a particular group to be considered an administrator user.'
            group_claim: typing.Optional[str]
            'The OIDC token claim to use as group membership. This claim can either be a String, or a list of Strings. The default value is ``groupIds``.'
            admin_group: typing.Optional[str]
            'The name of the group which a user must be a member of to be considered an administrator user. The default value is ``adminGroup``.'
            user_claim: typing.Optional[str]
            'Specifies the OIDC token claim to use as the username. The default value is ``sub``.'
            keystore: typing.Optional[str]
            'The SSL Truststore to verify connections the the OIDC OP. The default value if ``lmi_trust_store``.'
            enable_tokenmapping: bool
            'Specifies whether custom claim to identity mapping is performed using a JavaScript code fragment.'
            tokenmapping_script: str
            'The custom JavaScript code fragment to map an identity token to a username/group membership.'

        auth_type: str
        'Specifies whether the local user database or the remote LDAP user registry is used for authentication. If this parameter is set to local, then all other fields are ignored. Valid values include ``local``, ``federation`` and ``remote``.'
        ldap: typing.Optional[LDAP]
        'LDAP specific configuration properties. Only one of LDAP or OIDC should be defined'
        oidc: typing.Optional[OIDC]
        'OIDC specific configuration properties. Only one of LDAP or OIDC should be defined'

    def management_authentication(self, config):
        if config.management_authentication != None:
            ma = config.management_authentication
            methodArgs = {}
            if ma.ldap:
                methodArgs.update({
                    "ldap_host": ma.ldap.host,
                    "ldap_port": ma.ldap.port, 
                    "enable_ssl": ma.ldap.ssl, 
                    "key_database": ma.ldap.key_database,
                    "cert_label": ma.ldap.cert_label,
                    "user_attribute": ma.ldap.user_attribute,
                    "group_member_attribute": ma.ldap.group_member_attribute,
                    "base_dn": ma.ldap.base_dn,
                    "admin_group_dn": ma.ldap.admin_group_dn,
                    "anon_bind": ma.ldap.anon_bind,
                    "bind_dn": ma.ldap.bind_dn,
                    "bind_password": ma.ldap.bind_password,
                    "ldap_debug": ma.ldap.ldap_debug,
                    "enable_usermapping": ma.ldap.enable_usermapping,
                    "usermapping_script": ma.ldap.usermapping_script,
                    "enable_ssh_pubkey_auth": ma.ldap.enable_ssh_pubkey_auth,
                    "ssh_pubkey_auth_attribute": ma.ldap.ssh_pubkey_auth_attribute, 
                    })
            elif ma.oidc:
                methodArgs.update({
                    "oidc_client_id": ma.oidc.oidc_client_id,
                    "oidc_client_secret": ma.oidc.oidc_client_secret,
                    "oidc_discovery_endpoint": ma.oidc.oidc_discovery_endpoint,
                    "oidc_enable_pkce": ma.oidc.oidc_enable_pkce,
                    "oidc_enable_admin_group": ma.oidc.oidc_enable_admin_group,
                    "oidc_group_claim": ma.oidc.oidc_group_claim,
                    "oidc_admin_group": ma.oidc.oidc_admin_group,
                    "oidc_user_claim": ma.oidc.oidc_user_claim,
                    "oidc_keystore": ma.oidc.oidc_keystore,
                    "enable_tokenmapping": ma.oidc.enable_tokenmapping, 
                    "tokenmapping_script": ma.oidc.tokenmapping_script
                })
            ma = config.management_authentication
            rsp = self.factory.get_system_settings().management_authentication.update(ma.auth_type, **methodArgs)
            if rsp.success == True:
                _logger.info("Successfully updated the management authentication configuration")
            else:
                _logger.error("Failed to update the management authentication configuration:\n{}\nconfig:\n{}".format(
                                                                                    rsp.data, json.dumps(ma, indent=4)))


    class Advanced_Tuning_Parameter:
        '''
        Example::

                  advanced_tuning_parameters:
                  - name: "wga.rte.embedded.ldap.ssl.port"
                    value: 636
                  - name: "password.policy"
                    value: "minlen=8 dcredit=1 ucredit=1 lcredit=1"
                    description: "Enforced PAM password quality for management accounts."

        '''
        name: str
        'Name of the Advanced Tuning Parameter.'
        value: str
        'Value of the Advanced Tuning Parameter.'
        description: typing.Optional[str]
        'optional description of the Advanced Tuning Parameter.'
        operation: str
        'Operation which should be performed on advanced tuning parameter. Valid values include ``add`` | ``delete`` | ``update``.'

    def advanced_tuning_parameters(self, config):
        if config.advanced_tuning_parameters != None:
            old_atps = optional_list(self.factory.get_system_settings().advanced_tuning.list_parameters().json)
            for atp in config.advanced_tuning_parameters:
                if atp.operation == "delete":
                    uuid = None
                    for p in old_atps:
                        if p['key'] == atp.name:
                            uuid = p['uuid']
                            break
                    rsp = self.factory.get_system_settings().advanced_tuning.delete_parameter(uuid=uuid)
                    if rsp.success == True:
                        _logger.info("Successfully removed {} Advanced Tuning Parameter".format(atp.name))
                    else:
                        _logger.error("Failed to remove {} Advanced Tuning Parameter:\n{}".format(
                            atp.name, rsp.data))
                elif atp.operation == "update":
                    exists = False
                    for p in old_atps:
                        if p['key'] == atp.name:
                            exists = True
                            break
                    rsp = None
                    if exists == True:
                        rsp = self.factory.get_system_settings().advanced_tuning.update_parameter(
                            key=atp.name, value=atp.value, comment=atp.description)
                    else:
                        rsp = self.factory.get_system_settings().advanced_tuning.create_parameter(
                            key=atp.name, value=atp.value, comment=atp.description)
                    if rsp.success == True:
                        _logger.info("Successfully updated {} Advanced Tuning Parameter".format(atp.name))
                    else:
                        _logger.error("Failed to update {} Advanced Tuning Parameter with:\n{}\n{}".format(
                            atp.name, json.dumps(atp, indent=4), rsp.data))
                elif atp.operation == "add":
                    rsp = self.factory.get_system_settings().advanced_tuning.create_parameter(
                        key=atp.name, value=atp.value, comment=atp.description)
                    if rsp.success == True:
                        _logger.info("Successfully add {} Advanced Tuning Parameter".format(atp.name))
                    else:
                        _logger.error("Failed to add {} Advanced Tuning Parameter with:\n{}\n{}".format(
                            atp.name, json.dumps(atp, indent=4), rsp.data))
                else:
                    _logger.error("Unknown operation {} for Advanced Tuning Parameter:\n{}".format(
                        atp.operation, json.dumps(atp, indent=4)))


    class Snapshot(typing.TypedDict):
        '''
        Example::

                snapshot: "snapshot/isva-2023-02-08.snapshot"

        '''
        snapshot: str
        'Path to signed snapshot archive file.'

    def apply_snapshot(self, config):
        if config != None and config.snapshot != None:
            snapshotConfig = config.snapshot
            rsp = self.factory.get_system_settings().snapshot.upload(snapshotConfig.snapshot)
            if rsp.success == True:
                _logger.info("Successfully applied snapshot [{}]".format(snapshotConfig.snapshot))
                deploy_pending_changes(self.factory, self.config)
            else:
                _logger.error("Failed to apply snapshot [{}]\n{}".format(snapshotConfig.snapshot),
                        rsp.data)


    class Extensions(typing.TypedDict):
        '''
        Example::

                extensions:
                - extension: "Instana/instana.ext"
                  third_party_packages:
                  - "Instana/agent.rpm"
                  properties:
                    extId: "instanaAgent"
                    instanaAgentKey: !environment INSTANA_AGENT_KEY
                    instanaHost: !environment INSTANA_HOST
                    instanaPort: 443
                    mvnRepositoryUrl: "https://artifact-public.instana.io"
                    mvnRepositoryFeaturesPath: "artifactory/features-public@id=features@snapshots@snapshotsUpdate=never"
                    mvnRepositorySharedPath: "artifactory/shared@id=shared@snapshots@snapshotsUpdate=never"

        '''

        extension: str
        'The signed extension file to be installed on Verify Identity Access.'
        third_party_packages: typing.Optional[str]
        'An optional list of third party packages to be uploaded to Verify Identity Access as part of the installation process.'
        properties: typing.Optional[dict]
        'Key-Value properties to give the extension during the installation process. This list of properties will vary with the type of extension being installed.'

    def install_extensions(self, config):
        if config != None and config.extensions != None:
            for extension in config.extensions:
                third_party_files = []
                if extension.third_party_packages != None:
                    for tpp in extension.third_party_packages:
                        third_party_files += FILE_LOADER.read_file(tpp)
                third_party_files = [tpf.get("path", "INVALID") for tpf in third_party_files]
                ext_file = optional_list(FILE_LOADER.read_file(extension.extension))[0].get('path', "INVALID")
                rsp = self.factory.get_system_settings().extensions.create_extension(
                                        ext_file=ext_file, properties=extension.properties, third_party_packages=third_party_files)
                if rsp.success == True:
                    _logger.info("Successfully installed {} extension".format(extension.extension))
                    self.needsRestart = True
                else:
                    _logger.error("Failed to install extension:\n{}\n{}".format(
                                            json.dumps(extension, indent=4), rsp.data))

    class Remote_Syslog(typing.TypedDict):
        '''
        Example::

                remote_syslog:
                - server: "127.12.7.1"
                  port: 514
                  debug: False
                  protocol: "udp"
                  sources:
                  - name: "WebSEAL:ISAM:request.log"
                    tag: "isva-dev"
                    facility: "local0"
                    severity: "debug"
                  - name: "Runtime Messages"
                    tag: "isva-dev"
                    facility: "syslog"
                    severity: "info"

        .. note: This is an array of elements.
        '''

        class Forwarder(typing.TypedDict):
            name: str
            'The name of the log file source. The list of available source names can be retrieved via the ``source_names`` Web service.'
            tag: str
            'The tag to be used to designate the messages which originate from this source. This tag will be prepended to all messages that are sent to the remote syslog server.'
            facility: str
            'The syslog facility which will be used when sending messages to the remote syslog server. Valid values include ``kern``, ``user``, ``mail``, ``daemon``, ``auth``, ``syslog``, ``lpr``, ``news``, ``uucp``, ``cron``, ``security``, ``ftp``, ``ntp``, ``logaudit``, ``logalert``, ``clock``, ``local0``, ``local1``, ``local2``, ``local3``, ``local4``, ``local5``, ``local6`` and ``local7``.'
            severity: int
            'The syslog severity which will be used when sending messages to the remote syslog server. Valid values include ``emerg``, ``alert``, ``crit``, ``error``, ``warning``, ``notice``, ``info`` and ``debug``. '

        server: str
        'The IP address or host name of the remote syslog server.'
        port: int
        'The port on which the remote syslog server is listening.'
        debug: bool
        'Whether the forwarder process will be started in debug mode. All trace messages will be sent to the log file of the remote syslog forwarder.'
        protocol: str
        'The protocol which will be used when communicating with the remote syslog server. Valid values include ``udp``, ``tcp`` and ``tls``.'
        format: typing.Optional[str]
        'The format of the messages which are forwarded to the rsyslog server. Valid options include ``rfc-3164`` and ``rfc-5424``. Default value is ``rfc-3164``'
        keyfile: typing.Optional[str]
        'The name of the key file which contains the SSL certificates used when communicating with the remote syslog server (e.g. pdsrv). This option is required if the protocol is ``tls``.'
        ca_certificate: typing.Optional[str]
        'The label which is used to identify within the SSL key file the CA certificate of the remote syslog server. This option is required if the protocol is ``tls``.'
        client_certificate: typing.Optional[str]
        'The label which is used to identify within the SSL key file the client certificate which will be used during mutual authentication with the remote syslog server.'
        permitted_peers: typing.Optional[str]
        'The subject DN of the remote syslog server. If this policy data is not specified any certificates which have been signed by the CA will be accepted.'
        sources: typing.List[Forwarder]
        'The source of the log file entries which will be sent to the remote syslog server. '

    def remote_syslog(self, config):
        if config != None and config.remote_syslog != None and isinstance(config.remote_syslog, list):
            for server in config.remote_syslog:
                rsp = self.factory.get_analysis_diagnostics().remote_syslog.add_server(**server)
                if rsp.success == True:
                    _logger.info("Successfully added {} to the remote syslog configuration.".format(server.server))
                    self.needsRestart = True
                else:
                    _logger.error("Failed to update the remote syslog configuration with:\n{}\n{}".format(
                        json.dumps(server, indent=4) , rsp.data))


    def configure_base(self, appliance, container):
        base_config = None
        model = None
        if self.config.appliance is not None:
            base_config = self.config.appliance
            model = appliance
        elif self.config.container is not None:
            base_config = self.config.container
            model = container
        else:
            _logger.error("Deployment model cannot be found in config.yaml, skipping container/appliance configuration.")
            return
        self.apply_snapshot(base_config)
        self.admin_config(base_config)
        self.import_ssl_certificates(base_config)
        self.account_management(base_config)
        self.management_authentication(base_config) # This may cause an appliance to become un-contactable; eg. if auth changes from basic to bearer
        self.management_authorization(base_config)
        self.advanced_tuning_parameters(base_config)
        model.configure()

        self.activate_appliance(base_config)
        self.install_extensions(base_config)
        if self.needsRestart == True:
            deploy_pending_changes(self.factory, self.config)
            self.needsRestart = False

    def _check_aac_fed_licenses(self):
        activations = self.factory.get_system_settings().licensing.get_activated_modules().json
        result = False
        _logger.debug("Existing activations: {}".format(activations))
        if any(module.get('id', None) == 'mga' and module.get('enabled', "False") == "True" for module in activations):
            result = True
        if any(module.get('id', None) == 'federation' and module.get('enabled', "False") == "True" for module in activations):
            result = True
        return result

    def global_config(self, aac, fed):
        config = None
        if self.config.appliance is not None:
            config = self.config.appliance
        elif self.config.container is not None:
            config = self.config.container
        else:
            _logger.error("Deployment model cannot be found in config.yaml, skipping global configuration.")
            return

        options = ['template_files', 'mapping_rules', 'server_connections', 'runtime_properties', 
                        'point_of_contact', 'advanced_configuration', 'access_policies', 'attribute_sources']
        configRequired = False
        for k in config.keys():
            if k in options:
                configRequired = True
                break
        if configRequired == True and self._check_aac_fed_licenses() == False:
            _logger.error("You must activate the Advanced Access Control or Federation modules to configure global properties.")
            return
        elif configRequired == False:
            _logger.info("Skipping global configuration")
            return

        aac.upload_files(config)
        aac.server_connections(config)
        aac.runtime_configuration(config)
        fed.configure_poc(config)
        aac.advanced_config(config)
        fed.configure_access_policies(config)
        fed.configure_attribute_sources(config)

        deploy_pending_changes(self.factory, self.config)


    def get_modules(self):
        appliance = APPLIANCE(self.config, self.factory)
        container = CONTAINER(self.config, self.factory)
        web = WEB(self.config, self.factory)
        aac = AAC(self.config, self.factory)
        fed = FED(self.config, self.factory)
        return appliance, container, web, aac, fed


    def configure(self, config_file=None):
        _logger.info("Reading configuration file")
        self.config = config_yaml(config_file)
        _logger.info("Testing LMI connectivity")
        if self.lmi_responding(self.config) == False:
            _logger.error("Unable to contact LMI, exiting")
            sys.exit(1)
        _logger.info("LMI responding, begin configuration")
        if self.old_password(self.config):
            self.factory = pyivia.Factory(mgmt_base_url(self.config), *old_creds(self.config))
            self.accept_eula()
            self.fips(self.config)
            self.complete_setup()
            self.set_admin_password(old_creds(self.config), creds(self.config))
            self.factory = pyivia.Factory(mgmt_base_url(self.config), *creds(self.config))
        else:
            self.factory = pyivia.Factory(mgmt_base_url(self.config), *creds(self.config))
            self.accept_eula()
            self.fips(self.config)
            self.complete_setup()
        appliance, container, web, aac, fed = self.get_modules()
        self.configure_base(appliance, container)
        self.global_config(aac, fed)
        web.configure()
        aac.configure()
        fed.configure()
        #Configure the remote syslog after everything else as it might rely on config we create
        if self.config.appliance is not None:
            self.remote_syslog(self.config.appliance)
        elif self.config.container is not None:
            self.remote_syslog(self.config.container)
        if self.needsRestart == True:
            deploy_pending_changes(self.factory, self.config)
            self.needsRestart = False

if __name__ == "__main__":
    IVIA_Configurator().configure()
