FROM python:3.11.0

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY . .

RUN pip3 install --upgrade pip setuptools

RUN pip install -U -r requirements.txt
RUN chmod +x start.sh
CMD ["bash","start.sh"]
