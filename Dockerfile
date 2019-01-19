FROM python:3
ADD networkscan.py /
RUN pip3 install requests paramiko
CMD [ "python3", "./networkscan.py" ]
