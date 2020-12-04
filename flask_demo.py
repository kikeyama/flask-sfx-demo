from flask import Flask
from flask import request as flask_request
#import logging
import sys
import blinker as _
import time

import pymysql.cursors
from pymysqlpool.pool import Pool
import json
import requests

from logging.config import dictConfig
import logging

# DB Config
import env_config

## Have flask use stdout as the logger
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
        '[signalfx.trace_id=%(sfxTraceId)s signalfx.span_id=%(sfxSpanId)s] '
        '- %(message)s')

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': FORMAT,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
})

def connect_mysql():
    # Connecting MySQL with connection pool
    pool = Pool(host=env_config.db_host, 
        port=int(env_config.db_port), 
        user=env_config.db_username, 
        password=env_config.db_password, 
        db=env_config.db_name)
    pool.init()
    global connection
    connection = pool.get_conn()

#connection = pymysql.connect(
#    host=env_config.db_host,
#    user=env_config.db_username,
#    password=env_config.db_password,
#    db=env_config.db_name,
#    charset='utf8mb4',
#    cursorclass=pymysql.cursors.DictCursor
#)

## Flask
app = Flask(__name__)

## Flask-pymysql (https://github.com/rcbensley/flask-pymysql)
#pymysql_connect_kwargs = {
#    'host': env_config.db_host,
#    'port': int(env_config.db_port),
#    'user': env_config.db_username,
#    'password': env_config.db_password,
#    'db': env_config.db_name
#}
#app.config['pymysql_kwargs'] = pymysql_connect_kwargs
#mysql = MySQL(app)


@app.route('/')
def api_entry():
    start_time = time.time()

    app.logger.info('getting entity from table')
    name = flask_request.args.get('name', str)

#    # Flasy-pymysql
#    cur = mysql.connection.cursor()
#    cur.execute('''SELECT Name, UUID, Number FROM kikeyama_table WHERE Name='%s' ''' % name)

    if connection is None:
        connect_mysql()

    connection.ping(reconnect=True)

    with connection.cursor() as cursor:
        sql = "SELECT Name, UUID, Number FROM kikeyama_table where name='%s'" % name
        cursor.execute(sql)
        result = cursor.fetchone()
        
        return result

@app.route('/healthz')
def healthz_endpoint():
    app.logger.info('getting healthz endpoint')
    return json.dumps({'status':'ok'}), 200, {'Content-Type': 'application/json'}

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
    app.logger.info('posting post endpoint')
    app.logger.info('posting message: ' + flask_request.json['message'])
    return flask_request.json['message']

## /api/lambda?type=proxy|non-proxy
@app.route('/api/lambda')
def lambda_endpoint():
    app.logger.info('getting lambda endpoint')
    apigw_fqdn = env_config.apigw_fqdn
    lambda_q = {'TableName': 'kikeyama-dynamodb'}
    api_type = flask_request.args.get('type', str)
    lambda_response = ''
    if api_type == 'proxy':
        r = requests.get('https://%s/demo/proxy-integration' %apigw_fqdn, params=lambda_q)
        dict_r = json.loads(r.text)
        if dict_r['ResponseMetadata']['HTTPStatusCode'] == 200:
            lambda_response = dict_r
            app.logger.info('SUCCESS')
    elif api_type == 'non-proxy':
        r = requests.get('https://%s/demo/non-proxy-integration' %apigw_fqdn, params=lambda_q)
        dict_r = json.loads(r.text)
        if dict_r['statusCode'] == '200':
            lambda_response = dict_r['body']
            app.logger.info('SUCCESS')
    else:
        r = requests.get('https://%s/demo/python' %apigw_fqdn, params=lambda_q)
        # Return Error intentionally
        raise Exception
#    r = requests.get('https://%s/demo/python' %apigw_fqdn, params=lambda_q)
#    dict_r = json.loads(r.text)
#    if dict_r['ResponseMetadata']['HTTPStatusCode'] == 200:
#        app.logger.info('lambda call: Returned ' + str(dict_r['Count']) + ' results with RequestId: ' + dict_r['ResponseMetadata']['RequestId'])
#    return 'Lambda Traces'

    ## For API Gateway without Proxy Integraion testing
#    r = requests.get('https://%s/demo/non-proxy-integration' %apigw_fqdn, params=lambda_q)
#    dict_r = json.loads(r.text)
#    if dict_r['statusCode'] == 200:
#        app.logger.info('SUCCESS')
#    return dict_r['body']
#    return 'Lambda Traces'
    ##
    return lambda_response

@app.route('/api/lambda/jaeger')
def lambda_jaeger_endpoint():
    app.logger.info('getting lambda jaeger demo endpoint')
    apigw_fqdn = env_config.apigw_fqdn
    r = requests.get('https://%s/demo/jaeger-sample' %apigw_fqdn)
    dict_r = json.loads(r.text)
    app.logger.info('lambda call: Result: ' + dict_r['result'] + ' | Trace ID: ' + dict_r['trace_id'])
    return 'Lambda Jaeger Traces'

## /api/spring?status=success|error
@app.route('/api/spring')
def spring_endpoint():
    app.logger.info('getting java spring endpoint')
    spring_host = env_config.spring_host
    spring_status = flask_request.args.get('status', str)
    spring_q = {'status': spring_status}

    r = requests.get('http://%s/api/demo' %spring_host, params=spring_q)

    app.logger.info('spring call: Result: ' + r.text)
    return 'Spring Trace'


if __name__ == '__main__':
    app.logger.info('%(message)s This is __main__ log')
    try:
        connect_mysql()
        app.run(host='0.0.0.0', port='5050')
    finally:
        app.logger.info('close pymysql connection')
        connection.close()
