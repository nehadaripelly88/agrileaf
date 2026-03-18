import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger

print(f"TensorFlow version: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")

CONFIG = {
    "data_dir": "data/plantvillage",
    "image_size": (224, 224),
    "batch_size": 32,
    "epochs": 50,
    "learning_rate": 0.0001,
    "validation_split": 0.2,
    "model_save_path": "agrileaf_model.h5",
    "class_names_path": "class_names.json",
}


def create_data_generators():
    print("\n[1/5] Preparing data generators...")

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=CONFIG["validation_split"]
    )

    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=CONFIG["validation_split"]
    )

    train_generator = train_datagen.flow_from_directory(
        CONFIG["data_dir"],
        target_size=CONFIG["image_size"],
        batch_size=CONFIG["batch_size"],
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=42
    )

    val_generator = val_datagen.flow_from_directory(
        CONFIG["data_dir"],
        target_size=CONFIG["image_size"],
        batch_size=CONFIG["batch_size"],
        class_mode='categorical',
        subset='validation',
        shuffle=False,
        seed=42
    )

    print(f"  Training images:   {train_generator.samples}")
    print(f"  Validation images: {val_generator.samples}")
    print(f"  Number of classes: {train_generator.num_classes}")

    return train_generator, val_generator


def build_model(num_classes):
    print("\n[2/5] Building CNN model...")

    base_model = MobileNetV2(
        input_shape=(*CONFIG["image_size"], 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False

    inputs = keras.Input(shape=(*CONFIG["image_size"], 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = keras.Model(inputs, outputs)

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=CONFIG["learning_rate"]),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top3_accuracy')]
    )

    print(f"  Total parameters: {model.count_params():,}")
    return model, base_model


def get_callbacks():
    return [
        ModelCheckpoint(
            CONFIG["model_save_path"],
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.3,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        CSVLogger('training_log.csv', append=False)
    ]


def fine_tune(model, base_model, train_gen, val_gen):
    print("\n[4/5] Fine-tuning (unfreezing top layers)...")

    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=CONFIG["learning_rate"] / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top3_accuracy')]
    )

    history_ft = model.fit(
        train_gen,
        epochs=20,
        validation_data=val_gen,
        callbacks=get_callbacks(),
        verbose=1
    )
    return history_ft


def save_class_names(train_generator):
    class_names = {str(v): k for k, v in train_generator.class_indices.items()}
    with open(CONFIG["class_names_path"], 'w') as f:
        json.dump(class_names, f, indent=2)
    print(f"\n  Saved {len(class_names)} class names to {CONFIG['class_names_path']}")
    return class_names


def plot_history(history, filename="training_history.png"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('AgriLeaf CNN Training History', fontsize=14)

    axes[0].plot(history.history['accuracy'], label='Training', color='blue')
    axes[0].plot(history.history['val_accuracy'], label='Validation', color='orange')
    axes[0].set_title('Accuracy')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(history.history['loss'], label='Training', color='blue')
    axes[1].plot(history.history['val_loss'], label='Validation', color='orange')
    axes[1].set_title('Loss')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n  Training graph saved: {filename}")


def main():
    print("=" * 60)
    print("  AgriLeaf - CNN Model Training")
    print("=" * 60)

    if not os.path.exists(CONFIG["data_dir"]):
        print("""
ERROR: Dataset not found!

STEPS TO FIX:
1. Go to: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
2. Download the dataset (free Kaggle account needed)
3. Extract the zip file
4. Find the "color" folder inside
5. Create folder: model/data/plantvillage/
6. Copy all disease folders INTO model/data/plantvillage/
7. Run this script again

The structure should look like:
   model/data/plantvillage/
   ├── Tomato___Early_blight/
   ├── Tomato___Late_blight/
   ├── Rice___Brown_spot/
   └── ... (38 folders total)
        """)
        return

    train_gen, val_gen = create_data_generators()
    num_classes = train_gen.num_classes

    model, base_model = build_model(num_classes)

    print("\n[3/5] Training Phase 1 (custom layers only)...")
    history = model.fit(
        train_gen,
        epochs=CONFIG["epochs"],
        validation_data=val_gen,
        callbacks=get_callbacks(),
        verbose=1
    )

    fine_tune(model, base_model, train_gen, val_gen)

    print("\n[5/5] Saving results...")
    save_class_names(train_gen)
    plot_history(history)

    print("\n── Final Evaluation ──")
    results = model.evaluate(val_gen, verbose=0)
    print(f"  Validation Accuracy: {results[1]:.2%}")
    print(f"  Model saved to:      {CONFIG['model_save_path']}")
    print("\nTraining complete!")


if __name__ == '__main__':
    main()
```

---

Press **Ctrl+S** to save.

---

## Now you have all 7 files done. Run the project:

Open VS Code Terminal (`Ctrl+`backtick`) and type these one by one:

**Step 1 — Install packages:**
```
pip install flask flask-cors numpy Pillow
```

**Step 2 — Start the server:**
```
python run.py
```

**Step 3 — Open browser and go to:**
```
http://localhost:5000