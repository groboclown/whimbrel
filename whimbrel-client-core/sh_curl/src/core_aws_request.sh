#!/bin/sh

# Common code to make a request to AWS.
# Uses Signature Version 4
# http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html

# ENV requirements:
#   AWS_ACCESS_KEY=aws access key
#   AWS_SECRET_KEY=aws secret key
#   AWS_REGION=aws region for the request; must be lower-case
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
#       -x (url prefix)        By default, it adds "https://(host)" to the
#                              URL path.  Specify this argument to use something else.
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

# Note about "echo":
# Different platforms and implementations interpret the
# flags differently.  POSIX compatibility usually has the
# "-e" flag on by default, whereas some do not.  To avoid
# issues with the platforms, we output to a temp file.
# "printf" could be used, but it has issues if the string
# contains a '%' mark.  "echo -n" seems to work
# universally, though.

# All generated files are put under this temp directory.
tmp_dir=/tmp/$$.d
test -d "${tmp_dir}" && rm -rf "${tmp_dir}" 2>/dev/null
mkdir "${tmp_dir}" 2>/dev/null


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
date_epoch=`date -u +%s`
date_8601=`date +"%Y%m%dT%H%M%SZ" -u --date "@$date_epoch"`
date_scope=`date +%Y%m%d -u --date "@$date_epoch"`
scope="${date_scope}/${AWS_REGION}/${service_name}/aws4_request"
user_agent="Boto3/1.2.1 Python/2.7.6 `uname`/`uname -r` Botocore/1.3.5"
if [ -f "${payload_file}" ]; then
    payload_hash=`openssl dgst -sha256 "$payload_file" | cut -f 2 -d ' '`
    if [ -z "${content_type}" ]; then
        echo "$0 must provide -c parameter when -f parameter is given."
        exit 1
    fi
else
    touch "${tmp_dir}/empty_payload_hash"
    payload_hash=`openssl dgst -sha256 "${tmp_dir}/empty_payload_hash" | cut -f 2 -d ' '`
fi
# Canonical headers and signed headers.  Note that they must appear in
# alphabetical order.
signed_headers=""
canonical_headers_file="${tmp_dir}/canonical_headers.txt"
# Note trailing newline at the end of the file when complete with a line.
touch "${canonical_headers_file}"
if [ ! -z "$content_type" ]; then
    # Add the semicolon here
    signed_headers="content-type;"
    echo "content-type:${content_type}" >> "${canonical_headers_file}"
fi
#signed_headers="${signed_headers}host;x-amz-content-sha256;x-amz-date"
signed_headers="${signed_headers}host;user-agent;x-amz-date"
echo "host:${host}" >> "${canonical_headers_file}"
echo "user-agent:${user_agent}" >> "${canonical_headers_file}"
#echo "x-amz-content-sha256:${payload_hash}" >> "${canonical_headers_file}"
echo "x-amz-date:${date_8601}" >> "${canonical_headers_file}"
if [ ! -z "${extra_header_name}" ]; then
    extra_header_name_lower=`echo -n "${extra_header_name}" | tr [A-Z] [a-z]`
    signed_headers="${signed_headers};${extra_header_name_lower}"
    echo "${extra_header_name_lower}:${extra_header_value}" >> "${canonical_headers_file}"
fi

canonical_request_file="${tmp_dir}/canonical_request.txt"
echo "${request_type}" > "${canonical_request_file}"
echo "${url_path}" >> "${canonical_request_file}"
echo "${query_parameters}" >> "${canonical_request_file}"
# canonical headers file is produced with a trailing newline.
cat "${canonical_headers_file}" >> "${canonical_request_file}"
# Need an extra newline to separate headers from signed headers.
echo "" >> "${canonical_request_file}"
echo "${signed_headers}" >> "${canonical_request_file}"
# Do not end the file with a newline, so "-n"
echo -n "${payload_hash}" >> "${canonical_request_file}"

canonical_request_hash=`openssl dgst -sha256 "${canonical_request_file}" | cut -f 2 -d ' '`

string_to_sign_file="${tmp_dir}/string_to_sign.txt"
echo "AWS4-HMAC-SHA256" > "${tmp_dir}/string_to_sign.txt"
echo "${date_8601}" >> "${tmp_dir}/string_to_sign.txt"
echo "${scope}" >> "${tmp_dir}/string_to_sign.txt"
# Do not end the file with a newline, so "-n"
echo -n "${canonical_request_hash}" >> "${tmp_dir}/string_to_sign.txt"

# Four-step signing key calculation
sk_dateKey=`echo -n "${date_scope}" | openssl dgst -sha256 -mac HMAC -macopt key:"AWS4${AWS_SECRET_KEY}" | cut -f 2 -d ' '`
sk_dateRegionKey=`echo -n "${AWS_REGION}" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateKey} | cut -f 2 -d ' '`
sk_dateRegionServiceKey=`echo -n "${service_name}" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateRegionKey} | cut -f 2 -d ' '`
signing_key=`echo -n "aws4_request" | openssl dgst -sha256 -mac HMAC -macopt hexkey:${sk_dateRegionServiceKey} | cut -f 2 -d ' '`

request_signature=`openssl dgst -sha256 -mac HMAC -macopt hexkey:${signing_key} "${string_to_sign_file}" | cut -f 2 -d ' '`

if [ ${debug} = 1 ]; then
    echo "DEBUG:     temp file dir: ${tmp_dir}"
    echo "DEBUG:       url request: ${full_url}"
    echo "DEBUG:      request type: ${request_type}"
    echo "DEBUG:    signed headers: ${signed_headers}"
    echo "DEBUG:              date: ${date_8601} / ${date_scope}"
    echo "DEBUG:             scope: ${scope}"
    echo "DEBUG:      payload file: ${payload_file}"
    echo "DEBUG:      payload hash: ${payload_hash}"
    echo "DEBUG:      request hash: ${canonical_request_hash}"
    echo "DEBUG:       signing key: ${signing_key}"
    echo "DEBUG: request signature: ${request_signature}"
fi

if [ ${debug} = 0 ]; then
    # Clear out the temporary files only if not debugging.
    test -d ${tmp_dir} && rm -rf ${tmp_dir} 2>/dev/null
fi

# Perform the request
authorization_line="Credential=${AWS_ACCESS_KEY}/${scope}, SignedHeaders=${signed_headers}, Signature=${request_signature}"
if [ -f "$payload_file" -a ! -z "$content_type" ]; then
    if [ -z "${extra_header_name}" ]; then
        exec curl -X "$request_type" --data "@${payload_file}" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "X-Amz-Date: ${date_8601}" \
            -H "Accept-Encoding: identity" \
            -H "User-Agent: ${user_agent}" \
            -H "Content-Type: ${content_type}"
            #-H "x-amz-content-sha256: ${payload_hash}" \
    else
        exec curl -X "$request_type" --data "@${payload_file}" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "X-Amz-Date: ${date_8601}" \
            -H "Accept-Encoding: identity" \
            -H "User-Agent: ${user_agent}" \
            -H "Content-Type: ${content_type}" \
            -H "${extra_header_name}: ${extra_header_value}"
            #-H "x-amz-content-sha256: ${payload_hash}" \
    fi
else
    if [ -z "${extra_header_name}" ]; then
        exec curl -X "$request_type" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "X-Amz-Date: ${date_8601}" \
            -H "Accept-Encoding: identity" \
            -H "User-Agent: ${user_agent}"
            #-H "x-amz-content-sha256: ${payload_hash}" \
    else
        exec curl -X "$request_type" \
            -v "${full_url}" \
            -H "Authorization: AWS4-HMAC-SHA256 ${authorization_line}" \
            -H "X-Amz-Date: ${date_8601}" \
            -H "Accept-Encoding: identity" \
            -H "User-Agent: ${user_agent}" \
            -H "${extra_header_name}: ${extra_header_value}"
            #-H "x-amz-content-sha256: ${payload_hash}" \
    fi
fi
