
import logging

_logger = logging.getLogger(__name__)

'''
Container for common methods that must occur during the deployment model setup.

Kerberos: must occur after SSL, network setup;  must occur before HVDB setup
'''
class DeploymentBase(object):

    def kerberos_config(self, config, wrp_config, webset):
        if 'kerberos' in config.keys() or 'kerberos' in wrp_config.keys():
            krb5_cfg = config.kerberos
            if 'kerberos' in wrp_config:
                _logger.warning("Kerberos property in web reverse proxy is depreciated. Use appliance or container top level key.")
                if not krb5_cfg:
                    krb5_cfg = wrp_config.kerberos
            webset.kerberos(krb5_cfg)