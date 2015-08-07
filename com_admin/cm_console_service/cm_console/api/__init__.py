# -*- coding: utf-8 -*-
from pylon.frame import App, request
from cm_console.settings import MONGO_CONFIG, TMPL_FOLDER


app = App(__name__, template_folder=TMPL_FOLDER, static_folder='static')
app.config['mongodb_conf'] = MONGO_CONFIG
