import cv2
import requests
import json
import json


class AiCoreClient:

    def __init__(self, API_KEY, API_URL):
        self.apikey = API_KEY
        self.api_url = API_URL
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Token ' + self.apikey}

    def find_model_by_name(self, request_url, model_name):
        resp = requests.get(self.api_url + request_url + model_name, headers=self.headers)
        d = json.loads(resp.content)

        return d['results'][0]['uuid']

    def send_request(self, request_url, file_path, private_id, model_id):

        # Body
        payload = {'model': model_id,
                   'images': [{'private_id': private_id, 'url_path': file_path}]}
        # convert dict to json by json.dumps() for body data.

        resp = requests.post(self.api_url + request_url, data=json.dumps(payload, indent=4), headers=self.headers)
        json_response = json.loads(resp.content)
        if json_response['status'] != 'OK':
            raise Exception('AI Core service responded with errors. Details: ', json_response)

        return json_response
