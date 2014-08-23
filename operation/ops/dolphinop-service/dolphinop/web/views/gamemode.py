#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2013 Baina Info Inc. All rights reserved.
# Created On Apr 6, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com

import logging
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from dolphinop.web.models import gamemodedb

logger = logging.getLogger("dolphinop.web")


def show_game(request):
    try:
        game_url = request.GET.get('game')
        logger.debug(game_url)
        if len(game_url) >= 3:
            game_url = game_url[1:-1]
            logger.debug(game_url)
            cond = {'url': game_url}
            game_info = gamemodedb.get_game(cond)
            if game_info:
                return render_to_response('gamemode/gamemode.html', {'game': game_info}, context_instance=RequestContext(request))
            elif game_url:
                return redirect(game_url)
            else:
                return render_to_response('404.html')
        else:
            return render_to_response('404.html')

    except Exception, e:
        logger.exception(e)
        return render_to_response('500.html')
