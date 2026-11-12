
import logging

from .webseal import WEB_Configurator as WEB

_logger = logging.getLogger(__name__)

'''
Container for common methods that must occur during the deployment model setup.

Kerberos: must occur after SSL, network setup;  must occur before HVDB setup
'''
class DeploymentBase(object):

    def kerberos_config(self, config, wrp_config, factory):
        krb5_cfg = None
        if config and 'kerberos' in config.keys():
            krb5_cfg = config.kerberos
        if wrp_config and 'kerberos' in wrp_config.keys():
            _logger.warning("Kerberos property in web reverse proxy is depreciated. Use appliance or container top level key.")
            if not krb5_cfg:
                krb5_cfg = wrp_config.kerberos
        if krb5_cfg:
            WEB(None, factory).kerberos(krb5_cfg)