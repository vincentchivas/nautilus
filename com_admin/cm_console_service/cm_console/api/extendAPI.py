from cm_console.api import app
from armory.marine.access_control import access_control, exception_handler
from armory.marine.json_rsp import json_response_ok


@app.route('/<appname>/<modelname>/testupload', methods=['GET', ])
@exception_handler
@access_control
def testapi(appname, modelname):
    data = {'app': appname, 'mod': modelname}
    return json_response_ok(data, 'test it')
