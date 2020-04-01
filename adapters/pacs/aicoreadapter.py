from adapters.aicoretarget import TargetAdapter
from ai_core_client.client import AiCoreClient
import numpy as np
import cv2
import png
import validators
import wget
import json
from PIL import Image
from os import path
from cdm import END_POINT_FIND_MODEL_BY_ID, END_POINT_RUN_PREDICTION
from scu import ServiceClassUser
from cdm import SERVER_REMOTE_ADDRESS, SERVER_REMOTE_PORT, SERVER_REMOTE_AET
from utils import create_secondary_capture


class AiCorePACSAdapter(TargetAdapter):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.ai_core_client = AiCoreClient(API_URL=parameters['API_URL'], API_KEY=parameters['API_KEY'])

    def find_model_id(self, model_name):
        resp = self.ai_core_client.find_model_by_name(END_POINT_FIND_MODEL_BY_ID, model_name)
        return resp

    def send_message(self, model_name, metadata):
        try:
            study_id = metadata.StudyID
            image = metadata.pixel_array.astype(float)
            image_scaled = (np.maximum(image, 0) / image.max()) * 255.0
            image_scaled = np.uint8(image_scaled)

            original_shape = image_scaled.shape

            if image_scaled != (1024, 1024):
                image_resized = cv2.resize(image_scaled, (1024, 1024), interpolation=cv2.INTER_AREA)
            else:
                image_resized = image_scaled

            shape = image_resized.shape

            file_path = '/tmp/' + study_id + '.png'
            with open(file_path, 'wb') as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, image_resized)

            model_id = self.find_model_id(model_name)
            response_dict = self.ai_core_client.send_request(request_url=END_POINT_RUN_PREDICTION, file_path=file_path, private_id=study_id,
                                             model_id=model_id)

            try:
                visual_reponse_path = response_dict['data']['predictions'][0]['visual_prediction']
                if validators.url(visual_reponse_path):
                    local_image_filename = wget.download(visual_reponse_path)
                    visual_response_image = Image.open(local_image_filename)
                elif path.exists(visual_reponse_path):
                    visual_response_image = Image.open(visual_reponse_path)
                else:
                    raise Exception('url_path wrong')

                visual_response_image = visual_response_image.convert('RGB')
                visual_response_image = np.asarray(visual_response_image)
                if visual_response_image.shape != original_shape:
                    visual_response_image = cv2.resize(visual_response_image, original_shape, interpolation=cv2.INTER_AREA)

                secondary_capture_ds = create_secondary_capture(visual_response_image, metadata)

                scu = ServiceClassUser(origin_aet='ROUTER_ADAPTER')
                scu.associate(remote_address=SERVER_REMOTE_ADDRESS, remote_port=SERVER_REMOTE_PORT, remote_aet=SERVER_REMOTE_AET)

                scu.send_c_store(secondary_capture_ds)
                del(scu)
            except Exception as e:
                print('Error: ', e.__str__())
                #Revisar que hacer en caso de una excepcion
                pass

            return 0
        except Exception as e:
            print(e.__str__())
            return -1