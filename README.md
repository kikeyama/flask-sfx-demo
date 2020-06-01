# flask-sfx-demo

## Requirement

Backend database server powered by MySQL

## Environment Variables

When running container, following env vars are required.

`DB_HOST`: MySQL hostname  
`DB_USERNAME`: Username to connect MySQL  
`DB_PASSWORD`: Password to connect MySQL  
`DB_NAME`: Database name  
`API_FQDN`: AWS API Gateway endpoint FQDN (e.g. xxxxxxxxxx.execute-api.<REGION>.amazonaws.com)  
  
`SIGNALFX_SERVICE_NAME`: Specify a name for the service in SignalFx  
`SIGNALFX_ENDPOINT_URL`: endpoint URL for the Smart Agent, OpenTelemetry Collector, or ingest endpoint (e.g. http://localhost:9080/v1/trace)

## How to test

```
# Request with table query
curl "http://<hostname>:<port>/?name=apple

# POST Request
curl -X POST -d 'message=success' http://<hostname>:<port>/api/post

# Request Lambda microservice
curl http://<hostname>:<port>/api/lambda
```