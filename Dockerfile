FROM centos:latest

MAINTAINER yunwei <yunwei@ruitone.com.cn>

RUN echo 'Asia/Shanghai > /etc/timezone'
RUN yum install which python3 python3-pip -yq
RUN which python3|xargs -i ln -s {} /usr/bin/python
RUN which pip3|xargs -i ln -s {} /usr/bin/pip
RUN mkdir /root/.pip
COPY . /home/python
COPY pip.conf /root/.pip/pip.conf
WORKDIR /home/python
RUN pip install -r requirements.txt
CMD ["python", "fadan_api.py"]