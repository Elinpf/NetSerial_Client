import os
import sys
import json
from src.log import logger


class config():

    # set serial port, default None
    SERIAL_DEVICE = 'COM3'

    # set baudrate, default 9600
    SERIAL_BAUDRATE = 9600

    # set telnet listening port
    TELNET_PORT = 23

    # ssh connect IP address
    SSH_SERVER_IP_ADDRESS = '127.0.0.1'

    # ssh connect Port
    SSH_SERVER_PORT = 2200

    # ssh connect username
    SSH_SERVER_USERNAME = 'bar'

    # remote user can't modify by default
    REMOTE_USER_MODIFY = False

    # ssh connect password
    SSH_SERVER_PASSWORD = 'foo'

    _SSH_SERVER_TERMINAL_PORT = None

    def __init__(self):
        # software running root dir
        self._root_dir = os.path.split(os.path.realpath(sys.argv[0]))[0]

        # github check success one time
        self._success_check_github = False

    def _get_variables(self):
        return [c for c in dir(self) if c[0] != '_']

    def _upgrade(self, custom: str):
        local_var = self._get_variables()

        json_path = os.path.join(self._root_dir, custom)
        if not os.path.exists(json_path):
            return

        with open(json_path) as f:
            j_var = json.load(f)
            logger.info('loading custom configuration....')

        for (key, val) in j_var.items():
            if not key in local_var:
                continue

            self.__dict__[key] = val

        logger.info('loading done')
        return self


conf = config()
conf._upgrade('custom.json')
