FROM python:3.8
ADD flask_demo.py /
ADD env_config.py /
ADD requirements.txt /
# ENV DB_HOST <DB_HOST>
# ENV DB_USERNAME <DB_USERNAME>
# ENV DB_PASSWORD <DB_PASSWORD>
# ENV DB_NAME <DB_NAME>
# ENV API_FQDN <API_FQDN>
# ENV API_FQDN <API_GATEWAY_STAGE_FQDN>
# ENV SIGNALFX_SERVICE_NAME kikeyama_flask_demo
# ENV SIGNALFX_ENDPOINT_URL http://${SIGNALFX_AGENT_HOST}:9080/v1/trace
# ENV SIGNALFX_ACCESS_TOKEN <ACCESS_TOKEN>
RUN pip install -r requirements.txt
RUN sfx-py-trace-bootstrap
#CMD [ "python", "./flask_demo.py" ]
CMD [ "sfx-py-trace", "./flask_demo.py" ]
