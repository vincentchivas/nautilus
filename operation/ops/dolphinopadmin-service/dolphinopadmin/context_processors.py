from django.conf import settings  # import the settings file


def admin_env(context):
    # return the value you want as a dictionnary. you may add multiple values
    # in there.
    return {'ENVS': settings.ENV_CONFIGURATION.keys()}
