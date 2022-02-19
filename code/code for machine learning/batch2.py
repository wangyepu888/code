
import numpy as np


training_images = np.loadtxt("01Train_Images.gz") #x
labels = np.loadtxt("01Train_Labels.gz") #y
test_images = np.loadtxt("01Test_Images.gz")
test_labels = np.loadtxt("01Test_Labels.gz")

#Initialization
w=[]
for i in range(785):
    a=np.random.normal(0,0.1)
    w.append(a)
w=np.mat(w,dtype=float)
w=w.reshape(785,1)
L=0.01

labels=labels[:,1]
test_labels =test_labels [:,1]

numImages=training_images.shape[0]
numTestingImages=test_images.shape[0]
print(numImages)
print(numTestingImages)
print(labels)
training_images=np.insert(training_images,0,values=1,axis=1)
test_images=np.insert(test_images,0,values=1,axis=1)
def sigmoid(t):
    return 1 / (1 + np.exp(-t))


def train_batch(imags, labels):
    global w
    y=labels
    y=y.reshape(len(y),1)
    for j in range(785):
       for itineration in range(300):
          n=sigmoid(np.dot(imags,w))-y
          m=np.dot(imags[:,j],n)/numImages
          w[j]=w[j]-0.01*m


train_batch(training_images,labels)
print(w)



def predict(imag, label):
    global w
    imag=imag.reshape(1,785)
    p=sigmoid(np.dot(imag,w))
    print("p:",p," label",label)
    
    if p >= 0.5 and label == 1:
        return True
    elif p < 0.5 and label == 0:
        return True
    else:
        return False

correct = 0  # Number of correct predictions the network makes

# Test Accuracy
for i in range(numTestingImages):
    if predict(test_images[i], test_labels[i]):
        correct += 1

# Train Accuracy
train_correct = 0
for i in range(numImages):
    if predict(training_images[i], labels[i]):
        train_correct += 1

print ("Training Accuracy: " + str(float(train_correct) / len(training_images)))
print ("Testing Accuracy: " + str(float(correct) / len(test_images)))

