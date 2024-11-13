#!/bin/bash
# (C) 2024 GoodData Corporation

#
# Example script to start the FlexConnect server inside a Docker image.
#
# The configuration applied by this script is aimed towards a production
# deployment.
#
# By default, the example will try to start production-like server on localhost with
# TLS; you have to provide certificate and private key yourself. See settings below.
#
# Deploying to real production, you will have to make some tweaks of course. Most
# notably the advertise host setting, the TLS certificate and key and then the
# secret tokens used for authentication.
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CERTS_DIR="${SCRIPT_DIR}/test_data/certs"
mkdir -p "${CERTS_DIR}"

export CONFIG_ENV="${1:-prod}"

DEV_LOG=""

if [[ "$CONFIG_ENV" == "dev" ]]; then
   DEV_LOG="--dev-log"
fi

# Make the server listen on all interfaces inside the
# running container.
export GOODDATA_FLIGHT_SERVER__LISTEN_HOST="0.0.0.0"
export GOODDATA_FLIGHT_SERVER__LISTEN_PORT="17001"

# But make the server advertise hostname that is reachable from
# outside the container.
export GOODDATA_FLIGHT_SERVER__ADVERTISE_HOST="localhost"
export GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT="17001"

# This enables health-checking endpoints. They are HTTP endpoints /ready and /live
# that report 202 when server is ready and/or alive and 500 otherwise.
export GOODDATA_FLIGHT_SERVER__HEALTH_CHECK_HOST="0.0.0.0"
export GOODDATA_FLIGHT_SERVER__HEALTH_CHECK_PORT="8877"

# Configure TLS certificate and private key for the server.
#
# IMPORTANT
#
# The certificate and private key are not part of the Docker image;
# instead, they are expected to be provided externally. In this case, they
# are attached to the `/tls-files` directory inside the container:
# see `docker run --volume`. In case of this example, the test_data/certs
# are mounted to the `/tls-files` - you likely want to change this to
# suit your deployment.
#
# Alternatively, if it suits you better, you can set the actual certificate
# and private key values into these two environment variables instead of pointing
# to a file somewhere.
#
export GOODDATA_FLIGHT_SERVER__TLS_CERTIFICATE="@/tls-files/server-cert.pem"
export GOODDATA_FLIGHT_SERVER__TLS_PRIVATE_KEY="@/tls-files/server-key.pem"
export GOODDATA_FLIGHT_SERVER__USE_TLS="true"
export GOODDATA_FLIGHT_SERVER__AUTHENTICATION_METHOD="token"
export GOODDATA_FLIGHT_SERVER__TOKEN_VERIFICATION="EnumeratedTokenVerification"

# Set one or more values of secret tokens. The client must present themselves with
# one of the token from this list. If the client does not present a token or
# the token is not in the list, the request fails with authentication error.
#
#export GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS='[""]'

docker run \
  --env GOODDATA_FLIGHT_SERVER__LISTEN_HOST \
  --env GOODDATA_FLIGHT_SERVER__LISTEN_PORT \
  --env GOODDATA_FLIGHT_SERVER__ADVERTISE_HOST \
  --env GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT \
  --env GOODDATA_FLIGHT_SERVER__USE_TLS \
  --env GOODDATA_FLIGHT_SERVER__TLS_CERTIFICATE \
  --env GOODDATA_FLIGHT_SERVER__TLS_PRIVATE_KEY \
  --env GOODDATA_FLIGHT_SERVER__AUTHENTICATION_METHOD \
  --env GOODDATA_FLIGHT_SERVER__TOKEN_VERIFICATION \
  --env GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS \
  -p ${GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT}:${GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT} \
  --volume $CERTS_DIR:/tls-files:Z \
  flexconnect-server:latest start \
  --methods-provider gooddata_flexconnect \
  --config \
    /config/${CONFIG_ENV}.server.toml \
    /config/flexconnect.config.toml \
  --logging-config /config/default.logging.ini \
  ${DEV_LOG}
