import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers, initializers, regularizers

# File load
fname = os.path.join("barc.csv")
  
with open(fname) as f:
    data = f.read()
  
lines = data.split("\n")
lines = lines[0:-1]
header = lines[0].split(",")
lines = lines[1:]

# Series variables
open_price = np.zeros((len(lines),))
high_price = np.zeros((len(lines),))
low_price = np.zeros((len(lines),))
close_price = np.zeros((len(lines),))
volume = np.zeros((len(lines),))
raw_data = np.zeros((len(lines), len(header) - 1)) 

# Train data extraction
for i, line in enumerate(lines):
    values = [float(x) for x in line.split(",")[1:]]
    open_price[i] = values[0] 
    high_price[i] = values[1] 
    low_price[i] = values[2] 
    close_price[i] = values[3] 
    volume[i] = values[4]                       
    raw_data[i, :] = values[:]  

# Open price standardization   
open_mean = open_price[:].mean(axis=0)
open_price -= open_mean
open_std_mean = open_price[:].std(axis=0)
open_price /= open_std_mean

# High price standardization 
high_mean = high_price[:].mean(axis=0)
high_price -= high_mean
high_std_mean = high_price[:].std(axis=0)
high_price /= high_std_mean

# Low price standardization 
low_mean = low_price[:].mean(axis=0)
low_price -= low_mean
low_std_mean = low_price[:].std(axis=0)
low_price /= low_std_mean

# Close price standardization 
close_mean = close_price[:].mean(axis=0)
close_price -= close_mean
close_std_mean = close_price[:].std(axis=0)
close_price /= close_std_mean

# Volume standardization
volume_mean = volume[:].mean(axis=0)
volume -= volume_mean
volume_std_mean = volume[:].std(axis=0)
volume /= volume_std_mean

length = len(open_price[:])
train_data = np.zeros((length, 4))
target_data = np.zeros(length)

# Train data generation
for i, array in enumerate(train_data):
    train_data[i, 0] = open_price[i]
    train_data[i, 1] = high_price[i] 
    train_data[i, 2] = low_price[i] 
    train_data[i, 3] = close_price[i] 
    # train_data[i, 4] = volume[i] 
    target_data[i] = open_price[i]

# Dataset generation parameters
sampling_rate = 1
sequence_length = 10
delay = sequence_length + 5 - 1
batch_size = 8

# Datasets length 
num_train_samples = int(0.9 * len(train_data))
num_val_samples = int(0.9 * len(train_data))
num_test_samples = int(1 * len(train_data) - delay - 1)

# Train datasets generation
train_dataset = keras.utils.timeseries_dataset_from_array(
    data = train_data[:-delay], 
    targets=target_data[delay:], 
    sampling_rate=sampling_rate,
    sequence_length=sequence_length, 
    shuffle=True,
    batch_size=batch_size,
    start_index=0)

# Validation datasets generation
val_dataset = keras.utils.timeseries_dataset_from_array(
    data = train_data[:-delay],
    targets=target_data[delay:],
    sampling_rate=sampling_rate,
    sequence_length=sequence_length,
    shuffle=True,
    batch_size=batch_size,
    start_index=num_val_samples)

# Test datasets generation
test_dataset = keras.utils.timeseries_dataset_from_array(
    data = train_data[:-delay],
    targets=target_data[delay:],
    sampling_rate=sampling_rate,
    sequence_length=sequence_length,
    shuffle=True,
    batch_size=batch_size,
    start_index=num_val_samples)

# Model structure
inputs = keras.Input(shape=(sequence_length, train_data.shape[-1]))
x = layers.LSTM(64, 
                recurrent_dropout=0.1, 
                activation="tanh", 
                return_sequences = True,)(inputs)
x = layers.LSTM(32, 
                recurrent_dropout=0.1, 
                activation="tanh", )(inputs)
x = layers.Flatten()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(1, activation="tanh")(x)
model = keras.Model(inputs, outputs)

callbacks = [
    keras.callbacks.ModelCheckpoint("jena_dense.keras",          
                                    save_best_only=True)
] # Save the best model during training

# Model train
model.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
history = model.fit(train_dataset,
                    epochs=50,
                    validation_data=val_dataset,
                    callbacks=callbacks)

model = keras.models.load_model("jena_dense.keras") # Load saved model

print(f"Test MAE: {model.evaluate(test_dataset)[1]:.2f}") # test the performance of the model

for inputs, targets in test_dataset:
    prediction = model.predict(inputs[:1])
    print("prediction shape:", prediction.shape, "prediction open price: ", prediction)

# Model training check
loss = history.history["mae"]
val_loss = history.history["val_mae"]
epochs = range(1, len(loss) + 1)
plt.figure()
plt.plot(epochs, loss, "bo", label="Training MAE")
plt.plot(epochs, val_loss, "b", label="Validation MAE")
plt.title("Training and validation MAE")
plt.legend()
plt.show()