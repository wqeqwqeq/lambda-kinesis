lambda_deploy()
{   
    aws_lambda_function_name=$1
    set -eu
    echo "Currently in $(pwd)"
    rm function.zip
    echo "Removed function.zip"
    powershell "& Compress-Archive -Path .\* -DestinationPath .\function.zip"
    echo "Uploading $aws_lambda_function_name"
    success_func=$(aws lambda update-function-code \
    --function-name $aws_lambda_function_name\
    --zip-file fileb://function.zip | jq -r .FunctionName)
    echo " Successful upload new function.zip to $success_func "
}

# message_to_kinesis()
# {
#     set -eu
#     stream_name=$1
#     message=$2
#     aws kinesis put-record \
#     --stream-name $stream_name \
#     --partition-key 1 \
#     # --cli-binary-format raw-in-base64-out \
#     --data $message
# }