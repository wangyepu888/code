# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 22:09:57 2021

@author: Wenrui Mu
"""
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers


train_images = np.loadtxt("58Train_Images.gz")
train_labels = np.loadtxt("58Train_Labels.gz")
test_images = np.loadtxt("58Test_Images.gz")
test_labels = np.loadtxt("58Test_Labels.gz")



model = tf.keras.models.Sequential([
  layers.Flatten(input_dim=(784)),
  layers.Dense(784, activation='relu'), #choose relu as activation function
  layers.Dense(256, activation='relu')
  layers.Dense(2, activation='softmax')
])


#print model summary
#print(model.summary()) 

#compile the model

learning_rate=0.01 #0.01
model.compile(loss='categorical_crossentropy',optimizer=tf.keras.optimizers.Adam(lr=learning_rate),metrics=['accuracy'])
train_history = model.fit(x=train_images,y=train_labels,epochs=10,batch_size=100,verbose=2) 


#accuracy
test_scores = model.evaluate(test_images,test_labels) 
print('test set accuracy=',test_scores[1]) 
train_scores=model.evaluate(train_images,train_labels)
print('train set accuracy=',train_scores[1])

#result
#test set accuracy= 0.99571276
#train set accuracy= 0.9995581