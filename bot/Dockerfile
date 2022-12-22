FROM python:3.10.5

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt /bot/

RUN pip install -r /bot/requirements.txt

COPY bot/ /bot/

WORKDIR /bot

#RUN chmod 400 SSL/webhook_pkey.pem && \
#    chmod 400 SSL/webhook_cert.pem

EXPOSE 3333

CMD ["/usr/local/bin/python", "bot.py"]
