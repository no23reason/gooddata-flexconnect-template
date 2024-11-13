# (C) 2024 GoodData Corporation
from flexconnect.sample_function import SampleFlexConnectFunction


def test_sample_function1(flexconnect_call_parameters):
    fun = SampleFlexConnectFunction.create()
    result = fun.call(flexconnect_call_parameters, None, {})

    assert result is not None
