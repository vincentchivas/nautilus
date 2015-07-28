from armory.tank.mongo import ArmoryMongo
from cm_console.settings import MODELS
from cm_console.model.base import ModelBase
from cm_console.api import app

Model_Dict = {}
ArmoryMongo.init_app(app)

for key in MODELS:
    attrs = MODELS[key]
    Model_Dict[key] = type(str(key), (ModelBase,), attrs)
