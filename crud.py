import boto3
import json 
import logging
from decimal import Decimal
# import pymongo



logger = logging.getLogger()
logger.setLevel(logging.INFO)

# url = "mongodb+srv://temp:stanleytest@cluster0.rcyqsmm.mongodb.net/?retryWrites=true&w=majority"
# client = pymongo.MongoClient(url,tlsCAFile=ca)


dynamodbTableName = 'product-invetory'
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(dynamodbTableName)

getMethod = "Get"
postMethod = "Post"
patchMethod = "Patch"
deleteMethod = "Delete"
healthPath = "/health"
productPath = "/product"
productsPath = "/products"

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def buildResponse(status_code, Body= None):
    response = {
        "status_code": status_code,
        "headers": {"Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
        }    
    }
    if body is not None:
        response["body"] = json.dumps(body,cls=CustomEncoder)
    return response


def getProduct(productId):
    try:
        response = table.getItem(
            key = {
                "productId" : productId
            }
        )
        if "Item" in response:
            return buildResponse(200, response["Item"])
        else:
            return buildResponse(404, {"Message": f"ProductId {productId} not found in table"})
    except:
        logger.exception("Something here in getProduct, logged...")

def getProducts():
    try:
        response = table.scan()
        result = response["Items"]

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartedKey = response["LastEvaluatedKey"])
            result.extend(response["Items"])
        body = {
            "products": response

        }
        return buildResponse(200,body)
    except:
        logger.exception("Something wrong for getProducts, logging...")

def saveProduct(request_body):
    try:
        table.put_item(Item = request_body)
        body = {
            "Operation": "SAVE",
            "Message": "SUCCESS"
            "Item": request_body

        }
        return buildResponse(200,body)
    except:
        logger.exception("Something wrong for saveProduct, logging...")
    
def modifyProduct(productId, updateKey,updateValue):
    try:
        response = table.update_item(
            Key = {
                "ProductId": productId
            },
            updateExpression = f"set {updateKey} =:value",
            ExpressionAttributeValue = {
                ":update" : updateValue
            },
            ReturnValues = "UPADATED_NEW"
    
        )
        body = {
            "OPERATION": "UPDATE",
            "Message": "SUCCESS",
            "UpdateAttributes": response
        }
        return buildResponse(200,body)

    except:
        logger.exception("Something wrong for modifyProduct, logging...")
        
def deleteProduct(productId):
    try:
        response = table.delete_item(
            Key = {"productId": productId},
            ReturnValues = "ALL_OLD"

        )
        body = {
            "Operation": "DELETE",
            "Message": "SUCCESS,
            "deleteItem":response
        }
        return buildResponse(200,body)
    except:
        logger.exception("Something wrong for deleteProduct, logging...")
        


def lambda_handler(event,context):
    logger.info(event)

    httpMethod = event["httpMethod"]
    path = event["path"]
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    
    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event["queryStringParameters"]["productId"])
    
    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()
    
    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event["body"]) )
    
    elif httpMethod == patchMethod and path == productPath:
        request_body = json.loads(event["body"])
        response = modifyProduct(request_body["productId"],
                                 request_body["updateKey"],
                                 request_body["updateValue"]
                                 )
    elif httpMethod == deleteMethod and path == productPath:
        request_body = json.loads(event["body"])
        response = deleteProduct(request_body["productId"])
    
    else:
        response = buildResponse(404, "Not Found")
    
    return response

       