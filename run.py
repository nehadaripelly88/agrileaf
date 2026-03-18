import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

# Limit TensorFlow memory so it doesn't crash on low RAM
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("  AgriLeaf - AI Leaf Health Analyzer")
    print("  Open: http://localhost:5000 in your browser")
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000)