import logging
from logging.config import dictConfig

import yaml

with open("logging.yaml") as log_conf_file:
    log_conf = yaml.safe_load(log_conf_file)
    dictConfig(log_conf)

log = logging.getLogger("pyrandall")
