

class TDSNMPException(Exception):
    pass


class ImproperlyConfigured(TDSNMPException):
    pass


class UnsupportedSNMPVersion(TDSNMPException):
    pass


class TDSNMPNoSuchObjectError(TDSNMPException):
    pass


class TDSNMPConnectionError(TDSNMPException):
    pass


class TDSNMPNoSuchInstanceError(TDSNMPException):
    pass


class TDSNMPTimeoutError(TDSNMPException):
    pass


class TDSNMPNoSuchNameError(TDSNMPException):
    pass


class TDSNMPUnknownObjectIDError(TDSNMPException):
    pass


class TDSNMPUndeterminedTypeError(TDSNMPException):
    pass
