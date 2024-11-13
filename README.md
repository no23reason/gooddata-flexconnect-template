# GoodData FlexConnect template

This repository serves as a template that you can use to create your own
FlexConnect server that hosts your custom-made functions.

This template lets you focus on building and testing the FlexConnect functions themselves;
the infrastructure and boilerplate related to hosting and exposing your functions
is handled by GoodData code.

## What is FlexConnect

GoodData FlexConnect allows you to build your own data source for GoodData Cloud or Cloud Native.

FlexConnect works with a concept similar to 'table functions' that you may already know
from database technologies.

-  To build your own data source, you implement one or more FlexConnect functions. The
   functions compute and return tabular data - how they do it is completely up to you.
-  The functions are hosted and invoked inside a FlexConnect server (which is included in this package).
-  A running FlexConnect server can be added as a data source to your GoodData Cloud or GoodData Cloud Native.
-  The functions available on FlexConnect server will be mapped to data sets within GoodData's Semantic Model
   and from then on can be used during report computation.

The FlexConnect functions are intended for integration into the GoodData Cloud's semantic model
and are then used for report computation. This influences how the interface of FlexConnect function looks like:

- The schema of tabular data returned by a function must be known up-front
- The function arguments are prescribed by GoodData Cloud and describe computation context
  in which the function is called

### Technical perspective

A FlexConnect function is a class that implements the `FlexConnectFunction` interface.

The concrete implementations provide:

- Name of the function
- Schema of the returned tabular data
- Implementation of `call` method to compute and return the data

FlexConnect and its functions are implemented on top of the Apache Arrow. The schema describing the tabular
data is expected to be an Apache Arrow Schema. The returned tabular data is either an Apache Arrow
Table (fully materialized data) or a RecordBatchReader (stream of data).

The FlexConnect functions are hosted within a Flight RPC server - this template conveniently wraps
everything together. The invocation and data transfer is all done using the Flight RPC.

### FlexConnect function hosting

The FlexConnect function implementations are supposed to be hosted on a Flight RPC server which is
then added as a data source to GoodData Cloud or Cloud Native: thus, the functions become
available in the semantic model and can be used in report computations.

This template project (backed by infrastructure available in GoodData Python SDK) solves and
simplifies the task of creating a production-ready Flight RPC server where the FlexConnect functions
run.

The artifact produced by the template is a Docker image containing Flight RPC server with
your functions plugged into it.

You then have to deploy and run this Docker image 'somewhere' - for example on some AWS EC2
instance and then add that location as data source to GoodData Cloud or Cloud Native.

## Getting Started

To get started with custom functions is easy. The only prerequisite is a working installation of
Python 3.12 and access to internet:

1.  Clone this template: `git clone git@github.com:gooddata/gooddata-flexconnect-template.git <your-directory>`
2.  Navigate to your directory `cd <your-directory>`
3.  Re-initialize git repository `rm -rf .git && git init && git add . && git commit -m "Initial commit"`

    It is very much intentional that after you bootstrap your own FlexConnect project using this template,
    you want to 'detach' it from the template repository and track changes independently.

4.  Bootstrap development environment `make dev`

    This will create Python Virtual Environment in `.venv` directory.

5.  [Optional] The project is set up with `.envrc` - if you use [direnv](https://direnv.net/), then do `direnv allow`

HINT: If you have trouble installing Python 3.12, we recommend using [pyenv](https://github.com/pyenv/pyenv).
First, correctly install pyenv using its installation guide. Then after step #2 above, do `pyenv install` and `pyenv local`.
Then you can continue with `make dev`

If you use PyCharm or IDEA, you can now open the project and:

1. Add existing virtual environment (bootstrapped in previous steps and available in `.venv` directory)
2. Mark `src` as sources root, mark `tests` as test sources root

## Developing FlexConnect functions

The template sets initial convention where the functions are located in [src/flexconnect](./src/flexconnect) directory. You
can find the [sample_function.py](./src/flexconnect/sample_function.py) there. The easiest way to get poking around is
to modify this function to do your bidding.

### Adding new function

#### Adding the code

The only requirement is that your new FlexConnect function must be a file inside the `src` directory and within that you
need to have a class implementing the `FlexConnectFunction` interface. See the [sample_function.py](./src/flexconnect/sample_function.py)
for inspiration.

How your organize the implementations is completely up to you:

- If you have many small functions, then it may be enough to create file-per-function inside the
  existing `src/flexconnect` directory.

- If, however, you expect that the implementation of the function may grow large and be split into
  multiple smaller files, then we recommend that you create a new Python package somewhere under `src`
  directory.

  For example, you can go with layout such as:

  - src/flexconnect/function_name1/
    - api.py < this is where you have class implementing the FlexConnectFunction interface
    - any other files and sub-packages that the `api.py` depends on

  This way, each possibly complex function is separated in its own package, there is a well-defined
  entry point (the `api.py`) and then bunch of other files needed for the implementation - as you see fit.

IMPORTANT: if you create your own packages and sub-packages, make sure to include the `__init__.py` files -
otherwise you run risk of Import/ModuleLoad errors.

#### Registering the function

In order for the function to be loaded and exposed via Flight RPC, you need to register it to
the server. This is purely a configuration step:

- Open the [config/flexconnect.config.toml](./config/flexconnect.config.toml) configuration file
- Within that file, there is a `functions` setting. This is a list of Python modules that are expected
  to contain the `FlexConnectFunction` implementations.

  You add name of Python module that contains the function implementation. You code this the same way as
  when doing imports in Python.

  For example if you build your function in `src/flexconnect/function_name1/api.py`, then you need to
  register `flexconnect.function_name1.api`.

HINT: you can have multiple FlexConnectFunction implementations within a single Python source file. All those
implementations will be discovered and registered. This is fine to do if you have many small, trivial
functions. However, as the functions grow in complexity, the single file may grow too big and harder
to manage code-wise.

#### Recommendations

Your concrete FlexConnect function implementation is integrated into GoodData Flight server which handles
all the technicalities and boilerplate related to server operations and function invocations.

For every invocation of the function via the Flight RPC, the server will create a new instance
of your class. It is strongly recommended that this is as fast as possible and does not perform
any expensive initialization.

**HINT**: expensive one-time initialization can be done by overloading `on_load` method.

The server comes with built-in call queuing and separate thread pool that services the
invocations. See server configuration and the comments in it to find out more.

**IMPORTANT**: Your code must not make any assumptions that a thread that creates instance of
your function will be the same thread that invokes the `call`.

### Adding third party dependencies

If your function implementation requires some 3rd party libraries, you should add them to the
[requirements.txt](./requirements.txt) file. After you add the dependency, re-run `make dev`.

This will modify existing `.venv` and reinstall the dependencies. Usually, you do not have to
remove the existing `.venv`.

However, especially when adding more dependencies, removing dependencies or running into issues, we
recommend to re-bootstrap the environment: `rm -rf .venv && make dev`.

### Logging

This template comes with the `structlog` dependency installed by default. The `structlog` is used
and configured so that it uses Python stdlib logging backend. The `structlog` pipeline is set up so
that:

- In dev mode, the logs are pretty-printed into console (achieved by `--dev-log` option of the server)
- In production deployment, the logs are serialized into JSON (using orjson) which is then written out.
  This is ideal for consumption in log aggregators.

The stdlib loggers are configured using the [config/default.logging.ini](config/default.logging.ini)
file. In the default setup, all INFO-level logs are emitted. You can tweak the config file as you see
fit - see Python logging documentation to learn more. This document will not go into those details.

NOTE: you typically do not want to touch the formatter settings inside the logging ini file - the
`structlog` library creates the entire log lines accordingly to deployment mode.

The use of `structlog` and loggers is fairly straightforward:

```python
import structlog

_LOGGER = structlog.get_logger("sample_flex_function")
_LOGGER.info("event-name", some_event_key="value_to_log")
```

#### Recommendations

Here are few assorted recommendations based on our production experience with `structlog`:

- You can log complex objects such as lists, tuples, dicts and data classes no problem
  - Be conservative though. What can be serialized into dev-log may not always serialize
    using `orjson` into production logs
- Always log exceptions using the special [exc_info](https://www.structlog.org/en/stable/exceptions.html) event key.
- Mind the cardinality of the logger instances. If you have a class of which you may have thousands of
  instances, then it is **not a good idea** to create a logger instance for each instance of your class - even
  if the logger name is the same; this is because each logger instance comes with memory overhead.

### Prometheus Metrics

GoodData's Flight RPC server can be configured to start HTTP endpoint that exposes values of Prometheus
metrics. This is disabled by default.

To get started with Prometheus metrics you need to:

- Set `metrics_host` and `metrics_port`

  - Check out the config file comments to learn more about these settings.
  - What you have to remember is that the Prometheus scraper is an external process that
    needs to reach the HTTP endpoint via network.

- Install `prometheus_client`

  - Uncomment the `prometheus_client` line [requirements.txt](requirements.txt) and run `make dev`
  - Note: as is, the `gooddata-flight-server` already installs this package so the `make dev` step above
    will actually not install anything new. However, this may change in the future; not to mention that
    it is generally not a good idea to rely on transitive dependencies.

From then on, you can start using the Prometheus client to create various types of metrics. For example:

```python
from prometheus_client import Counter

# instantiate counter
MY_COUNTER = Counter(
    "my_counter",
    "Fitting description of `my_counter`.",
)

def some_function():
    # ...
    MY_COUNTER.inc()
```

#### Recommendations

Here are a few assorted recommendations based on our production experience:

- You must avoid double-declaration of metrics. If you try to define metric with same
  identifier twice, the registration will fail.

- It is nice to declare all/most metrics in single place. For example create `my_metrics.py`
  file and in that have `MyMetrics` class with one static field per metric.

  This approach leads to better 'discoverability' of available metrics just by looking
  at code. Using class with static field per-metric in turn makes imports and autocomplete
  more convenient.


### OpenTelemetry Tracing

GoodData's Flight RPC server can be configured to integrate with OpenTelemetry and start
and auto-configure OpenTelemetry exporters. It will also auto-fill the ResourceAttributes
by doing discovery where possible.

See the `otel_*` options in the configuration files to learn more. In a nutshell it
goes as follows:

- Configure which exporter to use using `otel_exporter_type` setting.

  Nowadays, the `otlp-grpc` or `otlp-http` is the usual choice.

  Depending on the exporter you use, you may/must specify additional, exporter-specific
  environment variables to configure the exporter. The supported environment variables
  are documented in the respective OpenTelemetry exporter package; e.g. they are not
  something special to GoodData's Flight Server.

  See [official exporter documentation](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#module-opentelemetry.exporter.otlp.proto.grpc).

- Install `opentelemetry-api` and the respective exporter package.

  See the [requirements.txt](requirements.txt). The packages are already listed there but
  are commented out. Once you uncomment them, do `make dev` to ensure they are installed.

- Tweak the other `otel_*` settings: you must at minimum set the `otel_service_name`

  The settings apart from `otel_service_name` will fall back to defaults.

To start tracing, you need to initialize a tracer. You can do so as follows:

```python
from opentelemetry import trace

MY_TRACER: trace.Tracer = trace.ProxyTracer("my_tracer")
```

Typically, you want to create one instance of tracer for your entire project and then import
that instance and use it wherever needed to create spans:

```python
from your_module_with_tracer import MY_TRACER

def some_function():
    # ... code
    with MY_TRACER.start_as_current_span("do_some_work") as span:
        # ... code
        pass
```

Note: there are many ways to instrument your code with spans. See [OpenTelemetry documentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
to find out more.

#### Recommendations

Here are a few assorted recommendations based on our production experience:

- Always use the `ProxyTracer`. The underlying initialization code in GoodData's Flight server
  will correctly set the actual tracer which the proxy will call.

  This way, if you turn off OpenTelemetry (by commenting out the `otel_export_type` setting or setting it
  to 'none'), the NoOpTracer will be injected under the covers and all the tracing code will
  be no-op as well.

- Do not skim on the contextual detail / essential info for troubleshooting:

  - Add span attributes to provide additional contextual information.
  - Log events and errors to span to propagate significant return values / errors

With tracing, it is always a dance between adding too much information (and thus possibly overwhelming
your underlying tracing infrastructure) vs only having basic span information which is useful to
identify control flow but does not provide necessary detail to help debugging problems.

### Health Checks

The GoodData Flight Server comes with a basic health-checking infrastructure - this is especially useful
when deploying to environments (such as k8s) that monitor health of your server and can automatically
restart it in case of problems.

When you configure the `health_check_host` (and optionally also `health_check_port`) setting, the Flight
Server will expose two HTTP endpoints:

- `/ready` - indicates whether the server is up and ready to serve requests

  The endpoint will respond with status `500` if the server is not ready. Otherwise, it will respond with
  `202`. The server is deemed ready when all its modules (which includes your FlexConnect functions) are
  up and the Flight RPC server is 'unlocked' to handle requests.

- `/live` - indicates whether the server is still alive and can be used. The liveness is determined
  from the status of the modules.

  Each of the server's modules can report its status to a central health checking service. If any of
  the modules is unhealthy, the whole server is unhealthy.

  Similar to the readiness, the server will respond with status `500` when not healthy. Otherwise, it
  will respond with status `202`.

Creating health-checks for your FlexConnect functions is fairly straightforward:

- There is the `on_load()` static method that you can implement on your function's class; it receives an
  instance of `ServerContext`

  - The `ServerContext` contains `health` property - which returns an instance of `ServerHealthMonitor`

  - At this occasion, your code should hold onto / propagate the health monitor to any mission-critical
    modules / components that are used by your function

- The `ServerHealthMonitor` has `set_module_status(module, status)` method - you can use this to indicate status

  - The module `name` argument to this method can be anything you see fit
  - The status is either `ModuleHealthStatus.OK` or `ModuleHealthStatus.NOT_OK`
  - When your module is `NOT_OK`, the entire server is `NOT_OK`
  - Usually, there is a grace period for which the server can be `NOT_OK`; after the time is up,
    environment will restart the server
  - If you return your module back to `OK` status, the server returns to `OK` status as well - thus
    avoiding the automatic restarts.

Here is an example component using health monitoring:

```python
import gooddata_flight_server as gf

class YourMissionCriticalComponent:
    """
    Let's say this component is used from your function to perform
    some heavy lifting / important job.

    The component is created / initialized during `on_load` of function and you
    propagate the `health` monitor that comes in the server context.
    """
    def __init__(self, health: gf.ServerHealthMonitor) -> None:
        self._health = health

    def some_important_method(self):
        try:
            # this does some important work
            return
        except OSError:
            # it runs into some kind of unrecoverable error (OSError here is purely example);
            # by setting the status to NOT_OK, your component indicates that it is unhealthy
            # and the /live endpoint will report the entire server as unhealthy.
            #
            # usually, the liveness checks have a grace period. if you set the module back
            # to `gf.ModuleHealthStatus.NOT_OK` everything turns healthy again. If the grace
            # period elapses, the server will usually be restarted by the environment.
            self._health.set_module_status("YourMissionCriticalComponent", gf.ModuleHealthStatus.NOT_OK)
            raise
```

### Dev-testing

A FlexConnect function is a piece of code like any other. The fact that it is exposed via Flight RPC
is a technical detail.

This template project comes with `pytest` pre-installed. You can test your function
implementations as you see fit using the standard techniques. You can run the tests either
from IDE or use the `make test` target.

Typically, if your function does not do any crazy / non-standard stuff, then there is a very
solid guarantee that a function passing tests will run fine once it is running inside the
Flight RPC server.

Additionally, the template comes with fixtures for automated end-to-end testing. See the
[test_e2e.py](tests/flexconnect/test_e2e.py). In a nutshell, the `testing_flexconnect_server` fixture
will start a server running your functions; you can then make calls to the server using
the standard FlightClient.

**HINT**: if you need additional third-party dependencies for dev/test, then add those to
the [requirements-dev.txt](./requirements-dev.txt).

### Template dev infrastructure

This project is set up with:

- [ruff](https://github.com/astral-sh/ruff) for linting, formating, import sorting
- [mypy](https://github.com/python/mypy) for type checking
- [pre-commit](https://github.com/pre-commit/pre-commit) hooks

The pre-commit hooks are enabled by default and run `ruff` and other basic hooks.
The use of `mypy` is optional - but we strongly encourage it especially if your functions
grow large.

There are a few Makefile targets for the usual tasks:

- `make mypy` - run type checker
- `make fix-format` - run ruff format and ruff check in auto-fix mode on all files
- `make fix-all` - runs configured pre-commit hooks on all files in the repository.
  Note: `ruff` format and check with auto-fix is part of the pre-commit.

**IMPORTANT**: Keep in mind that pre-commit will not auto-stage files that were modified
while it is running the configured hooks. What this means is that commit will fail if
the `pre-commit` hooks get involved and auto-fix the files. You typically then have to
re-drive the commit.

#### Secrets for dev and dev testing

During the bootstrap, the `make dev` will create `.secrets` file. This file is included in .gitignore
and will not be committed to git. It is intended to hold any env variables that contain secrets.

If you use `direnv`, then the contents of this file will be automatically sourced when you navigate to
the directory. Otherwise, you may want to source the file manually (or finally get around and install
direnv).

As the name indicates, the `.secrets` file is useful for holding any sensitive information:

- GDCN_LICENSE_KEY - the license key to use if you are doing end-to-end testing using docker-compose
  (see below)

- GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS - can be used to specify list of secret tokens
  used for authentication.

  This one is a bit tricky, you have to specify an array of tokens: `'["...", "..."]'`

## Running and testing locally using Docker Compose

The template comes with `docker-compose.yaml` which consists of two services:

1.  The GoodData Cloud Native Container Edition (gooddata-cn-ce). This runs the entire Cloud Native
    in a single container.

2.  The server hosting your FlexConnect functions (gooddata-flexconnect-server)

To start it all up, you do the usual: `docker compose up -d --build`. At the time of startup, the
Docker image with server hosting your functions will be built (see section above).

Right now, you have to add your server as a data source to GoodData CN manually. Do POST the following
payload to http://localhost:3000/api/v1/entities/dataSources:

```bash
curl http://localhost:3000/api/v1/entities/dataSources \
-H "Authorization: Bearer YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz" \
-s -H "Content-Type: application/vnd.gooddata.api+json" \
-X POST \
-d '{
  "data": {
    "id": "flexconnect-server",
    "type": "dataSource",
    "attributes": {
      "url": "grpc://gooddata-flexconnect-server:17001",
      "name": "flexconnect-server",
      "type": "FLIGHTRPC",
      "token": "none",
      "schema": "",
      "cacheStrategy": "NEVER"
    }
  }
}'
```

If you make some changes and want to rebuild & restart just the server
run: `docker compose up -d --build gooddata-flexconnect-server`.

Rebuild and restart of your server is usually very quick so this should allow you to iterate
very fast. Still, even faster and more natural is to use the typical tests that you
can write in `tests` directory.

We recommend doing most of the testing using programmatic tests and then use the end-to-end
testing using docker compose for final verification.

## Getting ready for deployment

### Configuration

The underlying server infrastructure uses [Dynaconf](https://www.dynaconf.com/) to manage
configuration. This template comes with two configuration files:

- [dev.server.toml](./config/dev.server.toml) is tailored for dev-testing on localhost
- [prod.server.toml](./config/prod.server.toml) is a stub of configuration for production
  server deployment.

The 'prod' configuration file is preset to listen on all addresses, use TLS and token authentication.
But it naturally omits configuration of TLS (certificate, private key) and the details of
token authentication. You have to supply those or (and we do not recommend this) turn them off.

**IMPORTANT**: depending on your production host, you may further tweak the configuration - especially
the `advertise_host`. Check out the following sections to learn more.

#### Environment Variables

You can use environment variables to override any setting from the configuration
files.

This is typically useful when handling secrets: you don't want to hammer those into the
configuration files that make it to a VCS. Instead, the values of secrets are injected at runtime
using environment variables.

For list of environment variables, see for example the `run-server.sh`. The environment
variables are derived from setting names:

- Always start with `GOODDATA_FLIGHT`
- The section name (e.g. `[server]`) comes next, so for example `GOODDATA_FLIGHT_SERVER`
- Then comes the setting name itself (e.g. `listen_host`), separated with two underscores;
  so you end up with `GOODDATA_FLIGHT_SERVER__LISTEN_HOST`

  All settings that can be specified in the TOML file can be also set via environment
  variable. The value from environment variable always wins.

Furthermore, we recommend checking the Dynaconf documentation - it has a lot of additional
features which you can take advantage of. It even has its own templating.

### Setting up hostnames

This part can get somewhat tricky if you do not read the documentation. We recommend to
check out the comments in the `prod.server.toml`.

For production, go as follows:

- Set `listen_host` to `0.0.0.0`
- Set `advertise_host` to either public IP or public hostname of your server.

  Essentially, this is the value that you would also use when adding the server
  as data source to the GoodData Cloud.

NOTE: Setting correct `advertise_host` is critical because the primary flow to
invoke functions is the GetFlightInfo -> DoGet flow. Where GetFlightInfo call returns
information where and how to consume the function result. The server infrastructure
needs your input (e.g. the `advertise_host`) so that it can fill the 'where' part.

### Authentication

At the moment, the server infrastructure supports two authentication methods:

- No authentication at all (this is default that the template starts with)
- Token based authentication, where the client has to present a secret token

For deployment where your server is reachable from the public networks, you almost
always want to set up authentication.

1. Set the `authentication_method` option to `token`

   Alternatively, you can use the `GOODDATA_FLIGHT_SERVER__AUTHENTICATION_METHOD`
   environment variable.

2. Define the secret tokens. This is done either using configuration or
   environment variable.

   ```toml
   [enumerated_tokens]
   tokens = []
   ```

   The `tokens` setting should contain one or more tokens. These are really some values
   that you keep secret and distribute them to clients. They can be whatever you see fit.

   The same can be achieved using the `GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS`. The
   value of this environment variable has to be coded as an array:

   `GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS='["...", "..."]'`

**IMPORTANT**: Never commit the secrets to VCS. Keep the secret token configuration
outside of this project.

### TLS

Using TLS (Transport Level Security) is highly recommended. To do so, you have to
obtain certificate and private key for your server - a topic that is not covered
in this manual.

When you have private key and the certificate (typically in `.pem` files), you can
configure these server settings (server.config.toml):

- `use_tls = true` to enable TLS
- `tls_certificate` - configure server's certificate
- `tls_private_key` - configure server's private key

For further information, see the comments for these settings in the
[prod.server.toml](./config/prod.server.toml) file.

**IMPORTANT**: you can opt to generate and self-sign the server certificate. It is
a viable option. If you do that, you **must** distribute the CA certificate the clients. So
for example you have to configure the data source in GoodData so that it includes the
CA certificate (this is covered in followup sections.)

**IMPORTANT**: do not commit server certificate and private key to VCS. Keep them outside
of this project (e.g. only keep them on / distribute them to the host where your server runs).

### Deployment without Docker

Deploying and running your server without use of Docker is a viable approach and in
many cases can be the simplest or most straightforward.

1. You have to get the whole template project to a host

   - You can do this by creating tarball of essential content using `make archive`
   - Then get the tarball to the host using your favorite method and extract it there

   HINT: Another approach is to have a git repository where you push and manage the
   contents of this project. Then check out the contents of this repository from the
   host.

2. Install production dependencies:

   - Your host must have Python 3.12 installed
   - On the host, run `make prod` - this will install production dependencies into
     its own virtual environment.

3. Start the server

  - Easiest is to use `./run-server.sh prod`
  - This will start server using the [prod.server.toml](./config/prod.server.toml) configuration
    stored in `config` directory
  - Typically, you will need to specify host-specific settings, you can do
    so using environment variables or further tweak the configuration.
  - If you have not already, see the 'Configuration' section above for additional
    detail.

### Dockerized deployment

This template comes with a [Dockerfile](./Dockerfile) and an [example script](./run-docker.sh) to
start the dockerized server hosting your FlexConnect functions.

As everything in the template, both the Dockerfile and the example are just one way to
proceed with Dockerized deployment; they are yours to change or even throw away and do
them your way from scratch to suit your deployment. You may be using Docker Swarm, Nomad,
k8s or some managed service - naturally, the example script is of little use in such contexts.

#### Docker Image

The `make docker` target is available and builds Docker image `flexconnect-server`. You may want
to modify the image name and specify your own custom one.

The Docker image build will:

- Install all dependencies from `requirements.txt` file

  IMPORTANT: dependencies from requirements-dev.txt are intentionally not installed.

- Copy content of the entire `src` folder and make sure it is added on PYTHONPATH

  IMPORTANT: contents of `tests` directory is not copied to the image.

- Copy content of the entire `config` folder

#### Important considerations when running in Docker

The most important aspect to re-iterate here is the setup of `listen_host` and `advertise_host`:


- You most often want to set `listen_host` to `0.0.0.0` so that the server listens
  on all addresses _inside_ the Docker container.

- The `advertise_host` must be then set to a host name that can be correctly resolved
  by your server's clients; this is usually different from any hostname that
  is set _inside_ the Docker container. In most cases, you _have_ to provide the hostname
  from outside.

### Multiple server replicas and load balancing

To foster resiliency and horizontal scalability, you can have multiple replicas of the server
running your FlexConnect functions. You can register all these replicas to the Flight RPC data source
and then set the load balancing strategy. Check out the following section to find an example.

It is critical to remember, that any **infrastructure-level load balancing will most likely
break things**. That is because the FlexConnect servers are **stateful**:

- FlexConnect function invocation happens in two steps.
- In the first step, the Flight RPC GetFlightInfo is called (as per spec) to tell
  the server to invoke the function and prepare the data. A response to GetFlightInfo contains,
  among other things, the `advertise_host` location of the server where to pick up the result.
- In the second step, the Flight RPC DoGet is called to actually pick up the data from the
  advertised location returned in the previous step.

Now, if you have a setup (common in k8s with gRPC load balancing) where there is a single hostname that
transparently balances to multiple replicas, things **will** break. The GetFlightInfo request lands
on one replica, computes results and returns pointers to access that result. The subsequent DoGet call
may however, be routed to completely different replica where the result is not present.

## Adding Data Source to GoodData Cloud

Now that you have the Flight RPC server with your FlexConnect functions up and running, you can
add it as data source to GoodData.

At the moment, this is only possible using the REST API.

You need to do a POST request on the `/api/v1/entities/dataSources` resource. The payload
should look like this:

```bash
curl https://<gooddatacloud>/api/v1/entities/dataSources \
-H "Authorization: Bearer <gooddata-token>" \
-s -H "Content-Type: application/vnd.gooddata.api+json" \
-X POST \
-d '{
  "data": {
    "id": "flexconnect-server",
    "type": "dataSource",
    "attributes": {
      "url": "grpc+tls://<your-hostname>:<port>",
      "name": "flexconnect-server",
      "type": "FLEXCONNECT",
      "token": "<secret authentication token for the Flight RPC server>",
      "schema": "",
      "cacheStrategy": "NEVER"
    }
  }
}'
```

### TLS and custom certificate

If your server has TLS enabled and uses self-signed certificates, then you also have to
provide this certificate as a parameter of the data source:

```bash
curl https://<gooddatacloud>/api/v1/entities/dataSources \
-H "Authorization: Bearer <gooddata-token>" \
-s -H "Content-Type: application/vnd.gooddata.api+json" \
-X POST \
-d '{
  "data": {
    "id": "flexconnect-server",
    "type": "dataSource",
    "attributes": {
      "url": "grpc+tls://<your-hostname>:<port>",
      "name": "flexconnect-server",
      "type": "FLEXCONNECT",
      "token": "<secret authentication token for the Flight RPC server>",
      "schema": "",
      "cacheStrategy": "NEVER",
      "parameters": [
        {
          "name": "tlsRootCertificate",
          "value": "..."
        }
      ]
    }
  }
}'
```

The `value` of the `tlsRootCertificate` is Base64 encoded content of the CA certificate .pem file. You can
do the base64 encoding for example using something like this:

```python
import base64

with open("ca-cert.pem", "rb") as file:
    print(base64.b64encode(file.read()))
```

### Load Balancing

If you have multiple replicas of the FlexConnect servers running your functions,
you can code them in the `url`, delimited using semicolon.

You can then specify the `loadBalancing` parameter to so the load balancing strategy to use:

- `none` - there will be no load balancing; the first server from the list will be used all the time; when the
  server is down, GoodData will contact next server in the list. This is the default.

- `round-robin` - requests will be distributed among servers using round-robin strategy.

- `random` - requests will be distributed among servers randomly

```bash
curl https://<gooddatacloud>/api/v1/entities/dataSources \
-H "Authorization: Bearer <gooddata-token>" \
-s -H "Content-Type: application/vnd.gooddata.api+json" \
-X POST \
-d '{
  "data": {
    "id": "flexconnect-server",
    "type": "dataSource",
    "attributes": {
      "url": "grpc+tls://<your-hostname1>:<port>;grpc+tls://<your-hostname2>:<port>",
      "name": "flexconnect-server",
      "type": "FLEXCONNECT",
      "token": "<secret authentication token for the Flight RPC server>",
      "schema": "",
      "cacheStrategy": "NEVER",
      "parameters": [
        {
          "name": "loadBalancing",
          "value": "round-robin"
        }
      ]
    }
  }
}'
```

### Cache strategy

The `cacheStrategy` set to 'NEVER' means that GoodData Cloud will never cache any
results obtained when invoking FlexConnect functions on your server.

You can set this to `ALWAYS` if you want to add caching layer on top of your server - just
keep in mind that then you have to do POST on `/api/v1/actions/dataSources/my-flexconnect/uploadNotification`
every time you want to invalidate the caches.

The use of caching on top of server running functions is at your discretion - in many
cases it depends on what your functions do. For example if the function does complex
computations on top of mostly static data - then using the caching is a no-brainer especially
in production deployments.
