importClass(Packages.com.tivoli.am.fim.trustserver.sts.utilities.IDMappingExtUtils);
importClass(Packages.com.tivoli.am.fim.trustserver.sts.utilities.OAuthMappingExtUtils);
importClass(Packages.com.ibm.security.access.httpclient.HttpClient);

IDMappingExtUtils.traceString("JS: ENTERED PREAUTH_USERAUTH::");
var payload = preauth.getPayload();
IDMappingExtUtils.traceString("payload: " + JSON.stringify(payload));
IDMappingExtUtils.traceString("CallbackURL::" + preauth.getCallbackURL());
if(payload["type"] == "http"){
    var headers = new Headers();

    headers.addHeader('Content-Type','application/json');
    var payload = preauth.getPayload();
    payload["callbackURL"] = preauth.getCallbackURL()
    IDMappingExtUtils.traceString("payload: " + JSON.stringify(payload));

    let resp = HttpClientV2.httpPost("http://localhost:8080/userauth", headers, JSON.stringify(payload), null, null, null, null, null, null, null, null, true, null)
    if (resp.hasError()) {//getError
        IDMappingExtUtils.traceString("resp.getError(): " + resp.getError());
    } else {
        IDMappingExtUtils.traceString("StatusCode: " + resp.getCode());
        if(resp.getCode() == 200){
            IDMappingExtUtils.traceString("HERE: ");
            var metadata = {};
            metadata.uid = "prabbit";
            metadata.given_name = "peter";
            metadata.family_name = "rabbit";
            metadata.preferred_username = "peter@zoo.org";
            IDMappingExtUtils.traceString("approved: ");
            preauth.approved(metadata);
        }
    }
}

//IDMappingExtUtils.traceString("preauth.isCallback(): " + preauth.isCallback());
else{
    if (preauth.isCallback()) {
        if (payload.status === "approved") {
            var metadata = {};
            metadata.uid = "prabbit";
            metadata.given_name = "peter";
            metadata.family_name = "rabbit";
            metadata.preferred_username = "peter@zoo.org";
            preauth.approved(metadata);
        } else if (payload.status === "denied") {
            IDMappingExtUtils.traceString("denied " );
            preauth.denied();
        } else {
            OAuthMappingExtUtils.throwSTSCustomUserMessageException("Expecting authentication status", 400, "invalid_request");
        }
    } else if (preauth.isCallback() == undefined){
        IDMappingExtUtils.traceString("else if " );
        if (payload.status === "cred_issuer_assertion") {
            var metadata = {};
            metadata.uid = (payload.sub ? payload.sub : "prabbit");
            metadata.given_name = "peter";
            metadata.family_name = "rabbit";
            metadata.preferred_username = "peter@zoo.org";
            preauth.approved(metadata);
        } else if(payload.status === "denied"){
            IDMappingExtUtils.traceString("denied " );
            preauth.denied();
        }  
        else{
            IDMappingExtUtils.traceString("pending " );
            IDMappingExtUtils.traceString("CallbackURL:::" + preauth.getCallbackURL() + ':::');
            preauth.pending();
        }  
    } else  {
        IDMappingExtUtils.traceString("else " );
        IDMappingExtUtils.traceString("$$CallbackURL" + preauth.getCallbackURL() + '$$');
        preauth.pending(); // for initial request, we return pending first
    }
}