#import torch
#print(torch.__version__)           # Должно быть `2.3.0+cu121` или новее
#print(torch.cuda.is_available())   # Должно быть `True`
#print(torch.cuda.get_device_name(0))  # Проверьте название GPU

import tensorflow as tf
print("Версия TensorFlow:", tf.__version__)
print("Доступные устройства:", tf.config.list_physical_devices())
