importClass(Packages.com.tivoli.am.fim.trustserver.sts.utilities.OAuthMappingExtUtils);
importClass(Packages.com.ibm.security.access.user.UserLookupHelper);
importClass(Packages.com.tivoli.am.fim.trustserver.sts.utilities.IDMappingExtUtils);

/*
 * Retrieve the username and password from the request.
 */

var username = stsuu.getContextAttributes().getAttributeValueByName("username");
var password = stsuu.getContextAttributes().getAttributeValueByName("password");

/*
 * Retrieve the LDAP handle and then perform a lookup on the user DN.
 */

var userLookupHelper = new UserLookupHelper("myldap");
var user = userLookupHelper.getUserByNativeId(
                            "cn="+username+",dc=iswga");

/*
 * Check the result.  If the user was found we attempt to authenticate using
 * the supplied password.
 */
if (user.hasError()) {
    OAuthMappingExtUtils.throwSTSException("Unable to authenticate user.");
} else if (!user.authenticate(password)) {
    OAuthMappingExtUtils.throwSTSException("Invalid user or password.");
} else {
    userData.uid = user.user.dn;
    userData.given_name = user.user.cn;
    userData.family_name = user.user.sn;
    //userData.sub = user.user.dn;
}