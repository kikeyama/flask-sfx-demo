import os

# MySQL settings
db_host = os.environ.get('DB_HOST', 'localhost')
db_username = os.environ.get('DB_USERNAME', 'admin')
db_password = os.environ.get('DB_PASSWORD', 'password')
db_name = os.environ.get('DB_NAME', 'defaultdb')

# AWS API Gateway settings
api_fqdn = os.environ.get('API_FQDN', 'xxxxxxxx.execute-api.us-east-1.amazonaws.com')

# SignalFx settings
ORG_TOKEN = os.environ.get('ORG_TOKEN', '')
API_TOKEN = os.environ.get('API_TOKEN', '')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')