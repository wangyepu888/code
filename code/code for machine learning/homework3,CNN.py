# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 21:25:31 2021

@author: Yepu Wang
"""

import tensorflow as tf                 
from tensorflow.keras import layers
import numpy as np

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout,Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras import  backend

from keras.optimizers import SGD

from keras.utils import to_categorical


from keras.datasets import mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()


img_x, img_y = 28, 28
x_train = x_train.reshape(x_train.shape[0], 784)
x_test = x_test.reshape(len(x_test.shape), 784)

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print(y_train[0])
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)
print(y_train[0])
'''
# structure
model = Sequential()
model.add(Conv2D(32, kernel_size=(5,5), activation='relu', input_shape=(28, 28, 1)))
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
model.add(Conv2D(64, kernel_size=(5,5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
model.add(Flatten())
model.add(Dense(1000, activation='relu'))
model.add(Dense(10, activation='softmax'))



learning_rate=0.001
model.compile(optimizer=tf.keras.optimizers.Adam(lr=learning_rate), loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=10, )

train=model.evaluate(x_train,y_train)
print('training accuracy=',train[1])
test = model.evaluate(x_test,y_test) 
print('testing accuracy=',test[1]) 

'''


