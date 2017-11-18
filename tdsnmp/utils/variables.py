from tdsnmp.utils import compat, snmp_strings


class SNMPVariable:
    """
    An SNMP variable binding which is used to represent a piece of
    information being retrieved via SNMP.

    :param oid: the OID being manipulated
    :param oid_index: the index of the OID
    :param value: the OID value
    :param snmp_type: the snmp_type of data contained in val (please see
                      http://www.net-snmp.org/wiki/index.php/TUT:snmpset#Data_Types
                      for further information); in the case that an object
                      or instance is not found, the type will be set to
                      NOSUCHOBJECT and NOSUCHINSTANCE respectively
    """

    def __init__(self, oid=None, oid_index=None, value=None, snmp_type=None):
        self.oid, self.oid_index = snmp_strings.normalize_oid(oid, oid_index)
        self.value = value
        self.snmp_type = snmp_type

    def __repr__(self):
        printable_value = snmp_strings.strip_non_printable(self.value)
        return (
            "<{0} value={1} (oid={2}, oid_index={3}, snmp_type={4})>".format(
                self.__class__.__name__,
                compat.unicode_repr(printable_value), compat.unicode_repr(self.oid),
                compat.unicode_repr(self.oid_index), compat.unicode_repr(self.snmp_type)
            )
        )

    def __str__(self):
        printable_value = snmp_strings.strip_non_printable(self.value)
        return "<oid={}{}{}{}>".format(
            compat.unicode_repr(self.oid),
            ", oid_index={}".format(compat.unicode_repr(self.oid_index)) if self.oid_index else "",
            ", value={}".format(compat.unicode_repr(printable_value)) if printable_value else "",
            ", snmp_type={}".format(compat.unicode_repr(self.snmp_type)) if self.snmp_type else "",
        )

    def __setattr__(self, name, value):
        self.__dict__[name] = snmp_strings.tostr(value)


class SNMPVariableList(list):
    """
    An slight variation of a list which is used internally by the
    Net-SNMP C interface.
    """

    @property
    def varbinds(self):
        return self