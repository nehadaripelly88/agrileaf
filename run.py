import sys
import os
 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
 
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
 
from app import app
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    print("=" * 60)
    print("  AgriLeaf - AI Leaf Health Analyzer")
    print(f"  Running on port {port}")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)