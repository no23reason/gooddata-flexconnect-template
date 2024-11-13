# (C) 2024 GoodData Corporation
import orjson
import pyarrow.flight

#
# Few sample end-to-end tests which exercise the sample function by making
# Flight RPC calls.
#


def test_list_flexconnect_funs(testing_flexconnect_server):
    c = pyarrow.flight.FlightClient(testing_flexconnect_server.location)

    for flight_info in c.list_flights():
        function_descriptor = orjson.loads(flight_info.descriptor.command)

        assert function_descriptor["functionName"] == "SampleFlexConnectFunction"


def test_function_call(testing_flexconnect_server, flexconnect_call_parameters):
    c = pyarrow.flight.FlightClient(testing_flexconnect_server.location)

    flight_info = c.get_flight_info(
        pyarrow.flight.FlightDescriptor.for_command(
            orjson.dumps(
                {
                    "functionName": "SampleFlexConnectFunction",
                    "parameters": flexconnect_call_parameters,
                }
            )
        )
    )
    data: pyarrow.Table = c.do_get(flight_info.endpoints[0].ticket).read_all()

    assert data.num_rows == 6
    assert data.num_columns == 6
