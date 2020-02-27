class BaseExceptionPrototype(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            {}
            return '{0}, {1}'.format(self.__class__.__name__, self.message)
        else:
            return '{0} has been raised'.format(self.__class__.__name__ )


class AssociationException(BaseExceptionPrototype):
    pass