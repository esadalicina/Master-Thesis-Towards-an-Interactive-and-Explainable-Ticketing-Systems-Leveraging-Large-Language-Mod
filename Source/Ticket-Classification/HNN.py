from sklearn.model_selection import train_test_split
from Tokenization import *
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, SpatialDropout1D, Dense, Dropout, Bidirectional, LSTM
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


X_train, X_val, Y_train, Y_val = train_test_split(train_embeddings, train_labels, test_size=0.2, random_state=42, shuffle=True)

train_embeddings_resampled, train_labels_resampled_w2v = smote.fit_resample(X_train, Y_train) # type: ignore

# Reshape data for Conv1D input
train_embeddings_resampled = train_embeddings_resampled.reshape(train_embeddings_resampled.shape[0], train_embeddings_resampled.shape[1], 1) # type: ignore
X_val = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)
test_embeddings = test_embeddings.reshape(test_embeddings.shape[0], test_embeddings.shape[1], 1)


# Create the model
model = Sequential()

model.add(Conv1D(filters=128, kernel_size=5, activation='relu', input_shape=(train_embeddings_resampled.shape[1], 1)))

# Optional: Spatial Dropout for regularization
model.add(SpatialDropout1D(0.2))

# Bidirectional LSTM Layer
model.add(Bidirectional(LSTM(100, return_sequences=True)))
model.add(Bidirectional(LSTM(100)))  # Another LSTM layer for more complex learning

# Dropout for regularization
model.add(Dropout(0.5))

# Output layer
model.add(Dense(5, activation='softmax'))

# Compile the model with sparse_categorical_crossentropy
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Print model summary
model.summary()

# Define callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.001)

# Train the model
model.fit(train_embeddings_resampled, train_labels_resampled_w2v, epochs=100, batch_size=64, 
          validation_data=(X_val, Y_val), callbacks=[early_stopping, reduce_lr]) 

