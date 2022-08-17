aws lambda create-function
--function-name ProcessKinesisRecords \
--zip-file fileb://function.zip  \
--handler lambda_func.lambda_handler  \
--runtime python3.8 \
--role arn:aws:iam::256259474153:role/lambda-kinesis-role \




aws lambda update-function-code \
--function-name ProcessKinesisRecords \
--zip-file fileb://function.zip 


# command latency? 

aws kinesis create-stream --stream-name lambda-stream --shard-count 1

aws kinesis describe-stream --stream-name lambda-stream

aws kinesis put-record 
--stream-name lambda-stream 
--partition-key 1 
--cli-binary-format raw-in-base64-out 
--data "a"

aws lambda create-event-source-mapping --function-name ProcessKinesisRecords \
--event-source  arn:aws:kinesis:us-east-2:256259474153:stream/lambda-stream \
--batch-size 100 --starting-position LATEST


aws lambda list-event-source-mappings --function-name ProcessKinesisRecords \
--event-source arn:aws:kinesis:us-east-2:256259474153:stream/lambda-stream


# how to fetch log from cloud watch? 


# more about kinesis
