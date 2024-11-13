FROM python:3.12-slim-bookworm
ARG FLEXCONNECT_USER="flexconnect"
ARG FLEXCONNECT_GROUP="flexconnect"

COPY /requirements.txt /

RUN apt-get update \
    && apt-get -y install --no-install-recommends curl \
    && pip3 install --upgrade pip \
    && pip3 install -r /requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /build /root/.cache/pip

RUN set -x \
  # Create user and group in OS
  && /usr/sbin/groupadd -r -g 1000 $FLEXCONNECT_USER \
  && /usr/sbin/useradd -r -u 1000 -m -s /bin/bash -g $FLEXCONNECT_GROUP $FLEXCONNECT_USER \
  && mkdir -p /data \
  && chown -R 1000:1000 /data \
  && mkdir -p /src \
  && chown -R 1000:1000 /src \
  && mkdir -p /config \
  && chown -R 1000:1000 /config

# Copy all configs
COPY /config /config

# Copy all source code and add it to PYTHONPATH
COPY /src /src
ENV PYTHONPATH="/src"

# BEGIN OF security hardening
RUN /usr/bin/rm -rf /etc/crontab /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly ; \
    /usr/bin/sed -i '/^CREATE_HOME/ s/^CREATE_HOME.*/CREATE_HOME yes/; t; $ aCREATE_HOME yes' /etc/login.defs
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# END OF security hardening

USER $FLEXCONNECT_USER

ENTRYPOINT ["gooddata-flight-server"]

EXPOSE 17001
EXPOSE 17101
