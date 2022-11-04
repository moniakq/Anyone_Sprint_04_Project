import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.applications import resnet50
from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
#print('model antes de db')
db = redis.Redis(
    host=settings.REDIS_IP, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB_ID, 
    charset="utf-8",
    decode_responses=True
)
#print('model despues de db')

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = resnet50.ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    #basic error handling to prevent the system crash when stresstesting with locust. If the model can't proccess the image
    #it returns 0 probability and in that case the api retunrs a 400 httpcode
    try:
        #Loads the image
        img = image.load_img(os.path.join(settings.UPLOAD_FOLDER, image_name), target_size=(224, 224))
        #Preproccess image
        x = image.img_to_array(img)
        x_batch = np.expand_dims(x, axis=0)
        x_batch = resnet50.preprocess_input(x_batch)
        #Get some predictions
        preds = model.predict(x_batch)
        #decode predictions
        res=resnet50.decode_predictions(preds, top=1)

        class_name = res[0][0][1]
        pred_probability = float(round(res[0][0][2],4))
    except:
        class_name=image_name
        pred_probability=0
    # TODO

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        
        #   1. Take a new job from Redis
        _, msg = db.brpop(settings.REDIS_QUEUE)
        msg = json.loads(msg)
        #   2. Run your ML model on the given data
        clas, pred = predict(msg['image_name'])
        #   3. Store model prediction 
        pred = str(pred)
        dict2={'prediction':clas,'score':pred}
        job_data = json.dumps(dict2)
        #   4. Store the results on Redis using the original job ID
        db.set(msg['id'],job_data)
        # Don't forget to sleep for a bit at the end
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
