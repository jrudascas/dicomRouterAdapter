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
            print('Message received')
            ds = event.dataset

            if ds.BodyPartExamined == 'CHEST' and ds.Modality == 'CR' and 'PA' in ds.SeriesDescription:  # Esto se ve feo, mejorar otro día.
                ds.file_meta = event.file_meta
                status = self.adapter.send_message(model_name=CHEST_MODEL, metadata={ds.StudyID: ds})
                if status == 0:
                    print("Message processed successfully")
                    return 0x0000
            else:
                print("Message discarded")
                return 0x0000

        handlers = [(evt.EVT_C_STORE, handle_store), (evt.EVT_C_MOVE, handle_store)]
        print('Server started successfully')
        scp = self.ae.start_server((self.address, self.port), block=True, evt_handlers=handlers)
        return scp


service = ServiceClassProvider(aet=SERVER_HOST_AET, address=SERVER_HOST_ADDRESS, port=SERVER_HOST_PORT)
scp = service.start_server()
