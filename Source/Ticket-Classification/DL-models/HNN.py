from tensorflow.keras.layers import Conv1D, GlobalMaxPooling1D, Dense, Dropout, Bidirectional, LSTM, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.regularizers import l2
from matplotlib import pyplot as plt
import numpy as np
import time


import sys
import os

print("HNN model")

# Get the absolute path of the directory containing other_script.py
other_directory_path = os.path.abspath('/home/users/elicina/Master-Thesis/Source/Ticket-Classification')

# Add the directory to sys.path
sys.path.append(other_directory_path)

# Now you can import the module
import Tokenization 
from Tokenization import *

X_train, X_val, Y_train, Y_val = train_test_split(train_embeddings, train_labels, test_size=0.2, random_state=42, shuffle=True)

train_embeddings_resampled, train_labels_resampled_w2v = smote.fit_resample(X_train, Y_train) # type: ignore

# Reshape data for Conv1D input
train_embeddings_resampled = train_embeddings_resampled.reshape(train_embeddings_resampled.shape[0], train_embeddings_resampled.shape[1], 1) # type: ignore
X_val = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)
test_embeddings = test_embeddings.reshape(test_embeddings.shape[0], test_embeddings.shape[1], 1)

# Create the model
model = Sequential()

model.add(Conv1D(filters=128, kernel_size=5, activation='relu', input_shape=(train_embeddings_resampled.shape[1], 1)))
model.add(BatchNormalization())

model.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model.add(BatchNormalization())

model.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model.add(BatchNormalization())

model.add(GlobalMaxPooling1D())

model.add(Dense(units=128, activation='relu', kernel_regularizer=l2(0.01)))
model.add(Dropout(rate=0.5))
model.add(BatchNormalization())

model.add(Dense(5, activation='softmax'))
model.add(Dropout(rate=0.5))

# Compile the model with sparse_categorical_crossentropy
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Print model summary
model.summary()

# Define callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.0001)
model_checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True)

start_time = time.time()


# Train the model
history = model.fit(train_embeddings_resampled, train_labels_resampled_w2v, epochs=50, batch_size=64, 
          validation_data=(X_val, Y_val), callbacks=[early_stopping, reduce_lr, model_checkpoint])


end_time = time.time()
training_time = end_time - start_time
print(f'Training Time: {training_time:.2f} seconds')


from sklearn.metrics import log_loss, precision_score, recall_score, f1_score, accuracy_score

# Make predictions on the test set
predictions = model.predict(test_embeddings)
predicted_labels = np.argmax(predictions, axis=1)

# Convert true labels to categorical (if needed)
true_labels_categorical = test_labels

# Calculate metrics
loss = log_loss(true_labels_categorical, predictions)
precision = precision_score(true_labels_categorical, predicted_labels, average='weighted')
recall = recall_score(true_labels_categorical, predicted_labels, average='weighted')
f1 = f1_score(true_labels_categorical, predicted_labels, average='weighted')
accuracy = accuracy_score(true_labels_categorical, predicted_labels)

print(f'Test Loss: {loss:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1-score: {f1:.4f}')
print(f'Accuracy: {accuracy:.4f}')


# Plot the training and validation loss
plt.figure(figsize=(12, 6))
plt.plot(history.history['loss'], label='Train Loss') # type: ignore 
plt.plot(history.history['val_loss'], label='Validation Loss') # type: ignore
plt.title(f'Training and Validation Loss - Test Accuracy: {accuracy}')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.savefig('HNN_loss_plot.png')  # Save the plot as an image
plt.show()
