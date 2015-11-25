#!/bin/sh

# UUID
# This is Linux specific.
# FreeBSD should use /compat/linux/proc/sys/kernel/random/uuid
UUID=`cat /proc/sys/kernel/random/uuid`

if [ -z "$AWS_ACCESS_KEY" -o -z "$AWS_SECRET_KEY" -o -z "$2" -o ! -f "$2" -o -z "$3" -o -z "$4" ]; then
  exit 1
fi

# If the payload is empty, use this content hash
emptyStringHash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

# Needs to be configurable
contentType="text/plain"

region="$1"
srcFile="$2"
bucket="$3"
destPath="$4"
service="s3"


payloadHash=`openssl dgst -sha256 ${srcFile} | sed 's/^.* //'`

queryString=""
canonicalRequest="PUT\n/${destPath}\n${queryString}\nhost;x-amz-content-sha256;x-amz-date;content-type\n${payloadHash}"
canonicalRequestHash=`echo -en $canonicalRequest | openssl dgst -sha256 | sed 's/^.* //'`

# Iso 8601 basic format
date8601=`date -I`
dateScope=`date +%Y%m%d`
scope="${dateScope}/${region}/${service}/aws4_request"
stringToSign="AWS4-HMAC-SHA256\n${date8601}\n${scope}\n${canonicalRequestHash}"

# Four-step signing key calculation
sk_dateKey=`echo -n "${dateScope}" | openssl dgst -sha256 -mac HMAC -macopt key:"AWS4${AWS_SECRET_KEY}" | sed 's/^.* //'`
sk_dateRegionKey=`echo -n "${region}" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_datekey} | sed 's/^.* //'`
sk_dateRegionServiceKey=`echo -n ${service} | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateRegionKey} | sed 's/^.* //'`
signingKey=`echo -n "aws4_request" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateRegionServiceKey} | sed 's/^.* //'`

requestSignature=`openssl dgst -sha256 -mac HMAC -macopt hexkey:${signingKey} ${srcFile} | sed 's/^.* //'`


curl -X PUT -T "${srcFile}" \
  -H "Host: ${bucket}.s3.amazonaws.com" \
  -H "x-amx-content-sha256: ${payloadHash}" \
  -H "x-amz-date: ${date8601}" \
  -H "Content-Type: ${contentType}" \
  -H "Authorization: AWS4-HMAC-SHA256 Credential=${AWS_ACCESS_KEY}/${scope}, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=${requestSignature}"
  https://${bucket}.s3.amazonaws.com/${destPath}

