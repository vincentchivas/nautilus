PROJECT_NAME = 'dolphin-operation'

VERSION_CONTROL = "dolphindeploy.git"

# The Project Role Alias table.
ROLE_ALIAS = {
    'dolphinop-db' : 'Dolphin Operation DB',
    'dolphinop-service' : 'Dolphin Operation Service',
    'dolphinop-webfront' : 'Dolphin Operation WebFront',
    'dolphinopadmin-service' : 'Dolphin Operation Admin Service',
    'dolphinopadmin-webfront' : 'Dolphin Operation Admin WebFront',
    'dolphinopstatic-service' : 'Dolphin Operation Static Service',
    'dolphinopstatic-webfront' : 'Dolphin Operation Static WebFront',
    'web' : 'Dolphin Operation Static Web',
}

# The project app table
ROLE_APPS_TABLE = {
    'Dolphin Operation DB' : ['dolphinop-db'],
    'Dolphin Operation Service' : ['dolphinop-service'],
    'Dolphin Operation WebFront' : ['dolphinop-webfront'],
    'Dolphin Operation Admin Service' : ['dolphinopadmin-service'],
    'Dolphin Operation Admin WebFront' : ['dolphinopadmin-webfront'],
    'Dolphin Operation Static Service' : ['dolphinopstatic-service'],
    'Dolphin Operation Static WebFront' : ['dolphinopstatic-webfront'],
    'Dolphin Operation Static Web' : ['web'],
}

# Extra extension to search
EXTRA_EXT_PATTERN = (
        '.conf',
        '.cfg',
        '.xml',
        '.csv',
        '.nginx'
        )

# Extra file name to search
EXTRA_CONF_NAME_PATTERN = (
        'settings2.py',
        'version'
        )

# Disuse compressor
BUILD_HANDLER_CONFIG =(
        'dolphindeploy.handlers.ConfigurationFileHandler',
        )
