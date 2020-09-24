__all__ = ['MonitoringManager']

import logging

from datetime import datetime

from spaceone.core import config
from spaceone.core.error import *
from spaceone.core.manager import BaseManager
from spaceone.monitoring.model.log_response_model import LogResponseModel

_LOGGER = logging.getLogger(__name__)


class MonitoringManager(BaseManager):

    def __init__(self, transaction):
        super().__init__(transaction)

    @staticmethod
    def make_log_response(log_info):
        response_model = LogResponseModel({
            'result': log_info
        })
        response_model.validate()
        return response_model.to_primitive()
