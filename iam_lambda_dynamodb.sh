# Download aws cli v2 in linux 
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
# or use this to install in a dir which has write permission
./aws/install -i /usr/local/aws-cli -b /usr/local/bin

# Config aws cli use aws config 
# just a example
aws configure
# can be find https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-2#/security_credentials 
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-2
Default output format [None]: json



# Create a dynamodb table
aws dynamodb create-table \
--table-name myapp_dynamodb_table \
--attribute-definitions AttributeName=id,AttributeType=S \
--key-schema AttributeName=id,KeyType=HASH \
--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5


# Create IAM role
## Create assume role policy definition
cat <<'EOF'> myapp_lambda_assume_role_policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
 

aws iam create-role \
--role-name myapp_lambda_iam_role \
--assume-role-policy-document file://myapp_lambda_assume_role_policy.json
 
## Add AWS managed policy to the role for access to CloudWatch and DynamoDB and Lambda-kinesis-execution permission
aws iam attach-role-policy \
--role-name myapp_lambda_iam_role \
--policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess &&
aws iam attach-role-policy \
--role-name myapp_lambda_iam_role \
--policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess

aws iam attach-role-policy \
--role-name myapp_lambda_iam_role \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole

 
# if in windows git bash, no jq, run following command as admin
curl -L -o /usr/bin/jq.exe https://github.com/stedolan/jq/releases/latest/download/jq-win64.exe


## Get the role ARN
ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account) &&
IAM_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/myapp_lambda_iam_role &&
echo $IAM_ROLE_ARN
 

# Create Lambda function
## Zip the code
zip function.zip lambda_function.py
# in powershell
# Compress-Archive -Path C:\Users\yzhhu\Desktop\AWS\lambda_kinesis\to_deploy -DestinationPath C:\Users\yzhhu\Desktop\AWS\lambda_kinesis\to_deploy\function.zip
 
## Create a lambda function
aws lambda create-function \
--function-name myapp_lambda_function2 \
--runtime python3.8 \
--zip-file fileb://function.zip  \
--handler lambda_func.lambda_handler  \
--runtime python3.8 \
--role $IAM_ROLE_ARN


# update lambda function

aws lambda update-function-code \
--function-name myapp_lambda_function2 \
--zip-file fileb://function.zip 
 
## Get lambda function ARN
LAMBDA_ARN=$(aws lambda get-function \
--function-name  myapp_lambda_function2 | jq -r .Configuration.FunctionArn) &&
echo $LAMBDA_ARN


## Create stream and get stream arn
aws kinesis create-stream --stream-name lambda-stream --shard-count 1 
stream_arn=$(aws kinesis describe-stream --stream-name lambda-stream | jq -r .StreamDescription.StreamARN)


## create event source mapping btw kinesis and lambda 
aws lambda create-event-source-mapping --function-name myapp_lambda_function2 \
--event-source  $stream_arn \
--batch-size 100 --starting-position LATEST


aws lambda list-event-source-mappings --function-name myapp_lambda_function2 \
--event-source $stream_arn 


## kinesis put data 
aws kinesis put-record \
--stream-name lambda-stream \
--partition-key 1 \
--data "a"


## kinesis put 1000 records with 0.01 second sleep 
for k in $(seq 2 1000)
do 
  aws kinesis put-record \
  --stream-name lambda-stream \
  --partition-key 1 \
  --data "message $k hello mongo, from kinesis"   
  echo  "message $k hello mongo, from kinesis:)" 
  sleep 0.01
done






# Create a API gateway, can be replaced by swagger 
aws apigateway import-rest-api --body 'fileb:///path/to/API_Swagger_template.json'

## Create a HTTP API
API_ID=$(aws apigatewayv2 create-api \
--name myapp_http_api \
--protocol-type HTTP \
--target $LAMBDA_ARN |tee myapp_http_api.json| jq -r .ApiId)
 
## Get integration id
INTEGRATION_ID=$(aws apigatewayv2 get-integrations \
--api-id $API_ID | jq -r .Items[].IntegrationId)
 
## Create API routes
ROUTE_ID1=$(aws apigatewayv2 create-route \
--api-id $API_ID \
--route-key 'GET /items' \
--target integrations/$INTEGRATION_ID | jq -r .RouteId) &&
ROUTE_ID2=$(aws apigatewayv2 create-route \
--api-id $API_ID \
--route-key 'GET /items/{id}' \
--target integrations/$INTEGRATION_ID | jq -r .RouteId) &&
ROUTE_ID3=$(aws apigatewayv2 create-route \
--api-id $API_ID \
--route-key 'PUT /items' \
--target integrations/$INTEGRATION_ID | jq -r .RouteId) &&
ROUTE_ID4=$(aws apigatewayv2 create-route \
--api-id $API_ID \
--route-key 'DELETE /items/{id}' \
--target integrations/$INTEGRATION_ID | jq -r .RouteId)
 
## Provide access to API gateway to invoke the lambda function
AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account) &&
AWS_REGION=ap-south-1 &&
aws lambda add-permission \
--statement-id api-invoke-lambda \
--action lambda:InvokeFunction \
--function-name $LAMBDA_ARN \
--principal apigateway.amazonaws.com \
--source-arn "arn:aws:execute-api:ap-south-1:$AWS_ACCOUNT_ID:$API_ID/*"



# call the api

## Get the api endpoint
URL=$(aws apigatewayv2 get-api \
--api-id $API_ID | jq -r .ApiEndpoint) &&
echo $URL
 
## Insert couple of items
curl -X "PUT" \
-H "Content-Type: application/json" \
-d "{\"id\": \"00001\", \"price\": 10, \"name\": \"mango\"}" \
$URL/items
 
curl -X "PUT" \
-H "Content-Type: application/json" \
-d "{\"id\": \"00002\", \"price\": 20, \"name\": \"banana\"}" \
$URL/items
 
## Get all items
curl $URL/items
 
## Get specific item
curl $URL/items/00002
 
## Delete an item
curl -X "DELETE" $URL/items/00001


# clean up
## Delete routes
aws apigatewayv2 delete-route \
--api-id $API_ID \
--route-id $ROUTE_ID1 &&
aws apigatewayv2 delete-route \
--api-id $API_ID \
--route-id $ROUTE_ID2 &&
aws apigatewayv2 delete-route \
--api-id $API_ID \
--route-id $ROUTE_ID3 &&
aws apigatewayv2 delete-route \
--api-id $API_ID \
--route-id $ROUTE_ID4
 
## Delete the http api
aws apigatewayv2 delete-api \
--api-id $API_ID
 
## Delete the lambda function
aws lambda delete-function \
--function-name myapp_lambda_function
 
## Delete the IAM role
aws iam detach-role-policy \
--role-name myapp_lambda_iam_role \
--policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess &&
aws iam detach-role-policy \
--role-name myapp_lambda_iam_role \
--policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess &&
aws iam delete-role \
--role-name myapp_lambda_iam_role
 
## Delete the dynamodb table
aws dynamodb delete-table \
--table-name myapp_dynamodb_table