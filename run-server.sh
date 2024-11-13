#!/bin/bash
# (C) 2024 GoodData Corporation

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVER_CMD="${SCRIPT_DIR}/.venv/bin/gooddata-flight-server"

export PYTHONPATH="${SCRIPT_DIR}/src"
export CONFIG_ENV="${1:-dev}"

DEV_LOG=""

if [[ "$CONFIG_ENV" == "dev" ]]; then
   DEV_LOG="--dev-log"
fi

# You can set the following environment variables to set or override
# any settings that can be loaded from configuration files.
#
#export GOODDATA_FLIGHT_SERVER__LISTEN_HOST="..."
#export GOODDATA_FLIGHT_SERVER__LISTEN_PORT="..."
#export GOODDATA_FLIGHT_SERVER__ADVERTISE_HOST="..."
#export GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT="..."
#export GOODDATA_FLIGHT_SERVER__USE_TLS="true"
#export GOODDATA_FLIGHT_SERVER__TLS_CERTIFICATE="@/path/to/server/cert.pem"
#export GOODDATA_FLIGHT_SERVER__TLS_PRIVATE_KEY="@/path/to/server/key.pem"
#export GOODDATA_FLIGHT_SERVER__HEALTH_CHECK_HOST="0.0.0.0"
#export GOODDATA_FLIGHT_SERVER__HEALTH_CHECK_PORT="8877"
#export GOODDATA_FLIGHT_SERVER__AUTHENTICATION_METHOD="token"
#export GOODDATA_FLIGHT_SERVER__TOKEN_VERIFICATION="EnumeratedTokenVerification"
#export GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS='[""]'

$SERVER_CMD start \
              --methods-provider gooddata_flexconnect \
              --config \
                config/${CONFIG_ENV}.server.toml \
                config/flexconnect.config.toml \
              --logging-config config/default.logging.ini \
              ${DEV_LOG}
