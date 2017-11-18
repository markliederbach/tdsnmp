from __future__ import unicode_literals

import re
import string

from tdsnmp.utils import compat

OID_INDEX_RE = re.compile(
    r'''(
            \.?\d+(?:\.\d+)*              # numeric OID
            |                             # or
            (?:\w+(?:[-:]*\w+)+)          # regular OID
            |                             # or
            (?:\.?iso(?:\.\w+[-:]*\w+)+)  # fully qualified OID
        )
        \.?(.*)                           # OID index
     ''',
    re.VERBOSE
)


def strip_non_printable(value):
    """
    Removes any non-printable characters and adds an indicator to the string
    when binary characters are found.

    :param value: the value that you wish to strip
    """
    if value is None:
        return None

    # Filter all non-printable characters
    # (note that we must use join to account for the fact that Python 3
    # returns a generator)
    printable_value = ''.join(
        filter(lambda c: c in string.printable, value)
    )

    if printable_value != value:
        if printable_value:
            printable_value += ' '
        printable_value += '(contains binary)'

    return printable_value


def tostr(value):
    """
    Converts any variable to a string or returns None if the variable
    contained None to begin with; this function currently supports None,
    unicode strings, byte strings and numbers.

    :param value: the value you wish to convert to a string
    """

    if value is None:
        return None
    elif isinstance(value, compat.text_type):
        return value
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return compat.iso_8859_1(value)


def normalize_oid(oid, oid_index=None):
    """
    Ensures that the index is set correctly given an OID definition.

    :param oid: the OID to normalize
    :param oid_index: the OID index to normalize
    """
    # This regular expression is used to extract the index from an OID

    # Determine the OID index from the OID if not specified
    if oid_index is None and oid is not None:
        # We attempt to extract the index from an OID (e.g. sysDescr.0
        # or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
        match = OID_INDEX_RE.match(oid)
        if match:
            oid, oid_index = match.group(1, 2)

    return oid, oid_index
