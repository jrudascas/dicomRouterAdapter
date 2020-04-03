from pynetdicom import AE, evt, StoragePresentationContexts, VerificationPresentationContexts, QueryRetrievePresentationContexts, RelevantPatientInformationPresentationContexts
from adapters.pacs.aicoreadapter import AiCorePACSAdapter
from cdm import CHEST_MODEL, API_KEY, API_URL, SERVER_HOST_ADDRESS, SERVER_HOST_AET, SERVER_HOST_PORT


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

        self.adapter = AiCorePACSAdapter({'API_URL':API_URL, 'API_KEY':API_KEY})

    def start_server(self):
        def handle_store(event):
            try:
                print('Message received')
                ds = event.dataset

                if hasattr(ds, 'PatientName'):
                    print('Patient --> ', ds.PatientName)

                if not (hasattr(ds, 'BodyPartExamined') and hasattr(ds, 'Modality') and hasattr(ds, 'SeriesDescription')):
                    raise Exception('Any of mandatory attribute does not exist in the dataset')

                if ds.BodyPartExamined == 'CHEST' and (ds.Modality == 'CR' or ds.Modality == 'DX') and 'PA' in ds.SeriesDescription:  # Esto se ve feo, mejorar otro día.
                    print('Starting processing...')
                    try:
                        ds.file_meta = event.file_meta
                        status = self.adapter.send_message(model_name=CHEST_MODEL, metadata=ds)
                        if status == 0:
                            print("Message processed successfully")
                            return 0x0000
                        else:
                            print("Message processed with erros")
                            return 0x0000
                    except Exception as e:
                        print('Message discarded. Details: ', e.__str__())
                        return 0x0000

                else:
                    print("Message discarded")
                    return 0x0000
            except Exception as e:
                print("Fatal error: ", e.__str__())
                print("Message discarded")

        handlers = [(evt.EVT_C_STORE, handle_store), (evt.EVT_C_MOVE, handle_store)]
        print('Server started successfully')
        scp = self.ae.start_server((self.address, self.port), block=True, evt_handlers=handlers)
        return scp


service = ServiceClassProvider(aet=SERVER_HOST_AET, address=SERVER_HOST_ADDRESS, port=SERVER_HOST_PORT)
scp = service.start_server()
