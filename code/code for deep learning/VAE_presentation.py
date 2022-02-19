#!/usr/bin/env python
# coding: utf-8

# ## This is an introduction of VAE
# 
# ### And we want to recommand you to use functional API, this time!
# 

# P
# (
# X
# )
# =
# ∫
# P
# (
# X
# |
# z
# )
# P
# (
# z
# )
# d
# z

# In[3]:


# This is funtional API

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow.keras.datasets import mnist

# Some Hyperparameters
batch_size = 100
original_dim = 784
latent_dim = 2 # latent dimension size
intermediate_dim = 256
epochs = 10


# get data
# Down load from internet!
(x_train, y_train_), (x_test, y_test_) = mnist.load_data() 

# Normalization
x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))


# **X** : data 

# In[4]:


x = Input(shape=(original_dim,)) # 784
h = Dense(intermediate_dim, activation='relu')(x)

# P(z|X) : mean and std
z_mean = Dense(latent_dim)(h)
z_log_var = Dense(latent_dim)(h)

# Reparameteration trick
def sampling(args):
    z_mean, z_log_var = args
    epsilon = K.random_normal(shape=K.shape(z_mean))
    return z_mean + K.exp(z_log_var / 2) * epsilon

# getting latent vector
z = Lambda(sampling, output_shape=(latent_dim,))([z_mean, z_log_var])


# we infer 
# P
# (
# z
# |
# X
# )
#  using a method called Variational Inference (VI)
#  
#  P
# (
# z
# )
#  : probability distribution of latent variable : sampling funtion

# In[5]:



# This a part of VAE
decoder_h = Dense(intermediate_dim, activation='relu')
decoder_mean = Dense(original_dim, activation='sigmoid')
h_decoded = decoder_h(z)
x_decoded_mean = decoder_mean(h_decoded)

# this is the model
vae = Model(x, x_decoded_mean)

# constrution and kl divergence
xent_loss = K.sum(K.binary_crossentropy(x, x_decoded_mean), axis=-1)
kl_loss = - 0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)
vae_loss = K.mean(xent_loss + kl_loss)

# add loss
vae.add_loss(vae_loss)
vae.compile(optimizer='rmsprop')
vae.summary()

vae.fit(x_train,
        shuffle=True,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(x_test, None))


# P
# (
# X
# |
# z
# )
#  : distribution of generating data given latent variable

# In[9]:


# Encoder P(z|X)
encoder = Model(x, z_mean)

x_test_encoded = encoder.predict(x_test, batch_size=batch_size)
plt.figure(figsize=(6, 6),dpi=100)
plt.scatter(x_test_encoded[:, 0], x_test_encoded[:, 1], c=y_test_)
plt.colorbar()
plt.show()

# Generator
decoder_input = Input(shape=(latent_dim,))
_h_decoded = decoder_h(decoder_input)
_x_decoded_mean = decoder_mean(_h_decoded)
generator = Model(decoder_input, _x_decoded_mean)


# In[7]:


# How these two dimensional vector matters
n = 15  # figure with 15x15 digits
digit_size = 28
figure = np.zeros((digit_size * n, digit_size * n))

# Gaussian distribution 
## percent point function, which is another name for the quantile function. 
## By default, norm.ppf uses mean=0 and stddev=1,
grid_x = norm.ppf(np.linspace(0.05, 0.95, n)) 
grid_y = norm.ppf(np.linspace(0.05, 0.95, n))

for i, yi in enumerate(grid_x):
    for j, xi in enumerate(grid_y):
        z_sample = np.array([[xi, yi]]) # Combine two scaler into a 2 dimension Vector..
        x_decoded = generator.predict(z_sample)
        digit = x_decoded[0].reshape(digit_size, digit_size)
        figure[i * digit_size: (i + 1) * digit_size,
               j * digit_size: (j + 1) * digit_size] = digit

plt.figure(figsize=(10, 10),dpi=100)
plt.imshow(figure, cmap='Greys_r')
plt.show()


# In[8]:


for i, yi in enumerate(grid_x):
    for j, xi in enumerate(grid_y):
        z_sample = tf.random.normal(shape=[1, latent_dim],mean=0,stddev=1)
        x_decoded = generator.predict(z_sample,steps=1)
        digit = x_decoded[0].reshape(digit_size, digit_size)
        figure[i * digit_size: (i + 1) * digit_size,
               j * digit_size: (j + 1) * digit_size] = digit

plt.figure(figsize=(10, 10),dpi=300)
plt.imshow(figure, cmap='Greys_r')
plt.show()

