import tensorflow
from tensorflow.python.client import device_lib
import torch
import cv2
import sys


tf = tensorflow.compat.v1
sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
print(device_lib.list_local_devices())
print(tf.__version__)
print("opencv version : ", cv2.__version__)
print("opencv cuda count : ", cv2.cuda.getCudaEnabledDeviceCount())
print(cv2.cuda.printCudaDeviceInfo(0))
print(sys.path)

gpus = tf.config.experimental.list_physical_devices("GPU")
if gpus:
    try:
        tf.config.experimental.set_visible_devices(gpus[0], "GPU")
    except RuntimeError as e:
        print(e)

print(torch.__version__)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"gpu {device} is available in torch")
