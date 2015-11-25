#!/bin/sh

# Common code to make a request to AWS.
# Uses Signature Version 4
# http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html

# ENV requirements:
#   AWS_ACCESS_KEY=aws access key
#   AWS_SECRET_KEY=aws secret key
#   AWS_REGION=aws region for the request
# Usage:
#   core_aws_request.sh
#       -s (service name)      The AWS service requested (e.g. s3)
#       -r (request type)      GET, PUT, or other kinds of supported HTTP methods.
#                              Defaults to "GET".
#       -p (url path)          The URL path (without the host name), should begin with a
#                              leading slash (/), up to but not including the '?'.
#                              Should be normalized according to RFC 3986.  If the
#                              absolute path is empty, use '/'.
#       -q (query parameters)  URI-encoded query string: Do not URL-encode A-Z, a-z, 0-9,
#                              hyphen (-), underscore (_), period (.), and tilde (~).
#                              Percent-encode all other characters with %XY, where X and Y
#                              are hexadecimal characters (0-9 and uppercase A-F).
#                              Space is '%20', not '+'.  These also need to be
#                              sorted by ASCII character code.
#       -f (payload file)      File to upload.  Optional.  Must include "-c" parameter
#                              if included.
#       -c (content type)      Content type of the file to upload.  Must be provided only
#                              if the "-f" parameter is provided.
#       -h (url host name)     URL host to connect to.
#       -d (header) (value)    An extra signed header name and value.
# Exit code:
#   The curl exit code.  Also, "1" if there was a parameter error.

service_name=""
request_type="GET"
url_path=""
query_parameters=""
payload_file=""
content_type=""
host=""
extra_header_name=""
extra_header_value=""
url_prefix=""
debug=0

while [ ! -z "$1" ]; do
    case "$1" in
        "-s") shift; service_name="$1";;
        "-r") shift; request_type="$1";;
        "-p") shift; url_path="$1";;
        "-q") shift; query_parameters="$1";;
        "-f") shift; payload_file="$1";;
        "-c") shift; content_type="$1";;
        "-h") shift; host="$1";;
        "-d") shift; extra_header_name="$1"; shift; extra_header_value="$1";;
        "-x") shift; url_prefix="$1";;
        "-D") debug=1;;
        "*") echo "$0 invalid invocation"; exit 1;;
    esac
    shift
done

# Setup request parameters
if [ -z "${url_prefix}" ]; then
    full_url="https://${host}${url_path}"
else
    full_url="${url_prefix}${url_path}"
fi
if [ ! -z "$query_parameters" ]; then
    full_url="${full_url}?${query_parameters}"
fi
signed_headers="host;x-amz-content-sha256;x-amz-date"
#date_8601=`date -I`
date_epoch=`date -u +%s`
date_8601=`date +"%Y%m%dT%H%M%SZ" --date "@$date_epoch"`
date_scope=`date +%Y%m%d --date "@$date_epoch"`
scope="${date_scope}/${AWS_REGION}/${service_name}/aws4_request"
if [ -f "${payload_file}" ]; then
    payload_hash=`openssl dgst -sha256 "$payload_file" | cut -f 2 -d ' '`
    if [ -z "${content_type}" ]; then
        echo "$0 must provide -c parameter when -f parameter is given."
        exit 1
    fi
else
    payload_hash=`echo -n '' | openssl dgst -sha256 | cut -f 2 -d ' '`
fi
# Note trailing newline
canonical_headers="host:${host}\nx-amz-content-sha256:${payload_hash}\nx-amz-date:${date_8601}\n"
if [ ! -z "${extra_header_name}" ]; then
    extra_header_name_lower=`echo -n "${extra_header_name}" | tr A-Z a-z`
    signed_headers="${signed_headers};${extra_header_name_lower}"
    # Note trailing newline
    canonical_headers="${canonical_headers}${extra_header_name_lower}:${extra_header_value}\n"
fi

if [ ! -z "$content_type" ]; then
    signed_headers="$signed_headers;content-type"
    # Note trailing newline
    canonical_headers="${canonical_headers}content-type:${content_type}\n"
fi

canonical_request="${request_type}\n/${url_path}\n${query_parameters}\n${canonical_headers}\n${signed_headers}\n${payload_hash}"
canonical_request_hash=`echo -en "$canonical_request" | openssl dgst -sha256 | cut -f 2 -d ' '`

string_to_sign="AWS4-HMAC-SHA256\n${date_8601}\n${scope}\n${canonical_request_hash}"

# Four-step signing key calculation
sk_dateKey=`echo -n "${date_scope}" | openssl dgst -sha256 -mac HMAC -macopt key:"AWS4${AWS_SECRET_KEY}" | cut -f 2 -d ' '`
sk_dateRegionKey=`echo -n "${AWS_REGION}" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateKey} | cut -f 2 -d ' '`
sk_dateRegionServiceKey=`echo -n ${service_name} | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateRegionKey} | cut -f 2 -d ' '`
signing_key=`echo -n "aws4_request" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateRegionServiceKey} | cut -f 2 -d ' '`

request_signature=`echo -n "${string_to_sign}" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${signing_key} | cut -f 2 -d ' '`

if [ $debug = 1 ]; then
    echo "DEBUG:       url request: ${full_url}"
    echo "DEBUG:      request type: ${request_type}"
    echo "DEBUG:    signed headers: ${signed_headers}"
    echo "DEBUG:              date: ${date_8601} / ${date_scope}"
    echo "DEBUG:             scope: ${scope}"
    echo "DEBUG:      payload file: ${payload_file}"
    echo "DEBUG:      payload hash: ${payload_hash}"
    echo -e "DEBUG: canonical headers: ${canonical_headers}"
    echo -e "DEBUG: canonical request: ${canonical_request}"
    echo "DEBUG:      request hash: ${canonical_request_hash}"
    echo -e "DEBUG:    string to sign: ${string_to_sign}"
    echo "DEBUG:       signing key: ${signing_key}"
    echo "DEUBG: request signature: ${request_signature}"
fi

# Perform the request
authorization_line="Credential=$AWS_ACCESS_KEY/$scope,SignedHeaders=$signed_headers,Signature=$request_signature"
if [ -f "$payload_file" -a ! -z "$content_type" ]; then
    if [ -z "${extra_header_name}" ]; then
        exec curl -X "$request_type" --data "@${payload_file}" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "x-amz-content-sha256: ${payload_hash}" \
            -H "x-amz-date: ${date_8601}" \
            -H "Content-Type: ${content_type}"
    else
        exec curl -X "$request_type" --data "@${payload_file}" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "x-amz-content-sha256: ${payload_hash}" \
            -H "x-amz-date: ${date_8601}" \
            -H "Content-Type: ${content_type}" \
            -H "${extra_header_name}: ${extra_header_value}"
    fi
else
    if [ -z "${extra_header_name}" ]; then
        exec curl -X "$request_type" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "x-amz-content-sha256: ${payload_hash}" \
            -H "x-amz-date: ${date_8601}"
    else
        exec curl -X "$request_type" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "x-amz-content-sha256: ${payload_hash}" \
            -H "x-amz-date: ${date_8601}" \
            -H "${extra_header_name}: ${extra_header_value}"
    fi
fi
