FROM python:3.6
MAINTAINER mpxc
RUN pip install bs4
RUN pip install requests
COPY websites.py /
CMD python /websites.py
