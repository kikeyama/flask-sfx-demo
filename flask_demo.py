from flask import Flask
from flask import request as flask_request
#import logging
import sys
import blinker as _
import time

import pymysql.cursors
import json
import requests

from logging.config import dictConfig

# DB Config
import env_config

## Have flask use stdout as the logger
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '- %(message)s')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': FORMAT,
    }},
    'handlers': {'console': {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'default',
        'stream': 'ext://sys.stdout'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})

## Connecting MySQL
connection = pymysql.connect(
    host=env_config.db_host,
    user=env_config.db_username,
    password=env_config.db_password,
    db=env_config.db_name,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
## Flask
app = Flask(__name__)

@app.route('/')
def api_entry():
    start_time = time.time()

    app.logger.info('getting entity from table')
    name = flask_request.args.get('name', str)

    with connection.cursor() as cursor:
        sql = "SELECT Name, UUID, Number FROM kikeyama_table where name='%s'" % name
        cursor.execute(sql)
        result = cursor.fetchone()
        
        return result

@app.route('/api/apm')
def apm_endpoint():
    app.logger.info('getting apm endpoint')
    return 'Getting APM Started'

@app.route('/api/trace')
def trace_endpoint():
    app.logger.info('getting trace endpoint')
    return 'Posting Traces'

@app.route('/api/post', methods=['POST'])
def post_endpoint():
    app.logger.info('posting message: ' + flask_request.form['message'])
    return flask_request.form['message']

@app.route('/api/lambda')
def lambda_endpoint():
    app.logger.info('getting lambda endpoint')
    fqdn = env_config.api_fqdn
    q = {'TableName': 'kikeyama-dynamodb'}
#    r = requests.get('https://%s/demo/python' %fqdn, params=q)
#    dict_r = json.loads(r.text)
#    if dict_r['ResponseMetadata']['HTTPStatusCode'] == 200:
#        app.logger.info('lambda call: Returned ' + str(dict_r['Count']) + ' results with RequestId: ' + dict_r['ResponseMetadata']['RequestId'])
#    return 'Lambda Traces'

    ## For API Gateway without Proxy Integraion testing
    r = requests.get('https://%s/demo/non-proxy-integration' %fqdn, params=q)
    dict_r = json.loads(r.text)
    if dict_r['statusCode'] == 200:
        app.logger.info('SUCCESS')
    return 'Lambda Traces'
    ##

@app.route('/api/lambda/jaeger')
def lambda_jaeger_endpoint():
    app.logger.info('getting lambda jaeger demo endpoint')
    fqdn = env_config.api_fqdn
    r = requests.get('https://%s/demo/jaeger-sample' %fqdn)
    dict_r = json.loads(r.text)
    app.logger.info('lambda call: Result: ' + dict_r['result'] + ' | Trace ID: ' + dict_r['trace_id'])
    return 'Lambda Jaeger Traces'


if __name__ == '__main__':
    app.logger.info('%(message)s This is __main__ log')
    try:
        app.run(host='0.0.0.0', port='5050')
    finally:
        connection.close()
