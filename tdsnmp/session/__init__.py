import importlib
from tdsnmp import enums, exceptions

SESSION_VERSION_MAP = {
    1: ('tdsnmp.session.versions.v1', 'SNMPv1Session'),
    2: ('tdsnmp.session.versions.v2', 'SNMPv2Session'),
    3: ('tdsnmp.session.versions.v3', 'SNMPv3Session'),
}


def get_session(*args, **kwargs):
    """
    Route session creation here based on the version required.
    :return:
        BaseSession: A subclass of BaseSession will be returned.
    """
    if len(args) > 1:
        version = int(args[1])
    else:
        version = int(kwargs.get('version', enums.DEFAULT_VERSION))
    try:
        session = importlib.import_module(SESSION_VERSION_MAP[version][0])
        return getattr(session, SESSION_VERSION_MAP[version][1])(*args, **kwargs)
    except KeyError:
        raise exceptions.UnsupportedSNMPVersion(
            'Unsupported Version of SNMP. '
            'Must use one of versions {}'.format(list(SESSION_VERSION_MAP.keys()))
        )
