# start with a python3 base container
FROM python:3
MAINTAINER Andreas Bauer <andreaslbauer@gmail.com>

# add python files
ADD networkscan.py /

# install required python packages
RUN pip3 install requests paramiko

# make port 5000 publically available
EXPOSE 5000

# run the app
CMD [ "python3", "./networkscan.py" ]
