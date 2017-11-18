from tdsnmp.session.base import BaseSession

def test_build_varlist_000():
    varlist = BaseSession.build_interface_vars(['sysContact.0'])
    assert len(varlist) == 1
    assert varlist[0].oid == 'sysContact'
    assert varlist[0].oid_index == '0'
    assert varlist[0].value is None
    assert varlist[0].snmp_type is None


def test_build_varlist_001_list():
    varlist = BaseSession.build_interface_vars(['sysContact.0', ('sysDescr', '0')])
    assert len(varlist) == 2
    assert varlist[0].oid == 'sysContact'
    assert varlist[0].oid_index == '0'
    assert varlist[0].value is None
    assert varlist[0].snmp_type is None
    assert varlist[1].oid == 'sysDescr'
    assert varlist[1].oid_index == '0'
    assert varlist[1].value is None
    assert varlist[1].snmp_type is None