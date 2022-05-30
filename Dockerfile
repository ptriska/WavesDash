FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install python3.6
RUN apt-get -y install python3-pip
RUN apt-get -y install git
RUN pip3 install dash
RUN pip3 install dash_auth
RUN pip3 install "dash-bootstrap-components<1"
RUN pip3 install dash_core_components
RUN pip3 install dash_html_components
RUN pip3 install dash_table
RUN pip3 install pandas
RUN pip3 install plotly
RUN pip3 install dash_trich_components
RUN pip3 install datetime
RUN pip3 install python-dateutil
RUN pip3 install python-time
RUN pip3 install pip --upgrade
RUN pip3 install datatable
