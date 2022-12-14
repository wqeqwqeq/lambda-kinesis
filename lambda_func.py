import boto3
import json
import logging
from decimal import Decimal
import pymongo


logger = logging.getLogger()
logger.setLevel(logging.INFO)

url = "mongodb+srv://temp:stanleytest@cluster0.rcyqsmm.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(url)


db = client.workspace
table = db.products

getMethod = "Get"
postMethod = "Post"
patchMethod = "Patch"
deleteMethod = "Delete"
healthPath = "/health"
productPath = "/product"
productsPath = "/products"


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def buildResponse(status_code, body=None):
    response = {
        "status_code": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }
    if body is not None:
        response["body"] = json.dumps(body, cls=CustomEncoder)
    return response


def findOne(filter_query):
    try:
        response = table.find_one(filter_query)
        if len(response) != 0 and "_id" in response:
            return buildResponse(200, response)
        else:
            return buildResponse(
                404, {"Message": f" filter_query {filter_query} not found in table"}
            )
    except:
        logger.exception("Something here in findOne, logged...")


def getProducts():
    try:
        response = list(table.find({}))
        body = {"products": response}
        return buildResponse(200, body)
    except:
        logger.exception("Something wrong for getProducts, logging...")


def insertOne(request_body):
    try:
        table.insert_one(request_body)
        body = {"Operation": "SAVE", "Message": "SUCCESS", "Item": request_body}
        return buildResponse(200, body)
    except:
        logger.exception("Something wrong for insertOne, logging...")


def updateOne(query_key, query_value, update_key, update_value):
    try:
        response = table.update_one(
            filter={query_key: query_value}, update={update_key: update_value}
        )
        body = {
            "OPERATION": "UPDATE",
            "Message": "SUCCESS",
            "UpdateAttributes": response,
        }
        return buildResponse(200, body)

    except:
        logger.exception("Something wrong for updateOne, logging...")


def deleteOne(delete_key, delete_val):
    try:
        response = table.delete_one(filter={delete_key: delete_val})
        body = {"Operation": "DELETE", "Message": "SUCCESS", "deleteItem": response}
        return buildResponse(200, body)

    except:
        pass


def lambda_handler(event, context):
    logger.info(event)

    httpMethod = event["httpMethod"]
    path = event["path"]
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)

    elif httpMethod == getMethod and path == productPath:
        response = findOne(event["queryStringParameters"])

    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()

    elif httpMethod == postMethod and path == productPath:
        response = insertOne(json.loads(event["body"]))

    elif httpMethod == patchMethod and path == productPath:
        request_body = json.loads(event["body"])
        response = updateOne(
            request_body["queryValue"],
            request_body["queryKey"],
            request_body["updateKey"],
            request_body["updateValue"],
        )
    elif httpMethod == deleteMethod and path == productPath:
        request_body = json.loads(event["body"])
        delete_key = request_body["delete_key"]
        delete_val = request_body["delete_val"]
        response = deleteOne(delete_key, delete_val)

    else:
        response = buildResponse(404, "Not Found")

    return response

