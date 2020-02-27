class TargetAdapter:

    def __init__(self, parameters):
        self.parameters = parameters

    def send_message(self, model, metadata):
        raise NotImplementedError('Method {0} is not implemented'.format('send_message'))