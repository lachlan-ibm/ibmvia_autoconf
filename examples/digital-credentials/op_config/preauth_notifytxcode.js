importClass(Packages.com.tivoli.am.fim.trustserver.sts.utilities.IDMappingExtUtils);
importClass(Packages.com.ibm.security.access.httpclient.HttpClient);


IDMappingExtUtils.traceString("\nENTERED PREAUTH_NOTIFY\n" + JSON.stringify(preauth, undefined, 4));
IDMappingExtUtils.traceString("CODE::" + preauth.getTransactionCode());
var headers = new Headers();

headers.addHeader('Content-Type','application/json');
let payload = {
    "message": "Here is your credential authorization code.  Enjoy!",
    "txCode": preauth.getTransactionCode(),
    "original": preauth,
};

IDMappingExtUtils.traceString("payload: " + JSON.stringify(payload));

// host.docker.internal
// let resp = HttpClientV2.httpPost("https://webhook.site/c80f23b7-6948-4598-acb6-05129ac04285", headers, JSON.stringify(payload), null, null, null, null, null, null, null, null, true, null)
let resp = HttpClientV2.httpPost("http://host.docker.internal:8888/txcode", headers, JSON.stringify(payload), null, null, null, null, null, null, null, null, true, null)
