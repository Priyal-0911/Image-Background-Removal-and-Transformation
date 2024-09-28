import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import base64
import io, os, tempfile
import json
import uuid
from typing import List

import websocket
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PIL import Image
import urllib.request
import urllib.parse
import urllib.error

app = FastAPI()

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images


def prompt_define(input, source):
    prompt_text = """
    {
    "1": {
        "inputs": {
        "image": "businessman-black-suit-promoting-something.jpg",
        "upload": "image"
        },
        "class_type": "LoadImage",
        "_meta": {
        "title": "Load Image"
        }
    },
    "2": {
        "inputs": {
        "image": "ii2.jpg",
        "upload": "image"
        },
        "class_type": "LoadImage",
        "_meta": {
        "title": "Load Image"
        }
    },
    "4": {
        "inputs": {
        "images": [      
            "5",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "5": {
        "inputs": {
        "enabled": true,
        "swap_model": "inswapper_128.onnx",
        "facedetection": "YOLOv5l",
        "face_restore_model": "none",
        "face_restore_visibility": 1,
        "codeformer_weight": 1,
        "detect_gender_input": "no",
        "detect_gender_source": "no",
        "input_faces_index": "0",
        "source_faces_index": "0",
        "console_log_level": 1,
        "input_image": [
            "1",
            0
        ],
        "source_image": [
            "2",
            0
        ]
        },
        "class_type": "ReActorFaceSwap",
        "_meta": {
        "title": "ReActor 🌌 Fast Face Swap"
        }
    }
    }
    """

    prompt = json.loads(prompt_text)

    prompt["1"]["inputs"]["image"] = "/home/ml/Downloads/2/ComfyUI_temp_ndkbk_00002_.png"

    #set the seed for our KSampler node
    prompt["2"]["inputs"]["image"] = "/home/ml/Downloads/2/ii2.jpg"

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)

    return images


@app.post("/face-swap")
async def face_swap(input_image: UploadFile = File(...), source_image: UploadFile = File(...)):
    try:
        # Create temporary files with ".jpg" extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as input_temp, \
                tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as source_temp:

            # Write image content to temporary files
            await input_image.seek(0) # Move to the beginning of the file
            input_temp.write(await input_image.read())
            
            await source_image.seek(0)
            source_temp.write(await source_image.read())

            input_image_path = input_temp.name
            source_image_path = source_temp.name

            images = prompt_define(input_image_path, source_image_path)

            # ws = websocket.WebSocket()
            # ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
            # images = get_images(ws, prompt)

            for node_id in images:
                for image_data in images[node_id]:
                    image = Image.open(io.BytesIO(image_data))
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG") 

                    base64_encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    return {"image": base64_encoded_image}  # Return as JSON
                
    finally:
        # Clean up temporary files
        os.remove(input_image_path)
        os.remove(source_image_path)