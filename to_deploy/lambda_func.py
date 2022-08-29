import boto3
import json
import logging
from decimal import Decimal
import pymongo
import certifi
import bson

ca = certifi.where()
print("This is where certifi is located" + ca)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

url = "mongodb+srv://temp:stanleytest@cluster0.rcyqsmm.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(url, tlsCAFile=ca)


db = client.workspace
table = db.work

getMethod = "GET"
postMethod = "POST"
patchMethod = "PATCH"
deleteMethod = "DELETE"
healthPath = "/health"
productPath = "/product"
productsPath = "/products"


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def buildResponse(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    }
    print(body,status_code)
    print('This is response b4 add body ')
    print(response)
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
        print('This is response after add body ')
        print(response)
    return response


def findOne(filter_query):
    try:
        response = table.find_one(filter_query)
        if response is not None:
            return buildResponse(200, response)
        else:
            return buildResponse(
                404, {"Message": f" filter_query {filter_query} not found in table"}
            )
    except Exception as e:
        body = {"Excepting":str(e)}
        logger.exception("Something here in findOne, logged...")
        return buildResponse(502,body)


def getProducts():
    try:
        response = list(table.find({}))
        body = {"products": response}
        return buildResponse(200, body)
    except Exception as e:
        body = {"Excepting":str(e)}
        logger.exception("Something wrong for getProducts, logging...")
        return buildResponse(502,body)


def insertOne(request_body):
    try:
        table.insert_one(request_body)
        body = {"Operation": "SAVE", "Message": "SUCCESS", "Item": request_body}
        return buildResponse(200, body)
    except Exception as e:
        body = {"Excepting":str(e)}
        logger.exception("Something wrong for insertOne, logging...")
        return buildResponse(502,body)


def updateOne(filter_query, update_query):
    try:
        response = table.find_one(filter_query)
        if response is not None:
            response = table.update_one(
                filter=filter_query, update={"$set": update_query}
            )

            body = {
                "OPERATION": "UPDATE",
                "Message": "SUCCESS",
                "UpdateTarget": filter_query,
                "UpdatedAttributes": update_query
            }
            return buildResponse(200, body)
        else:
            return buildResponse(404,{"Message": f"filter query {filter_query} not found in db"})

    except Exception as e:
        body = {"Excepting":str(e)}
        logger.exception("Something wrong for updateOne, logging...")
        return buildResponse(502,body)


def deleteOne(request_body):
    try:
        response = table.delete_one(filter=request_body)
        body = {"Operation": "DELETE", "Message": "SUCCESS", "deleteItem": request_body}
        return buildResponse(200, body)

    except Exception as e:
        body = {"Excepting":str(e)}
        return buildResponse(502,body)
        pass


def lambda_handler(event, context):
    logger.info(event)
    print("This is the event", event)
    print(type(event),type(context))

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
            request_body["filter_query"],
            request_body["update_query"]
        )
    elif httpMethod == deleteMethod and path == productPath:
        request_body = json.loads(event["body"])
        response = deleteOne(request_body)

    else:
        response = buildResponse(404, "Not Found")

    return response


