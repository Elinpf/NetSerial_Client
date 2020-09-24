import re
import time

import git
import requests

from src.banner import banner
from src.config import conf
from src.log import logger
from src.variable import gvar
from src.tools import wait_time


def calc_version(ver):
    r = re.match(r'v(\d+?)\.(\d+?)\.(\d+)', ver)
    if len(r.regs) != 4:
        logger.error("The version format is incorrect")
        return False

    _ = int(r.group(1))*10000 + int(r.group(2))*100 + int(r.group(3))
    return _


class Update():
    def __init__(self):
        pass

    def get_new_version(self):
        try:
            resp = requests.get(url=banner.REPOSITORY_API_ADDRESS)
        except Exception as e:
            logger.error("network anomaly")
            return False

        if resp.status_code != 200:
            logger.info("unable to get a valid page")
            return False

        _ = str(resp.content.decode())

        new_ver = re.search(r'"name":"(.*?)",', _).group(1)
        if not new_ver:
            logger.info("unable to get valid version information")
            return False

        return new_ver

    def check_version(self):
        new_ver = self.get_new_version()
        if not new_ver:
            return

        logger.info("remote repository recent version is: %s" % new_ver)
        logger.info("the running version is %s" % banner.VERSION)

        new_ver_int = calc_version(new_ver)
        run_ver_int = calc_version(banner.VERSION)
        if not(new_ver_int and run_ver_int):  # check if format is bad
            return False

        if (new_ver_int > run_ver_int):  # check if recent version is new
            return True
        else:
            logger.info("don't need update")
            return False

    def pull(self):
        g = git.cmd.Git(conf._root_dir)
        return g.pull()

    def run(self):
        while not conf._success_check_github:
            if self.check_version():
                conf._success_check_github = True

            wait_time(10*60)  # check every 10min

    def thread_run(self):
        gvar.thread.function(target=self.run, name="check update")
        logger.info('thread start -> Update.run()')
