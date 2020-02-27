from pynetdicom import AE, evt, StoragePresentationContexts
from adapters.pacs.aicoreadapter import AiCorePACSAdapter
from cdm import CHEST_MODEL, API_KEY, API_URL


class ServiceClassProvider(object):

    def __init__(self, aet, address, port):
        self.ae_title = aet
        self.address = address
        self.port = port
        self.ae = AE(ae_title=self.ae_title)
        self.ae.supported_contexts = StoragePresentationContexts
        self.adapter = AiCorePACSAdapter({'API_URL':API_URL, 'API_KEY':API_KEY})

    def start_server(self):
        def handle_store(event):
            print('Llegó mensaje')
            ds = event.dataset

            if ds.BodyPartExamined == 'CHEST' and ds.Modality == 'CR' and 'PA' in ds.SeriesDescription:  # Esto se ve feo, mejorar otro día.
                ds.file_meta = event.file_meta
                self.adapter.send_message(model_name=CHEST_MODEL, metadata={ds.StudyID: ds})

            print('Fin fin fin')

            return 0x0000

        handlers = [(evt.EVT_C_STORE, handle_store)]
        scp = self.ae.start_server((self.address, self.port), block=True, evt_handlers=handlers)
        print('Server started successfully')
        return scp


service = ServiceClassProvider(aet='DAEMON', address='127.0.0.1', port=11112)
scp = service.start_server()
