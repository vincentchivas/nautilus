from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils.respcode import PARAM_REQUIRED, DATA_ERROR
from provisionadmin.model.i18n import LocalizationModules
from provisionadmin.decorator import check_session, exception_handler
# import all_json


@exception_handler()
@check_session
def get_modules(request):
    if request.method == 'GET':
        data = request.GET

        appname = data.get("appname")
        if not appname:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter 'appname' invalid")
        appversion = data.get("appversion")
        if not appversion:
            return json_response_error(
                PARAM_REQUIRED, msg="parameter 'appversion' invalid")
        # name = data.get("name")

        modules = LocalizationModules.get_by_app(appname, appversion)
        if not modules:
            return json_response_error(DATA_ERROR, msg='not found modules')

        return json_response_ok(modules)
