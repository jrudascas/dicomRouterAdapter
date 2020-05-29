from adapters.aicoretarget import TargetAdapter
from ai_core_client.client import AiCoreClient
import numpy as np
import cv2
import png
import validators
import wget
import SimpleITK as sitk
import logging
from PIL import Image
from os import path
from cdm import END_POINT_FIND_MODEL_BY_ID, END_POINT_RUN_PREDICTION
from scu import ServiceClassUser
from cdm import SERVER_REMOTE_ADDRESS, SERVER_REMOTE_PORT, SERVER_REMOTE_AET
from utils import create_secondary_capture

logger = logging.getLogger('dicomRouterAdapter')


class AiCorePACSAdapter(TargetAdapter):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.ai_core_client = AiCoreClient(API_URL=parameters['API_URL'], API_KEY=parameters['API_KEY'])

    def find_model_id(self, model_name):
        resp = self.ai_core_client.find_model_by_name(END_POINT_FIND_MODEL_BY_ID, model_name)
        return resp

    def send_message(self, model_name, return_secondary_capture, expected_image_size, tags, metadata):
        try:
            study_id = metadata.StudyID #Getting Study ID
            image_data = metadata.pixel_array.astype(float) #Getting the DICOM image as a numpy array

            #Tranforming (Linear transformation) from DICOM pixel space to RGB pixel space
            image_sitk = sitk.IntensityWindowing(image1=sitk.GetImageFromArray(image_data), windowMinimum=image_data.min(), windowMaximum=image_data.max(), outputMinimum=0, outputMaximum=255)
            image_sitk = sitk.Cast(image_sitk, sitk.sitkUInt8)
            image_array_scaled = sitk.GetArrayFromImage(image_sitk)

            #image_scaled = (np.maximum(image_data, 0) / image_data.max()) * 255.0
            #image_scaled = np.uint8(image_scaled)

            original_shape = image_array_scaled.shape

            if image_array_scaled.shape != expected_image_size:
                image_resized = cv2.resize(image_array_scaled, expected_image_size, interpolation=cv2.INTER_AREA)
            else:
                image_resized = image_array_scaled

            resized_shape = image_resized.shape

            file_path = '/tmp/' + study_id + '.png'
            with open(file_path, 'wb') as png_file:
                w = png.Writer(resized_shape[1], resized_shape[0])
                w.write(png_file, image_resized)
            print(file_path)
            model_id = self.find_model_id(model_name)
            response_dict = self.ai_core_client.send_request(request_url=END_POINT_RUN_PREDICTION, file_path=file_path, private_id=study_id,
                                             model_id=model_id)

            if return_secondary_capture:
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
                        visual_response_image = cv2.resize(visual_response_image, (original_shape[1], original_shape[0]), interpolation=cv2.INTER_AREA)
                    #cv2.imwrite('test_image.png', visual_response_image)

                    if tags is not None:
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        scale = 0.3 * (original_shape[1] / 512)
                        thickness = 1
                        color_text = (255, 255, 255)
                        delta = 0

                        for tag in tags:
                            text = tag[0] + str(metadata[tag[1]].value)
                            textsize = cv2.getTextSize(text, font, scale, thickness)[0]
                            cv2.putText(img=visual_response_image,
                                        text=text,
                                        org=(round(original_shape[0] - textsize[0] - original_shape[0]*0.02), round(original_shape[1]*0.03 + delta)),
                                        fontFace=font,
                                        fontScale=scale,
                                        color=color_text,
                                        thickness=thickness)

                            delta = delta + textsize[1] + original_shape[1]*0.01

                    Image.fromarray(np.uint8(visual_response_image)).convert("RGBA").show()

                    secondary_capture_ds = create_secondary_capture(visual_response_image, metadata)

                    scu = ServiceClassUser(origin_aet='ROUTER_ADAPTER')
                    scu.associate(remote_address=SERVER_REMOTE_ADDRESS, remote_port=SERVER_REMOTE_PORT, remote_aet=SERVER_REMOTE_AET)

                    scu.send_c_store(secondary_capture_ds)
                    del(scu)
                except Exception as e:
                    logger.error(e.__str__())
                    pass

            return 0
        except Exception as e:
            logger.error(e.__str__())
            return 1
