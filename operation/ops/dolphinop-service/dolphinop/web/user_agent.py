'''
Copyright (c) 2011 Baina Info Inc. All rights reversed.
@Author: Wenyuan Wu
@Date: 2011-12-01
'''

import re

_DEFAULT_QUERY_VALUE = "unknown"

# iPhone/iPad User_Agent:
#  [iPhone/iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us]
_IPHONE_REGEX = re.compile(r'\(iPhone; [U|N|I]; [^;]+; [^\)]+\)')
_IPAD_REGEX = re.compile(r'\(iPad; [U|N|I]; [^;]+; [^\)]+\)')

# Android User_Agent:
#  [Linux; U; Android 2.1; en-us; Nexus One Build/ERD62]
_ANDROID_REGEX = re.compile(
    r'\(Linux; [U|N|I]; Android [^;]+; [^;]+; [^\)]+\)')

_REPLACE_REGEX = re.compile(r'\(|\)')


def _get_info_from_agent(agent):
    if len(_IPHONE_REGEX.findall(agent)) > 0:
        agent = _REPLACE_REGEX.sub('', _IPHONE_REGEX.findall(agent)[0])
        agent_infos = agent.split("; ")
        os, locale = agent_infos[0], agent_infos[3]
    elif len(_IPAD_REGEX.findall(agent)) > 0:
        agent = _REPLACE_REGEX.sub('', _IPAD_REGEX.findall(agent)[0])
        agent_infos = agent.split("; ")
        os, locale = agent_infos[0], agent_infos[3]
    elif len(_ANDROID_REGEX.findall(agent)) > 0:
        agent = _REPLACE_REGEX.sub('', _ANDROID_REGEX.findall(agent)[0])
        agent_infos = agent.split("; ")
        os, locale = agent_infos[2], agent_infos[3]
    else:
        os, locale = "PC", _DEFAULT_QUERY_VALUE

    return os, locale


def package_request_infos(func):
    # get os and language from request if exist, or get from user_agent
    def package_infos(*args, **kwargs):
        request = args[0]
        os = request.GET.get('os', None)
        locale = request.GET.get('l', None)
        if not os or not locale:
            agent = request.META.get('HTTP_USER_AGENT', None)
            temp_request = request.GET.copy()
            if agent:
                detected_os, detected_locale = _get_info_from_agent(agent)
                if not os:
                    temp_request["os"] = detected_os if detected_os \
                        else _DEFAULT_QUERY_VALUE
                if not locale:
                    temp_request["l"] = detected_locale if detected_locale \
                        else _DEFAULT_QUERY_VALUE
            else:
                temp_request["os"] = _DEFAULT_QUERY_VALUE
                temp_request["l"] = _DEFAULT_QUERY_VALUE
            request.GET = temp_request
        return func(*args, **kwargs)
    return package_infos
