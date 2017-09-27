FROM google/cloud-sdk
MAINTAINER mabl <developers@mabl.com>

USER root

# Set timezone
RUN echo "UTC" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# Fix known apt TLS bug
RUN apt-get update -qqy \
  && apt-get -qqy install apt-transport-https \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN apt-get update -qqy \
  && apt-get -qqy install python-pip libgdal-dev \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN apt-get update -qqy \
  && apt-get -qqy install git \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN mkdir /tmp/raw_data_in/ /tmp/raw_data_out/
RUN git clone https://github.com/mapbox/rio-cloudmask.git

COPY docker/firebase-service-account.json .
COPY docker/requirements.txt .

RUN pip install -r requirements.txt
RUN pip install -r rio-cloudmask/requirements.txt

COPY sat_cruncher.py .

#file permissions                                                          │
RUN chmod -R +x sat_cruncher.py \
  && chmod +x sat_cruncher.py
  
ENV PYTHONPATH=/rio-cloudmask

# TODO create test user - not root

ENTRYPOINT ["./sat_cruncher.py"]
