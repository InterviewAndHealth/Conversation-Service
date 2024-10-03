import datetime
import hashlib
import hmac
import urllib.parse

from app import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY


class AwsSignatureGenerator:
    """AWS Signature Generator"""

    ALGORITHM = "AWS4-HMAC-SHA256"
    SIGNED_HEADERS = "host"

    def generate_presigned_url(
        self, method, host, path, service, protocol, expires, query
    ):
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        credential_scope = self.credential_scope(utc_time, service)

        canonical_querystring = ""

        for key, value in query.items():
            canonical_querystring += f"{key}={urllib.parse.quote(value, safe='-_.~')}&"

        canonical_querystring += "X-Amz-Algorithm=" + self.ALGORITHM
        canonical_querystring += "&X-Amz-Credential=" + urllib.parse.quote(
            AWS_ACCESS_KEY_ID + "/" + credential_scope, safe="-_.~"
        )
        canonical_querystring += "&X-Amz-Date=" + self.amz_date(utc_time)
        canonical_querystring += "&X-Amz-Expires=" + str(expires)
        canonical_querystring += "&X-Amz-SignedHeaders=" + self.SIGNED_HEADERS

        canonical_request = self.canonical_request(
            method, path, canonical_querystring, host
        )
        string_to_sign = self.string_to_sign(
            utc_time, credential_scope, canonical_request
        )
        signature = self.signature(string_to_sign, utc_time, service)

        canonical_querystring += "&X-Amz-Signature=" + signature
        return f"{protocol}://{host}{path}?{canonical_querystring}"

    def credential_scope(self, utc_time, service):
        return "/".join([self.datestamp(utc_time), AWS_REGION, service, "aws4_request"])

    def canonical_request(self, method, path, query, host):
        return "\n".join(
            [
                method.upper(),
                path,
                query,
                f"host:{host}\n",
                self.SIGNED_HEADERS,
                hashlib.sha256(("").encode("utf-8")).hexdigest(),
            ]
        )

    def string_to_sign(self, utc_time, credential_scope, canonical_request):
        return "\n".join(
            [
                self.ALGORITHM,
                self.amz_date(utc_time),
                credential_scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )

    def signature(self, string_to_sign, utc_time, service):
        signing_key = self.getSignatureKey(
            AWS_SECRET_ACCESS_KEY, self.datestamp(utc_time), AWS_REGION, service
        )

        return hmac.new(
            signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def getSignatureKey(self, key, dateStamp, regionName, serviceName):
        kDate = self.sign(("AWS4" + key).encode("utf-8"), dateStamp)
        kRegion = self.sign(kDate, regionName)
        kService = self.sign(kRegion, serviceName)
        kSigning = self.sign(kService, "aws4_request")
        return kSigning

    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def amz_date(self, utc_time):
        return utc_time.strftime("%Y%m%dT%H%M%SZ")

    def datestamp(self, utc_time):
        return utc_time.strftime("%Y%m%d")
