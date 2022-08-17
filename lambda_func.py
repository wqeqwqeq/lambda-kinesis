# import json
import base64


def lambda_handler(event, context):
    for record in event["Records"]:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record["kinesis"]["data"])
        print(
            "Decoded payload: "
            + str(payload)
            + " Length of msg in char: "
            + str(len(payload))
        )
    print(event)
    print("context type is " + type(context))
    print(context)

