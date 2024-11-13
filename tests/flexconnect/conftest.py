# (C) 2024 GoodData Corporation
import os
import socket
from collections.abc import Generator
from contextlib import closing

import gooddata_flight_server as gf
import pytest
from gooddata_flexconnect import create_flexconnect_flight_methods

__current_dir__ = os.path.dirname(os.path.abspath(__file__))
__config_dir__ = os.path.join(__current_dir__, "..", "..", "config")


@pytest.fixture(scope="module")
def testing_server_hostname() -> str:
    return "127.0.0.1"


@pytest.fixture(scope="module")
def testing_server_port() -> int:
    """
    see: https://stackoverflow.com/a/45690594
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def testing_server_env_config(
    testing_server_hostname, testing_server_port
) -> dict[str, str]:
    return {
        "GOODDATA_FLIGHT_SERVER__LISTEN_HOST": testing_server_hostname,
        "GOODDATA_FLIGHT_SERVER__LISTEN_PORT": str(testing_server_port),
        "GOODDATA_FLIGHT_SERVER__ADVERTISE_HOST": testing_server_hostname,
        "GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT": str(testing_server_port),
        "GOODDATA_FLIGHT_SERVER__USE_TLS": "false",
        "GOODDATA_FLIGHT_SERVER__AUTHENTICATION_METHOD": "none",
        "GOODDATA_FLIGHT_SERVER__OTEL_EXPORTER_TYPE": "none",
    }


@pytest.fixture(scope="module")
def testing_server_config_files() -> tuple[str, ...]:
    # intentionally, this uses the main flexconnect config so that all
    # functions developed within the project are loaded in the test server
    #
    # if you need to include additional config files, you add them to
    # this tuple and they will be used during server startup
    return (os.path.join(__config_dir__, "flexconnect.config.toml"),)


@pytest.fixture(scope="module")
def testing_flexconnect_server(
    testing_server_config_files, testing_server_env_config
) -> Generator[gf.GoodDataFlightServer]:
    """
    This fixture starts up Flight server that hosts all FlexConnect functions
    that you have implemented and added to `flexconnect.config.toml`.

    The server is started up and handed over to your tests. You can access
    the location of the running server via it's `location` property. You can
    use that to create flight client and perform Flight RPC calls.
    """
    for env_var, value in testing_server_env_config.items():
        os.environ[env_var] = value

    try:
        server = gf.create_server(
            create_flexconnect_flight_methods,
            config_files=testing_server_config_files,
            dev_log=True,
        )

        server.start()
        server.wait_for_start()

        yield server

        server.stop()
        server.wait_for_stop(timeout=5.0)
    finally:
        for env_var in testing_server_env_config.keys():
            os.environ.pop(env_var)


@pytest.fixture(scope="module")
def flexconnect_call_parameters() -> dict:
    """
    Mock parameters that are passed to the FlexConnect function with valid execution context.
    """
    return {
        "executionContext": {
            "executionType": "REPORT",
            "organizationId": "default",
            "workspaceId": "demo",
            "userId": "demo",
            "timestamp": "2024-09-12T12:51:26+00:00",
            "timezone": "Etc/UTC",
            "weekStart": "sunday",
            "executionRequest": {
                "attributes": [
                    {
                        "localIdentifier": "a_attribute1",
                        "label": {"identifier": {"id": "attribute1", "type": "label"}},
                        "showAllValues": False,
                    }
                ],
                "filters": [
                    {
                        "negativeAttributeFilter": {
                            "label": {
                                "identifier": {"id": "attribute1", "type": "label"}
                            },
                            "notIn": {"values": ["id1"]},
                            "applyOnResult": None,
                        }
                    }
                ],
                "measures": [
                    {
                        "localIdentifier": "m_fact1_min",
                        "definition": {
                            "measure": {
                                "item": {"identifier": {"id": "fact1", "type": "fact"}},
                                "aggregation": "MIN",
                                "computeRatio": False,
                                "filters": [],
                            }
                        },
                    }
                ],
                "auxMeasures": [],
            },
            "reportExecutionRequest": {
                "attributes": [
                    {
                        "localIdentifier": "a_attribute1",
                        "label": {"identifier": {"id": "attribute1", "type": "label"}},
                        "showAllValues": False,
                    }
                ],
                "filters": [
                    {
                        "negativeAttributeFilter": {
                            "label": {
                                "identifier": {"id": "attribute1", "type": "label"}
                            },
                            "notIn": {"values": ["id1"]},
                            "applyOnResult": None,
                        }
                    }
                ],
                "measures": [
                    {
                        "localIdentifier": "m_fact1_min",
                        "definition": {
                            "measure": {
                                "item": {"identifier": {"id": "fact1", "type": "fact"}},
                                "aggregation": "MIN",
                                "computeRatio": False,
                                "filters": [],
                            }
                        },
                    }
                ],
                "auxMeasures": [],
            },
        }
    }
