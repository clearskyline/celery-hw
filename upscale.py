import cv2
from cv2 import dnn_superres


def upscale_func(input_path: str, output_path: str, model_path: str = 'EDSR_x2.pb'):

    scaler = dnn_superres.DnnSuperResImpl_create()
    scaler.readModel(model_path)
    scaler.setModel("edsr", 2)
    image = cv2.imread(input_path)
    result = scaler.upsample(image)
    cv2.imwrite(output_path, result)
    return output_path


# print(upscale_func('lama_300px.png', 'lama_600px.png'))
