from adapters.aicoretarget import TargetAdapter
from ai_core_client.client import AiCoreClient
import numpy as np
import cv2
import png
from cdm import END_POINT_FIND_MODEL_BY_ID, END_POINT_RUN_PREDICTION


class AiCorePACSAdapter(TargetAdapter):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.ai_core_client = AiCoreClient(API_URL=parameters['API_URL'], API_KEY=parameters['API_KEY'])

    def find_model_id(self, model_name):
        resp = self.ai_core_client.find_model_by_name(END_POINT_FIND_MODEL_BY_ID, model_name)
        return resp

    def send_message(self, model_name, metadata):
        try:
            study_id = list(metadata.keys())[0]
            image = list(metadata.values())[0].pixel_array.astype(float)
            image_scaled = (np.maximum(image, 0) / image.max()) * 255.0
            image_scaled = np.uint8(image_scaled)

            image_resized = cv2.resize(image_scaled, (1024, 1024), interpolation=cv2.INTER_AREA)
            shape = image_resized.shape

            file_path = '/tmp/' + study_id + '.png'
            with open(file_path, 'wb') as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, image_resized)

            model_id = self.find_model_id(model_name)
            self.ai_core_client.send_request(request_url=END_POINT_RUN_PREDICTION, file_path=file_path, private_id=study_id,
                                             model_id=model_id)
            return 0
        except Exception as e:
            print(e.__str__())
            return -1