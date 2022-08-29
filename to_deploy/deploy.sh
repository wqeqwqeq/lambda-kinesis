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

test()
{
test=$1
echo $test
}