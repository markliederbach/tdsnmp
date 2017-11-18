from tdsnmp.session.base import BaseSession


class SNMPv3Session(BaseSession):

    def get_session_ptr(self):
        return self.get_interface().session_v3(
                self.version,
                self.connect_hostname,
                self.local_port,
                self.retries,
                self.timeout_microseconds,
                self.security_username,
                self.security_level,
                self.security_engine_id,
                self.context_engine_id,
                self.context,
                self.auth_protocol,
                self.auth_password,
                self.privacy_protocol,
                self.privacy_password,
                self.engine_boots,
                self.engine_time
        )
