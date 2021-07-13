import os
import json
import base64
import re
from io import BytesIO
from PIL import Image
from urllib import request

import boto3 # AWS SDK 

BUCKET = os.environ['BUCKET_NAME'] if 'BUCKET_NAME' in os.os.environ else 'iv-alex-oregon-bucket1' # Supplied by Function service-discovery wire
RESULT_HANDLER_URL = os.environ['RESULT_HANDLER_URL'] if 'RESULT_HANDLER_URL' in os.os.environ else 'http://localhost/api/images/updateStatus' # Supplied by Function service-discovery wire

s3 = boto3.client('s3')

def image_to_base64_str(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_byte = buffered.getvalue()
    img_str = base64.b64encode(img_byte).decode()
    return img_str

def base64_to_image(base64_str, image_path=None):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img



def lambda_handler(event, context):
    # Get id from event body
    id = event['id']
    new_id = event['newId']
    
    # Get image from S3 bucket
    response = s3.get_object(
        Bucket=BUCKET,
        Key=id,
    )
    img_bytes = response['Body'].read()
    img = Image.open(BytesIO(img_bytes))

    # Transform image to grayscale
    grayscale_img = img.convert('L')

    # Get image as Buffer

    in_mem_file = BytesIO()
    grayscale_img.save(in_mem_file, format=img.format)
    in_mem_file.seek(0)

    s3.upload_fileobj(
        in_mem_file, # This is what i am trying to upload
        BUCKET,
        Key=new_id,
        ExtraArgs={
            'ACL': 'public-read'
        }
    )
    
    # b64_g_img = image_to_base64_str(grayscale_img)
    response_body = json.dumps({
        "id": id,
        "newId": new_id,
        "processingType": "grayscaling"
        # "base64": b64_g_img
    })
    # print(response_body)

    data = str(response_body)
    data = data.encode('utf-8')

    req =  request.Request(RESULT_HANDLER_URL, data=data)
    resp = request.urlopen(req)

    return {
        "statusCode": 200,
        "body": response_body,
    }