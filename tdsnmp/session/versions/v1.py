from tdsnmp.session.base import BaseSession

class SNMPv1Session(BaseSession):

    def get_session_ptr(self):
        return self.get_interface().session(
            self.version,
            self.community,
            self.connect_hostname,
            self.local_port,
            self.retries,
            self.timeout_microseconds,
        )
