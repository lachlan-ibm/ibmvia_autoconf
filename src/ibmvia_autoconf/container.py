#!/bin/python
"""
@copyright: IBM
"""
import logging
import json
#import typing
import copy

from requests import get

from .util.constants import HEADERS
from .util.configure_util import deploy_pending_changes
from .util.data_util import Map
from .util.api_tracker import track_failure

_logger = logging.getLogger(__name__)

class Docker_Configurator(object):

    config = Map()
    #factory = None
    #There are errors deploying changes with some HVDB's so we choose to restart if the config is present not if successful
    needsRestart = False

    def __init__(self, config, factory):
        self.config = config
        self.factory = factory

    """
    class Cluster_Configuration(typing.TypedDict):
        '''
        Example::


                  cluster:
                    runtime_database:
                      type: "postgresql"
                      host: "postgresql"
                      port: 5432
                      ssl: True
                      ssl_keystore: "rt_profile_keys"
                      username: "postgres"
                      password: "Passw0rd"
                      db_name: "isva"

        '''
        class Database(typing.TypedDict):
            type: str
            'Database type. "postgresql" | "db2" | "oracle".'
            host: str
            'Hostname or address of database.'
            port: str
            'Port database is listening on.'
            ssl: bool
            'Enable SSL encryption of connections.'
            ssl_keystore: typing.Optional[str]
            'SSL database to use to verify connections. Only valid if ``ssl == true``.'
            user: str
            'Username to authenticate to database as.'
            password: str
            'Password to authenticate as ``username``.'
            db_name: str
            'Name of the database instance to use.'
            extra_config: typing.Optional[dict]
            'Database type specific configuration.'

        class DistributedSessionCache(typing.TypedDict):
            class Server(typing.TypedDict):
                ip: str
                'The name/IP address over which clients can connect to the DSC.'
                service_port: int
                'The port which can be used by clients to connect to the DSC for session requests.'
                replication_port: int
                'The port which can be used by the DSC to replicate data to a replication DSC.'

            client_grace: int
            'The length of time (in seconds) that a client (aka WebSEAL) has to reconnect before sessions owned by that client are discarded.'
            connection_idle_timeout: int
            'The maximum length of time that a connection from a client can remain idle before it is closed by the server. A value of 0 indicates that connections will not be reused.'
            max_session_lifetime: int
            'The maximum lifetime (in seconds) of any session stored by the DSC.'
            service_port: int
            'The port number on which the DSC will listen for requests.'
            replication_port: int
            'The port number on which the DSC will listen for replication requests.'
            ssl_ciphers: typing.Optional[str]
            'The comma separated list of permissted SSL algorithms for TLS connections to the DSC.'
            worker_threads: int
            'The number of worker threads allocated to processing requests.'
            servers: typing.List[Server]
            'The external connection data for each instance of the DSC. This corresponds to the IP address and ports to which clients will connect. Up to 4 servers may be defined (primary, secondary, tertiary and quaternary). The role of the server will be determined by the order of elements within the servers array.'

        runtime_database: typing.Optional[Database]
        'Configuration for the runtime (HVDB) database.'
        dsc: typing.Optional[DistributedSessionCache]
        'Configuration for the distributed session cache runtime containers.'
    """

    def __set_config_db(self, config_database):
        database = copy.deepcopy(config_database)
        methodArgs = {'db_type': database.pop('type'), 'host': database.pop('host'), 'port': database.pop('port'),
                        'secure': database.pop('ssl'), 'db_key_store': database.pop('ssl_keystore', None), 'embedded': False,
                        'user': database.pop('user'), 'passwd': database.pop('password'), 'db_name': database.pop('db_name'),
                        'extra_config': database
            }
        rsp = self.factory.get_system_settings().cluster.set_config_db(**methodArgs)
        if rsp.success == True:
            _logger.info("Successfully configured config database")
            self.needsRestart = True
        else:
            track_failure('container', 'config_database', rsp, database)
            _logger.error("Failed to configure config database with config:\n{}\n{}".format(
                json.dumps(config_database, indent=4), rsp.data))

    def __set_runtime_db(self, runtime_database):
        database = copy.deepcopy(runtime_database)
        methodArgs = {'db_type': database.pop('type'), 'host': database.pop('host'), 'port': database.pop('port'),
                        'secure': database.pop('ssl'), 'db_key_store': database.pop('ssl_keystore', None), 
                        'user': database.pop('user'), 'passwd': database.pop('password'), 'db_name': database.pop('db_name'), 
                        'extra_config': database
            }
        rsp = self.factory.get_system_settings().cluster.set_runtime_db(**methodArgs)
        if rsp.success == True:
            _logger.info("Successfully configured HVDB")
            self.needsRestart = True
        else:
            track_failure('container', 'runtime_database', rsp, runtime_database)
            _logger.error("Failed to configure HVDB with config:\n{}\n{}".format(
                json.dumps(runtime_database, indent=4), rsp.data))

    def configure_database_and_dsc(self, clusterConfig):
        if clusterConfig == None:
            _logger.info("Cannot find cluster configuration, in a docker environment this is probably bad")
            return

        if clusterConfig.runtime_database != None:
            self.__set_runtime_db(clusterConfig.runtime_database)

        if clusterConfig.config_database != None:
            self.__set_config_db(clusterConfig.config_database)

        if clusterConfig.dsc != None:
            rsp = self.factory.get_system_settings().dsc.set_dsc(**clusterConfig.dsc)
            if rsp.success == True:
                _logger.info("Successfully configured DSC")
                self.needsRestart = True
            else:
                track_failure('container', 'dsc', rsp, clusterConfig.dsc)
                _logger.error("Failed to configure DSC with config:\n{}\n{}".format(
                    json.dumps(clusterConfig.dsc, indent=4), rsp.data))



    def configure(self):
        containerConfig = self.config.container
        if containerConfig == None:
            _logger.info("Unable to find container specific configuration")
            return
        self.configure_database_and_dsc(containerConfig.cluster)
        if self.needsRestart == True:
            deploy_pending_changes(self.factory, self.config, restartContainers=False)

if __name__ == "__main__":
    from .util.configure_util import config_yaml
    from pyivia import Factory
    import sys
    c = Docker_Configurator(
                Factory(sys.argv[1], sys.argv[2], sys.argv[3]), config_yaml())
    c.configure()
