import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf

# Load labeled samples
df = pd.read_csv("hello_data.csv")  # repeat for all signs
df2 = pd.read_csv("yes_data.csv")
df3 = pd.read_csv("no_data.csv")
df = pd.concat([df, df2, df3])

X = df.iloc[:, :-1].values  # 63 landmark values
y = df.iloc[:, -1].values   # label (e.g., 'hello')

# Label encode
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Normalize
X = X - np.mean(X, axis=0)
X = X / np.std(X, axis=0)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2)

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(63,)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(np.unique(y_encoded)), activation='softmax')
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=30, validation_data=(X_test, y_test))

# Save
model.save("sign_model.h5")
np.save("classes.npy", le.classes_)
