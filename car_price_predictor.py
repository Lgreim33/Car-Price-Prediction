# -*- coding: utf-8 -*-
"""Car_Price_Predictor

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YgK2rMz5m9AcW23_g2IhCWj7cf-tVZUt
"""

import tensorflow as tf
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Normalization, Dense, InputLayer
from tensorflow.keras.losses import MeanSquaredError, Huber, MeanAbsoluteError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam

"""**Data Preperation**

"""
#import dataset
data = pd.read_csv("train.csv", ",")
data.head()

#create pairplot to visualize the relationship between inputs and cost 
sns.pairplot(data[["years",	"km",	"rating",	"condition",	"economy",	"top speed",	"hp",	"torque",	"current price"]], diag_kind = "kde")

tensor_data = tf.random.shuffle(tf.constant(data))

input = tensor_data[:,3:-1]

output = tensor_data[:,-1]
output = tf.expand_dims(output,axis = -1)


TRAIN_RATIO = .8
VAL_RATIO = .1
TEST_RATIO = .1
DATASET_SIZE = len(input)

output_train = output[:int(DATASET_SIZE * TRAIN_RATIO)]
input_train = input[:int(DATASET_SIZE * TRAIN_RATIO)]

train_dataset = tf.data.Dataset.from_tensor_slices((input_train,output_train))
train_dataset = train_dataset.shuffle(buffer_size = 8, reshuffle_each_iteration = True).batch(32).prefetch(tf.data.AUTOTUNE)

output_val = output[int(DATASET_SIZE * TRAIN_RATIO):int(DATASET_SIZE * (TRAIN_RATIO+VAL_RATIO))]
input_val = input[int(DATASET_SIZE * TRAIN_RATIO):int(DATASET_SIZE * (TRAIN_RATIO+VAL_RATIO))]

val_dataset = tf.data.Dataset.from_tensor_slices((input_val,output_val))
val_dataset = train_dataset.shuffle(buffer_size = 8, reshuffle_each_iteration = True).batch(32).prefetch(tf.data.AUTOTUNE)

output_test = output[int(DATASET_SIZE * (TRAIN_RATIO+VAL_RATIO)):]
input_test = input[int(DATASET_SIZE * (TRAIN_RATIO+VAL_RATIO)):]

test_dataset = tf.data.Dataset.from_tensor_slices((input_test,output_test))
test_dataset = train_dataset.shuffle(buffer_size = 8, reshuffle_each_iteration = True).batch(32).prefetch(tf.data.AUTOTUNE)

normalizer = Normalization()
normalizer.adapt(input)
normalizer(input)

from keras.api._v2.keras import activations
model = tf.keras.Sequential([InputLayer(input_shape = (8,)),
                             normalizer,
                             Dense(128, activation = "relu"),
                             Dense(128, activation = "relu"),
                             Dense(128, activation = "relu"),
                             Dense(1)])

model.summary()

tf.keras.utils.plot_model(model, to_file = "CarModel.png", show_shapes = True)

model.compile(optimizer = Adam(learning_rate = 1),
              loss = MeanAbsoluteError(),
              metrics = RootMeanSquaredError())

history = model.fit(train_dataset,validation_data = val_dataset, epochs = 100, verbose = 1)

#measure loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title("model loss")
plt.ylabel("loss")
plt.xlabel("epoch")
plt.legend(["train","train_loss"])
plt.show()

#measure performance
plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title("model performance")
plt.ylabel("rmse")
plt.xlabel("epoch")
plt.legend(["train", "val_train"])
plt.show()

model.evaluate(input_test,output_test)

model.predict(tf.expand_dims(input_test[0],axis = 0))

output_test[0]

out_true = list(output_test[:,0].numpy())

out_pred = list(model.predict(input_test)[:,0])

ind = np.arange(100)
plt.figure(figsize=(40,20))

width = 0.1

plt.bar(ind,out_pred,width,label="Predicted Car Price")
plt.bar(ind + width, out_true, width, label= "Actual Car Price")

plt.xlabel("Actual vs Predicted Car Price")
plt.ylabel("Car Prices")

plt.show()
