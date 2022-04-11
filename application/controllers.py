from tensorflow import keras
from keras.initializers import glorot_uniform

with open("/media/pi/Flash/basic_bmodel/basic_bmodel.json", 'r') as json_file:
    json_model = json_file.read()

model = keras.models.model_from_json(json_model)
model.summary()
#model = load_model("/media/pi/Flash/basic_bmodel/basic_bmodel.h5")