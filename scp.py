from pynetdicom import AE, evt, StoragePresentationContexts, VerificationPresentationContexts, \
    QueryRetrievePresentationContexts, RelevantPatientInformationPresentationContexts
from adapters.pacs.aicoreadapter import AiCorePACSAdapter
from cdm import MODELS_TO_SEND, API_KEY, API_URL, SERVER_HOST_ADDRESS, SERVER_HOST_AET, SERVER_HOST_PORT
from utils import check_filter
import numpy as np
import logging

logging.basicConfig(format='%(asctime)s - %(filename)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s', filename='log.log', level=logging.INFO)
logger = logging.getLogger('dicomRouterAdapter')


class ServiceClassProvider(object):

    def __init__(self, aet, address, port):
        self.ae_title = aet
        self.address = address
        self.port = port
        self.ae = AE(ae_title=self.ae_title)
        self.ae.supported_contexts = StoragePresentationContexts
        self.ae.supported_contexts = VerificationPresentationContexts
        self.ae.supported_contexts = QueryRetrievePresentationContexts
        self.ae.supported_contexts = RelevantPatientInformationPresentationContexts

        self.adapter = AiCorePACSAdapter({'API_URL': API_URL, 'API_KEY': API_KEY})

    def start_server(self):
        def handle_store(event):
            try:
                print('Message received')
                ds = event.dataset
                ds.file_meta = event.file_meta

                if hasattr(ds, 'PatientName'):
                    print('Patient --> ', ds.PatientName)
                    logger.info('Patient --> ' + ds.PatientName.given_name + ' ' + ds.PatientName.family_name)


                if ds.SOPClassUID == '1.2.840.10008.5.1.4.1.1.7':
                    logger.error('Message received is a Secondary Capture')
                    raise Exception('Message received is a Secondary Capture')

                '''
                if not hasattr(ds, 'BodyPartExamined'):
                    raise Exception('Dataset does not has BodyPartExamined attribute')
                elif not hasattr(ds, 'Modality'):
                    raise Exception('Dataset does not has Modality attribute')
                elif not hasattr(ds, 'SeriesDescription'):
                    if hasattr(ds, 'StudyDescription'):
                        ds.SeriesDescription = ds.StudyDescription
                    else:
                        raise Exception('Dataset does not has neither SeriesDescription and StudyDescription attributes')
                
                if ds.BodyPartExamined.upper() in ['CHEST', 'TORAX', 'BREAST'] and ds.Modality.upper() in ['CR'] and 'PA' in ds.SeriesDescription.upper():  # Esto se ve feo, mejorar otro día.
                    print('Starting processing...')
                    try:
                        status = {}
                        for model_name, return_secondary_capture, filter in MODELS_TO_SEND:
                            
                            
                            
                            
                            print('Sending to ', model_name, ' model...')
                            status[model_name] = self.adapter.send_message(model_name=model_name, return_secondary_capture=return_secondary_capture, metadata=ds)
                        if not np.array(list(status.values())).any():
                            print("Message processed successfully")

                            return 0x0000
                        else:
                            print("Message processed with erros, Details: ")
                            for k, v in status.items():
                                print(k, ' --> ', 'Successfully' if v == 0 else 'With errors')
                            return 0x0000
                    except Exception as e:
                        print('Message discarded. Details: ', e.__str__())
                        return 0x0000

                else:
                    print("Message discarded")
                    return 0x0000
                '''

                try:
                    status = {}
                    for model_name, return_secondary_capture, expected_image_size, filter, tags in MODELS_TO_SEND:
                        logger.info('Checking filter for ' + model_name + ' model...')
                        flat, error_message = check_filter(filter, ds)
                        if flat:
                            print('Sending to ', model_name, ' model...')
                            logger.info('Sending to ' + model_name + ' model...')

                            status[model_name] = self.adapter.send_message(model_name=model_name,
                                                                           return_secondary_capture=return_secondary_capture,
                                                                           expected_image_size=expected_image_size,
                                                                           tags = tags,
                                                                           metadata=ds)
                        else:
                            print('Model --> ', model_name, ' can not used. Details: ', error_message)
                            logger.info('Model --> ' + model_name + ' can not used. Details: ' + error_message)


                    if not np.array(list(status.values())).any():
                        print("Message processed successfully")
                        logger.info("Message processed successfully")

                        return 0x0000
                    else:
                        print("Message processed with erros, Details: ")
                        logger.error("Message processed with erros, Details: ")
                        for k, v in status.items():
                            print(k, ' --> ', 'Successfully' if v == 0 else 'With errors')
                        return 0x0000
                except Exception as e:
                    print('Message discarded. Details: ', e.__str__())
                    logger.error('Message discarded. Details: ' + e.__str__())
                    return 0x0000

            except Exception as e:
                print("Fatal error: ", e.__str__())
                print("Message discarded")
                logger.error("Fatal error: " + e.__str__())
                return 0x0000

        handlers = [(evt.EVT_C_STORE, handle_store), (evt.EVT_C_MOVE, handle_store)]
        print('Server started successfully')
        scp = self.ae.start_server((self.address, self.port), block=True, evt_handlers=handlers)
        return scp


service = ServiceClassProvider(aet=SERVER_HOST_AET, address=SERVER_HOST_ADDRESS, port=SERVER_HOST_PORT)
scp = service.start_server()
