Developing configuration definitions
####################################

JSON schema files are provided to help administrators validate their deployment definitions without running the autoconf module.

IDE editors can use a directive at the top of the file to fetch the schema definitions which can be used to validate the YAML you are generating.

.. code-block:: yaml
    # yaml-language-server: $schema=https://github.com/ibm-verify/ibm-verify-identity-access-automated-configurator/docs/schemas/ivia-config.json
    mgmt_base_url: "https://localhost:9443"
    mgmt_user: admin
    container:
      activation:
        trial_license: ISAM_Trial.cer
    . . .


Note: if you are using the YAML keyword macros for secrets or splitting configuration into multiple files, you may rquire additional properties in your
`.vscode/settings.json` file to correctly resolve the keywords:

.. code-block:: json

  "yaml.customTags": [
    "!include scalar:object",
    "!secret scalar:string",
    "!secret:tofile scalar:string",
    "!configmap:tofile scalar:string",
    "!environment scalar:string",
    "!vault scalar:string",
    "!vault:tofile scalar:string"
    ]
