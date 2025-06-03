# (C) 2024 GoodData Corporation
import uuid
from typing import Optional

import gooddata_flight_server as gf
import pyarrow
import structlog
from gooddata_flexconnect import (
    DataSourceMessage,
    ExecutionContext,
    ExecutionType,
    FlexConnectFunction,
    add_data_source_messages_metadata,
)

_LOGGER = structlog.get_logger("sample_flexconnect_function")


class SampleFlexConnectFunction(FlexConnectFunction):
    """
    A sample FlexConnect function. This serves static data. It is not very useful but is
    a good starting point to explain FlexConnect functions:

    - Specify a nice name in `Name` field -> this will be visible in GoodData's
      semantic model
    - Specify `Schema` which describes the result -> this information will be used
      to populate data set columns in GoodData's Semantic Model

    The `call` method does the heavy lifting. This is where you add your custom code to generate the result.
    Typically, the `call` method should inspect the parameters and do the computation as necessary.

    NOTE: when GoodData invokes your function, it may provide a hint on which
    columns it is interested in - it will always be a subset of all columns defined in
    the `Schema`.

    Your code MAY take this into account and return only those desired columns. This is
    a basic optimization that your function can leverage to save bandwidth. The presence of
    `columns` does not mean your function should perform additional aggregations or alter
    how it does the computation - it only tells your code that you can trim some columns
    from the result.

    If you want to learn more, check out the class documentation on the `FlexConnectFunction` class.
    """

    Name = "SampleFlexConnectFunction"
    Schema = pyarrow.schema(
        [
            pyarrow.field("attribute1", pyarrow.string()),
            pyarrow.field("attribute2", pyarrow.string()),
            pyarrow.field("attribute3", pyarrow.bool_()),
            pyarrow.field("fact1", pyarrow.float64()),
            pyarrow.field("fact2", pyarrow.float64()),
            pyarrow.field("fact3", pyarrow.int64()),
        ]
    )

    _StaticData = pyarrow.table(
        {
            "attribute1": ["id1", "id2", "id3", "id4", "id5", "id6"],
            "attribute2": ["value1", "value2", "value3", "value1", "value2", "value3"],
            "attribute3": [True, True, True, False, False, False],
            "fact1": [123.456, 23.45, 8.76, 1.23, 34.56, 567.89],
            "fact2": [0.1, 0.2, 0.3, 0.15, 0.25, 0.35],
            "fact3": [111, 222, 333, 444, 555, 666],
        },
        # This is how you can pas additional data to GoodData.
        # These will then be available in the execution result metadata.
        # If you are not planning to use this feature, feel free to omit this altogether.
        # See https://github.com/gooddata/gooddata-python-sdk/blob/master/gooddata-flexconnect/gooddata_flexconnect/function/data_source_messages.py
        # for additional helper functions to add the DataSourceMessages in case you are using Arrow's RecordBatchReaders.
        metadata=add_data_source_messages_metadata(
            [
                DataSourceMessage(
                    # Unique identifier of the call, this allows you to discern different messages from the same source.
                    correlation_id=str(uuid.uuid4()),
                    # Name of the message source.
                    source=Name,
                    # Type of the message. There are currently no well-known types, but we may add some in the future.
                    type="info",
                    # You can include arbitrary data; however, there are two important limitations:
                    # 1. The data MUST be serializable to JSON.
                    # 2. The data SHOULD be small, there are quite strict limits on the size of the metadata.
                    data={"extra": "data"},
                )
            ]
        ),
    )

    def call(
        self,
        parameters: dict,
        columns: Optional[tuple[str, ...]],
        headers: dict[str, list[str]],
    ) -> gf.ArrowData:
        _LOGGER.info("function_called", parameters=parameters)

        execution_context = ExecutionContext.from_parameters(parameters)
        if execution_context is None:
            # This can happen for invalid invocations that do not come from GoodData
            raise ValueError("Function did not receive execution context.")

        _LOGGER.info("execution_context", execution_context=execution_context)

        if execution_context.execution_type == ExecutionType.REPORT:
            _LOGGER.info(
                "report_execution",
                report_execution_context=execution_context.report_execution_request,
            )
        elif execution_context.execution_type == ExecutionType.LABEL_ELEMENTS:
            _LOGGER.info(
                "label_elements",
                label_elements_execution_context=execution_context.label_elements_execution_request,
            )
        else:
            _LOGGER.info("Received unknown execution request")

        return self._StaticData

    @staticmethod
    def on_load(ctx: gf.ServerContext) -> None:
        """
        You can do one-time initialization here. This function will be invoked
        exactly once during startup.

        Most often, you want to perform function-specific initialization that may be
        further driven by external configuration (e.g., env variables or TOML files).

        The server uses Dynaconf to work with configuration. You can access
        all available configuration values via `ctx.settings`.

        :param ctx: server context
        :return: nothing
        """
        # value = ctx.settings.get("your-setting")
        pass

    def cancel(self) -> bool:
        """
        If you have some long-running operations as part of the `call` method,
        you can implement this method so that it does all the necessary work to cancel them.

        For example, if your `call` body performs some query to a database, you might want
        to implement the query cancellation here.

        Implementing the cancellation is optional.
        If not implemented, the FlexConnect server will still pretend the entire call was
        cancelled - it's just that it will wait for the `call` to finish and then throw the results away.

        If you do not plan on implementing this method, you can delete it altogether:
        it will fall back to the default implementation.

        :return: True, if the cancellation was requested successfully, False otherwise.
        """
        return False
