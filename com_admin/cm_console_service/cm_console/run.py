import sys
sys.path.append("../")

from cm_console import settings
from cm_console.api import app
# from cm_console.middleware import TestMiddleware
import cm_console.api.commonAPI
import cm_console.api.uploadAPI
from cm_console.webfront.web_api import test


if __name__ == "__main__":
    app.run(host="0.0.0.0", processes=4, debug=settings.DEBUG)
