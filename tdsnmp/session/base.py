import re
import os
import importlib
import collections
from tdsnmp import exceptions, enums
from tdsnmp.utils.variables import SNMPVariable, SNMPVariableList
from tdsnmp.session import get_session


class BaseSession:

    def __init__(
        self, hostname='localhost', version=enums.DEFAULT_VERSION, community='public',
        timeout=1, retries=3, remote_port=0, local_port=0,
        security_level=enums.NO_AUTH_OR_PRIVACY, security_username='initial',
        privacy_protocol='DEFAULT', privacy_password='',
        auth_protocol='DEFAULT', auth_password='', context_engine_id='',
        security_engine_id='', context='', engine_boots=0, engine_time=0,
        our_identity='', their_identity='', their_hostname='',
        trust_cert='', use_long_names=False, use_numeric=False,
        use_sprint_value=False, use_enums=False, best_guess=0,
        retry_no_such=False, abort_on_nonexistent=False
    ):
        if ':' in hostname:
            if remote_port:
                raise exceptions.ImproperlyConfigured(
                    'hostname has a port specification '
                    'yet remote_port is defined'
                )
            hostname, remote_port = hostname.split(':')
            remote_port = int(remote_port)

        self.hostname = hostname
        self.version = version
        self.community = community
        self.timeout = timeout
        self.retries = retries
        self.local_port = local_port
        self.remote_port = remote_port
        self.security_level = security_level
        self.security_username = security_username
        self.privacy_protocol = privacy_protocol
        self.privacy_password = privacy_password
        self.auth_protocol = auth_protocol
        self.auth_password = auth_password
        self.context_engine_id = context_engine_id
        self.security_engine_id = security_engine_id
        self.context = context
        self.engine_boots = engine_boots
        self.engine_time = engine_time
        self.our_identity = our_identity
        self.their_identity = their_identity
        self.their_hostname = their_hostname
        self.trust_cert = trust_cert
        self.use_long_names = use_long_names
        self.use_numeric = use_numeric
        self.use_sprint_value = use_sprint_value
        self.use_enums = use_enums
        self.best_guess = best_guess
        self.retry_no_such = retry_no_such
        self.abort_on_nonexistent = abort_on_nonexistent

        # The following variables are required for internal use as they are
        # passed to the C interface

        #: read-only, holds the error message assoc. w/ last request
        self.error_string = ''

        #: read-only, holds the snmp_err or status of last request
        self.error_number = 0

        #: read-only, holds the snmp_err_index when appropriate
        self.error_index = 0

        self.session_ptr = self._get_session()

    @property
    def connect_hostname(self):
        """
        Join hostname and port.
        Returns:
            str: hostname with a port
        """
        if self.remote_port:
            return '{}:{}'.format(self.hostname, self.remote_port)
        return self.hostname

    @property
    def timeout_microseconds(self):
        return int(self.timeout * 1000000)

    @property
    def is_tunneled(self):
        """
        Logic to determine if a session will be tunneled.
        Returns:
            bool: True if session will be tunneled.
        """
        return re.match('^(tls|dtls|ssh)', self.hostname)

    def _get_session(self):
        if self.is_tunneled:
            return self.get_tunneled_session()
        return self.get_session_ptr()

    def get_tunneled_session(self):
        """
        Default behaviour when the session is tunneled.
        Returns:
            InterfaceSession: Interface Session
        """
        return self._get_default_tunneled_session()

    def _get_default_tunneled_session(self):
        return self.get_interface().session_tunneled(
            self.version,
            self.connect_hostname,
            self.local_port,
            self.retries,
            self.timeout_microseconds,
            self.security_username,
            self.security_level,
            self.context_engine_id,
            self.context,
            self.our_identity,
            self.their_identity,
            self.their_hostname,
            self.trust_cert
        )

    def get_session_ptr(self):
        """
        Abstract method to return a session pointer from a subclass.
        Returns:
            NotImplementedError: Should be implemented by subclasses.
        """
        raise NotImplementedError(
            "{}.get_session() must be implemented by a sub class".format(__class__.__name__)
        )

    def get_interface(self):
        """
        Method to return the interface module.
        Returns:
            tdsnmp.c.interface: Module to act as interface to net-snmp c library
        """
        # Don't attempt to import the C interface if building docs on RTD
        if not os.environ.get('READTHEDOCS', False):  # noqa
            return importlib.import_module('tdsnmp.c.interface')
        return None

    def get(self, *oids, cast_list=False):
        """
        Perform an SNMP GET operation using the prepared session to
        retrieve a particular piece of information.
        Args:
            *oids (str or tuple): At least one OID, but can be multiple. Each OID
                   may be a string representing the entire OID
                   (e.g. 'sysDescr.0') or may be a tuple containing the
                   name as its first item and index as its second
                   (e.g. ('sysDescr', 0))
            cast_list (bool): Whether to always return a list
                              as opposed to a list only when the
                              result larger than a single item

        Returns:
            list(SNMPVariable): A list of SNMPVariable objects
            SNMPVariable: A single SNMPVariable object
        """
        if len(oids) == 0:
            raise TypeError('Must give at least 1 OID')

        interface_vars = self.build_interface_vars(oids)
        interface = self.get_interface()
        interface.get(self, interface_vars)

        if self.abort_on_nonexistent:
            self.validate_results(interface_vars)

        if cast_list:
            return list(interface_vars)
        return interface_vars if len(interface_vars) > 1 else interface_vars[0]

    def bulkwalk(self, oids=('.1.3.6.1.2.1',), non_repeaters=0,
                 max_repetitions=15):
        """
        Uses SNMP BULKWALK operation using the prepared session to
        automatically retrieve multiple pieces of information in an OID
        :param non_repeaters:
        :param max_repetitions:
        :param oids: you may pass in a single item (multiple values currently
                     experimental) which may be a string representing the
                     entire OID (e.g. 'sysDescr.0') or may be a tuple
                     containing the name as its first item and index as its
                     second (e.g. ('sysDescr', 0))
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        if self.version == 1:
            raise exceptions.TDSNMPException(
                "BULKWALK is not available for SNMP version 1")

        # Build our variable bindings for the C interface
        oids = (oids,) if isinstance(oids, str) or not isinstance(oids, collections.Iterable) else oids
        interface_vars = self.build_interface_vars(oids)

        # Perform the SNMP walk using GETNEXT operations
        self.get_interface().bulkwalk(self, non_repeaters, max_repetitions, interface_vars)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            self.validate_results(interface_vars)

        # Return a list of variables
        return interface_vars

    def walk(self, oids=('.1.3.6.1.2.1',)):
        """
        Uses SNMP GETNEXT operation using the prepared session to
        automatically retrieve multiple pieces of information in an OID.
        :param oids: you may pass in a single item (multiple values currently
                     experimental) which may be a string representing the
                     entire OID (e.g. 'sysDescr.0') or may be a tuple
                     containing the name as its first item and index as its
                     second (e.g. ('sysDescr', 0))
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        # Build our variable bindings for the C interface
        oids = (oids,) if isinstance(oids, str) or not isinstance(oids, collections.Iterable) else oids
        interface_vars = self.build_interface_vars(oids)

        # Perform the SNMP walk using GETNEXT operations
        self.get_interface().walk(self, interface_vars)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            self.validate_results(interface_vars)

        # Return a list of variables
        return list(interface_vars)

    def get_bulk(self, *oids, non_repeaters=0, max_repetitions=15):
        """
        Performs a bulk SNMP GET operation using the prepared session to
        retrieve multiple pieces of information in a single packet.
        :param oids: you may pass in a list of OIDs or single item; each item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        :param non_repeaters: the number of objects that are only expected to
                              return a single GETNEXT instance, not multiple
                              instances
        :param max_repetitions: the number of objects that should be returned
                                for all the repeating OIDs
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """
        if len(oids) == 0:
            raise TypeError(
                'Must give at least 1 OID'
            )
        if self.version == 1:
            raise exceptions.TDSNMPException(
                'you cannot perform a bulk GET operation for SNMP version 1'
            )

        # Build our variable bindings for the C interface
        interface_vars = self.build_interface_vars(oids)

        self.get_interface().getbulk(self, non_repeaters, max_repetitions, interface_vars)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            self.validate_results(interface_vars)

        # Return a list of variables
        return interface_vars

    def get_next(self, *oids):
        """
        Uses an SNMP GETNEXT operation using the prepared session to
        retrieve the next variable after the chosen item.
        :param oids: you may pass in a list of OIDs or single item; each item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        :return: an SNMPVariable object containing the value that was
                 retrieved or a list of objects when you send in a list of
                 OIDs
        """
        if len(oids) == 0:
            raise TypeError(
                'Must give at least 1 OID'
            )

        # Build our variable bindings for the C interface
        interface_vars = self.build_interface_vars(oids)

        # Perform the SNMP GET operation
        self.get_interface().getnext(self, interface_vars)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            self.validate_results(interface_vars)

        # Return a list or single item depending on what was passed in
        return list(interface_vars) if len(interface_vars) > 1 else interface_vars[0]

    def set(self, oid, value, snmp_type=None):
        """
        Perform an SNMP SET operation using the prepared session.
        :param oid: the OID that you wish to set which may be a string
                    representing the entire OID (e.g. 'sysDescr.0') or may
                    be a tuple containing the name as its first item and
                    index as its second (e.g. ('sysDescr', 0))
        :param value: the value to set the OID to
        :param snmp_type: if a numeric OID is used and the object is not in
                          the parsed MIB, a type must be explicitly supplied
        :return: a boolean indicating the success of the operation
        """

        vars_list = SNMPVariableList()
        # OIDs specified as a tuple (e.g. ('sysContact', 0))
        if isinstance(oid, tuple):
            oid, oid_index = oid
            vars_list.append(SNMPVariable(oid=oid, oid_index=oid_index,
                                          value=value, snmp_type=snmp_type))
        # OIDs specefied as a string (e.g. 'sysContact.0')
        else:
            vars_list.append(SNMPVariable(oid=oid, value=value, snmp_type=snmp_type))

        # Perform the set operation and return whether or not it worked
        success = self.get_interface().set(self, vars_list)
        return bool(success)

    def set_multiple(self, oid_values):
        """
        Perform an SNMP SET operation on multiple OIDs with multiple
        values using the prepared session.
        :param oid_values: a list of tuples whereby each tuple contains a
                           (oid, value) or an (oid, value, snmp_type)
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        vars_list = SNMPVariableList()
        for oid_value in oid_values:
            if len(oid_value) == 2:
                oid, value = oid_value
                snmp_type = None
            else:
                oid, value, snmp_type = oid_value

            # OIDs specified as a tuple (e.g. ('sysContact', 0))
            if isinstance(oid, tuple):
                oid, oid_index = oid
                vars_list.append(SNMPVariable(oid=oid, oid_index=oid_index,
                                              value=value, snmp_type=snmp_type))
            # OIDs specefied as a string (e.g. 'sysContact.0')
            else:
                vars_list.append(
                    SNMPVariable(oid=oid, value=value, snmp_type=snmp_type)
                )

        # Perform the set operation and return whether or not it worked
        success = self.get_interface().set(self, vars_list)
        return bool(success)

    @staticmethod
    def build_interface_vars(oids):
        """
        Prepare variable binding list to be used
        for the C interface.
        Args:
            oids: A list of OIDS in string or tuple form

        Returns:
            list: A list of SNMPVariable objects.
        """
        ret = SNMPVariableList()
        for oid in oids:
            if isinstance(oid, tuple):
                oid, oid_index = oid
                ret.append(SNMPVariable(oid=oid, oid_index=oid_index))
            elif oid == '.':
                ret.append(SNMPVariable('iso'))
            else:
                ret.append(SNMPVariable(oid=oid))
        return ret

    @staticmethod
    def validate_results(snmp_vars):
        """
        Validates a list of SNMPVariable objects and raises any appropriate
        exceptions where necessary.

        :param snmp_vars: a variable list containing SNMPVariable objects to be
                        processed
        """

        for variable in snmp_vars:
            # Create a printable variable string for the error

            if variable.snmp_type == enums.NO_SUCH_OBJECT:
                raise exceptions.TDSNMPNoSuchObjectError(
                    'no such object {0} could be found'.format(variable)
                )
            if variable.snmp_type == enums.NO_SUCH_INSTANCE:
                raise exceptions.TDSNMPNoSuchInstanceError(
                    'no such instance {0} could be found'.format(variable)
                )


class Session(BaseSession):
    """
    Router class that proxies to specific versions of Session classes.
    """
    def __init__(self, *args, **kwargs):
        super().__setattr__('_args', args)
        super().__setattr__('_kwargs', kwargs)
        super().__setattr__('_routed_session', get_session(*self._args, **self._kwargs))

    def __getattr__(self, item):
        return getattr(self._routed_session, item)

    def __setattr__(self, key, value):
        return setattr(self._routed_session, key, value)

    # TODO: There has to be a better way to do this...
    def get_session_ptr(self): return self._routed_session.get_session_ptr()
    def get_interface(self): return self._routed_session.get_interface()
    def get(self, *args, **kwargs): return self._routed_session.get(*args, **kwargs)
    def walk(self, *args, **kwargs): return self._routed_session.walk(*args, **kwargs)
    def bulkwalk(self, *args, **kwargs): return self._routed_session.bulkwalk(*args, **kwargs)
    def get_next(self, *args, **kwargs): return self._routed_session.get_next(*args, **kwargs)
    def get_bulk(self, *args, **kwargs): return self._routed_session.get_bulk(*args, **kwargs)
    def set(self, *args, **kwargs): return self._routed_session.set(*args, **kwargs)
    def set_multiple(self, *args, **kwargs): return self._routed_session.set_multiple(*args, **kwargs)