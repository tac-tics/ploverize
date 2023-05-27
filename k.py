import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
import numpy

with tf.device('/device:GPU:0'):
#with tf.device('/CPU:0'):
    seed = 7
    numpy.random.seed(seed)

    dataset = numpy.loadtxt("pima-indians-diabetes.csv", delimiter=",")

    X = dataset[:,0:8]
    Y = dataset[:,8]

    model = Sequential()
    model.add(Dense(12, input_dim=8, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(20, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(10, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(1, kernel_initializer='uniform', activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.fit(X, Y, validation_split=0.33, epochs=1500, batch_size=10)

    scores = model.evaluate(X, Y)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
