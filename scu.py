from pynetdicom import AE, evt, StoragePresentationContexts, VerificationPresentationContexts
from exceptions.Exceptions import AssociationException


class ServiceClassUser:

    def __init__(self, origin_aet, tls_parameters=None):
        self.ae_title = origin_aet
        self.tls_parameters = tls_parameters
        self.ae = AE(ae_title=self.ae_title)
        self.ae.requested_contexts = StoragePresentationContexts
        #self.ae.requested_contexts = VerificationPresentationContexts
        self.assoc = None

    def associate(self, remote_address, remote_port, remote_aet):
        # Associate with peer AE at IP=address and port=port (TLS is optional)
        if self.tls_parameters is not None:
            self.assoc = self.ae.associate(addr=remote_address, port=remote_port, ae_title=remote_aet,
                                           tls_args=self.tls_parameters)
        else:
            self.assoc = self.ae.associate(addr=remote_address, port=remote_port, ae_title=remote_aet)

    def send_c_store(self, dataset, priority=1):

        if self.assoc.is_established:
            status = self.assoc.send_c_store(dataset=dataset, priority=priority, originator_aet=self.ae_title)
            self.assoc.release()

            if status:
                return status
            else:
                raise AssociationException('Connection timed out, was aborted or received invalid response')
            # self.assoc.release()
        else:
            raise AssociationException('It was not possible to do a association')
