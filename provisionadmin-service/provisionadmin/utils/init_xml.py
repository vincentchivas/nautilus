import logging
from provisionadmin.model.i18n import LocalizationApps
from provisionadmin.service.utils.adapter import init_adpter_Ex

logger = logging.getLogger("init_xml_file")


def init_xml_file():
    logger.info("start to update_apps")
    info = LocalizationApps.update_apps()
    appname = info.get("appname")
    appversion = info.get("appversion")
    md5 = info.get("md5")
    logger.info("start to download %s xml file", appname)
    xml_path = LocalizationApps.get_xml_file(appname, appversion, md5)
    logger.info("start to unzip %s xml file", appname)
    package_name, version_name = init_adpter_Ex(appname, appversion, xml_path)
    return package_name, version_name
