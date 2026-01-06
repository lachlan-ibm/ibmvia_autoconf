importClass(Packages.com.tivoli.am.fim.trustserver.sts.utilities.IDMappingExtUtils);
/*
 * We want to set the scope based on the client identifier and grant type.  Of
 * particular concern are administrative users.
 */

var grantType = stsuu.getContextAttributes().getAttributeValueByName(
                                                    "grant_type");
var clientID  = stsuu.getContextAttributes().getAttributeValueByName(
                                                    "client_id");

/*
 * If the grant type is a pre-authorized code then we need to add the
 * pre-authorized code to the token data so that it can introspected
 * by the credential issuer later.  It is likely the credential issuer
 * will need to correlate a credential offer with the pre-authorized code
 * value.
 */

if (grantType === "urn:ietf:params:oauth:grant-type:pre-authorized_code") {
    var preAuthorizedCode  = stsuu.getContextAttributes().getAttributeValueByName("pre-authorized_code");
    IDMappingExtUtils.traceString("pre-authorized_code: " + preAuthorizedCode);
    tokenData["pre-authorized_code"] = preAuthorizedCode;
}

const excludeAznClientCheck = new Set(["default_oid4vci_wallet"]);

if (!excludeAznClientCheck.has(clientID)) {

    const adminIDs = new Set(["admin"]);

    if (grantType == "client_credentials" && adminIDs.has(clientID)) {
        tokenData.scope = "admin";
    } else if (grantType == "password") {
        tokenData.scope = "holder";
        //tokenData.sub = stsuu.getAttributeValueByName("uid");
    } else {
        tokenData.scope = "verifier/issuers";
    }

    /*
    * If the grant type is an authorization code (which occurs during OIDC
    * authentication) we want to add the scope to the id token data, based
    * on the client id.
    */
    if (grantType == "authorization_code" && excludeAznClientCheck.has(clientID) != true) {
        if (clientID == "rp_client") {
            idtokenData.scope = "admin";
        } else {
            idtokenData.scope = "verifier/issuers";
        }
    }
}
