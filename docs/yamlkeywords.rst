.. _ibmvia_autoconf_yaml_keywords:

YAML configuration keywords
============================

Each module expects a YAML object describing the desired configuration state. There are a number of useful features
which can be used to make configuration files re-usable and version controlled. There are six keywords which
can be used in configuration files:

``!include``
    Include a YAML file as the value of a key. Can be an absolute path or relative to ``IVIA_CONFIG_BASE``.

    .. code-block:: yaml

        container: !include base_config.yaml
        webseal: !include webseal.yaml
        access_control: !include aac.yaml

``!secret``
    Set a key's value from a Kubernetes Secret, using the format ``namespace/name:key``.

    .. code-block:: yaml

        admin_password: !secret default/isva-secrets:admin_secret

``!secret:tofile``
    Load a binary or text file from a Kubernetes Secret and write it to a temporary file. Use this for
    certificates, archives, mapping rules, and templates. If namespace is omitted, autoconf uses the
    namespace of the pod it is running in.

    .. code-block:: yaml

        lmi_certificate:
          p12: !secret:tofile default/lmi-ssl-certs:server.p12
          password: !secret lmi-ssl-passwords:p12-password

``!configmap:tofile``
    Load a binary or text file from a Kubernetes ConfigMap and write it to a temporary file. Works
    identically to ``!secret:tofile`` but reads from ConfigMaps. Use for non-sensitive files such as
    templates and scripts.

    .. code-block:: yaml

        mapping_rules:
          - type: SAML2
            files:
              - !configmap:tofile default/aac-config:saml_mapping.js
        template_files:
          - !configmap:tofile ui-templates:login.zip

``!environment``
    Set a key's value from an environment variable.

    .. code-block:: yaml

        admin_password: !environment IVIA_ADMIN_SECRET

``!vault``
    Set a key's value from a HashiCorp Vault KV secret engine.
    This requires the ``IVIA_HASHIVAULT_BASE`` and ``IVIA_HASHIVAULT_TOKEN``
    environment properties. When the mount is omitted (``path:key`` with
    no ``/`` before the ``:``), the default KV mount ``secret`` is assumed.

    .. code-block:: yaml

        admin_password: !vault ivia/admin:secret

``!vault:tofile``
    Read a value from a HashiCorp Vault KV secret engine and write it to a
    temporary file. Use this for certificates, archives, and other binary or
    text files stored in Vault.

    Binary files must be stored in Vault as a **base64-encoded string** (e.g.
    ``vault kv put secret/lmi-ssl cert=$(base64 -w0 server.p12)``).
    Plain text values are written to the temp file as-is.

    Uses the same ``mount/path:key`` format as ``!vault`` and returns the
    temp file path, exactly like ``!secret:tofile``.

    .. code-block:: yaml

        lmi_certificate:
          p12: !vault:tofile kv/lmi-ssl:server.p12
          password: !vault kv/lmi-ssl:p12-password