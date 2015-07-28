# coding: utf-8
import logging
from cm_console.model import Model_Dict


_LOGGER = logging.getLogger(__name__)


def classing_model(model_name):
    return Model_Dict.get(model_name) if Model_Dict.get(model_name) else None
