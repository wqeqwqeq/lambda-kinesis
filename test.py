import json
import base64

with open("input.txt", "r") as f:
    txt = f.read()

js = json.loads(txt)


def lambda_handler(event):
    for record in event["Records"]:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record["kinesis"]["data"])
        print(payload)
        print(record)

        print(
            "Decoded payload: "
            + str(payload)
            + " Length of msg in char: "
            + str(len(payload))
        )
    #    print("Raw record: " + record + " " + record["kinesis"]["data"] + " " + payload)


# lambda_handler(js)
import sys

print(sys.path)
import pymongo

print("imported")
