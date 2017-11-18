import logging
import pytest
import tdsnmp

snmp_logger = logging.getLogger('tdsnmp.c.interface')
snmp_logger.disabled = True

@pytest.fixture
def sess_v1_args():
    return {
        'version': 1,
        'hostname': 'localhost',
        'remote_port': 11161,  # TODO: This assumes snmpd running on this port...
        'community': 'public',
    }

@pytest.fixture
def sess_v2_args():
    return {
        'version': 2,
        'hostname': 'localhost',
        'remote_port': 11161,
        'community': 'public'
    }


@pytest.fixture
def sess_v3_args():
    return {
        'version': 3,
        'hostname': 'localhost',
        'remote_port': 11161,
        'security_level': tdsnmp.AUTH_WITH_PRIVACY,
        'security_username': 'initial',
        'privacy_password': 'priv_pass',
        'auth_password': 'auth_pass'
    }


@pytest.fixture
def sess_v1():
    return tdsnmp.Session(**sess_v1_args())


@pytest.fixture
def sess_v2():
    return tdsnmp.Session(**sess_v2_args())


@pytest.fixture
def sess_v3():
    return tdsnmp.Session(**sess_v3_args())