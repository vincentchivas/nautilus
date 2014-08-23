# -*- coding: utf-8 -*-
import re
import simplejson
import urllib2
import time
import logging
from bs4 import BeautifulSoup
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dolphinop.settings'

from dolphinop.service.models import searchdb, contentdb

logger = logging.getLogger('dolphinop.service')

MAX_LENGTH = 17
WORD_MAX = 8
_TIME_OUT = 30

DOMAIN = {
    'web': 'http://top.baidu.com',
    'story': 'http://wap.sogou.com/book/',
    'news': 'http://n.easou.com',
    'shop': 'http://s.m.taobao.com',
    'picture': 'http://wap.sogou.com',
}


def filter_word(word_list, length=MAX_LENGTH):
    results = []
    sum_len = 0
    for item in word_list:
        title_len = len(item['title'])
        if title_len <= WORD_MAX:
            sum_len += title_len
            if sum_len <= length:
                results.append(item)
            else:
                break
    return results


def content_hotwords():
    res = urllib2.urlopen("http://top.baidu.com/buzz?b=1", timeout=_TIME_OUT)
    soup = BeautifulSoup(res.read().decode('gbk'))
    a_tags = soup('a', {'class': 'list-title'},
                  href=re.compile(r'detail'), limit=20)
    word_list = []
    for item in a_tags:
        word_list.append(
            {'title': item.text, 'url': DOMAIN['web'] + item['href'][1:]})
    results = [word_list[0]]
    tops = filter_word(word_list[1:])
    results.extend(tops)
    for item in results:
        item['order'] = results.index(item)
    return results


def crawl_web():
    res = urllib2.urlopen("http://top.baidu.com/buzz?b=1", timeout=_TIME_OUT)
    soup = BeautifulSoup(res.read().decode('gbk'))
    a_tags = soup('a', {'class': 'list-title'},
                  href=re.compile(r'detail'), limit=30)
    shop_list = []
    for item in a_tags:
        shop_list.append({'title': item.text, 'url': ''})
    results = filter_word(shop_list, 50)
    return results


def crawl_story():
    res = urllib2.urlopen(
        "http://wap.sogou.com/book/rankingList.jsp", timeout=_TIME_OUT)
    soup = BeautifulSoup(res.read())
    a_tags = soup('a', href=re.compile(r'searchList\.jsp'), limit=10)
    shop_list = []
    for item in a_tags:
        shop_list.append(
            {'title': item.text, 'url': DOMAIN['story'] + item['href']})
    results = filter_word(shop_list)
    return results


def crawl_news():
    res = urllib2.urlopen("http://n.easou.com", timeout=_TIME_OUT)
    soup = BeautifulSoup(res.read())
    a_tags = soup('a', href=re.compile(r's\.m'), limit=10)
    shop_list = []
    for item in a_tags:
        shop_list.append({'title': item.text, 'url': ''})
    results = filter_word(shop_list)
    return results


def crawl_picture():
    res = urllib2.urlopen(
        "http://wap.sogou.com/pic/index.jsp", timeout=_TIME_OUT)
    soup = BeautifulSoup(res.read())
    a_tags = soup('a', href=re.compile(r'pic/searchList'), limit=10)
    shop_list = []
    for item in a_tags:
        shop_list.append({'title': item.text, 'url': ''})
    results = filter_word(shop_list)
    return results


def crawl_shop():
    res = urllib2.urlopen("http://m.taobao.com/?v=0", timeout=_TIME_OUT)
    soup = BeautifulSoup(res.read())
    a_tags = soup.find('div', class_='zz-hotWord').find_all('a',
                                                            href=re.compile(r'wo\.m\.taobao'))
    shop_list = []
    for item in a_tags:
        shop_list.append({'title': item.text, 'url': item['href']})
    results = filter_word(shop_list)
    return results


def crawl_wbnews():
    res = urllib2.urlopen(
        "http://dzone.dolphin.com/api/infostream/featured.json?c=10&from=widget&cid=%5b1,8,5,4,6%5d", timeout=_TIME_OUT)
    return simplejson.loads(res.read())


def add_from(cats):
    for items in cats:
        for item in items['items']:
            url = item['url']
            item['url'] = url.replace('#', '%sfrom=widget#' %
                                      ('&' if url.find('?') != -1 else '?'))
    return cats


def orginize_data(cats, is_new=False):
    #old = ['热点','科技','娱乐','论坛','体育']
    #new = ['要闻','科技','娱乐','社会','体育']
    more_ids = ['100', '102', '103', '101', '104']
    categorys = [1, 2, 3, 4, 5]
    for pos, items in enumerate(cats):
        #key = items['title'].strip().encode('utf-8')
        items = items['items']
        if is_new:
            cats[pos][
                'url'] = 'http://news.dolphin-browser.com/#ch%s' % more_ids[pos]
        categorys[pos] = '@'.join([item['url'] for item in items])

    return '%'.join(categorys)


def update_hotwords():
    try:
        update_methods = [crawl_web, crawl_story, crawl_news,  crawl_picture]
        for layout, method in zip(range(1, 6), update_methods):
            words = method()
            logger.info("[%s]->%s", method.__name__, words)
            cats = searchdb.get_search_categories({'_key.layout': layout})
            for cat in cats:
                if not cat.get('_meta')['manual_hotword']:
                    searchdb.update_search_category({
                        '_sync_key.id': cat['_sync_key']['id'],
                        '_key.layout': cat['_key']['layout']
                    },
                        {
                            '$set': {
                                '_meta_extend.hotwords': words,
                                '_meta_extend.hotword_modified': int(time.time())
                            }
                        })
    except Exception, e:
        logger.exception(e)


def update_news():
    try:
        update = True
        news_list = add_from(crawl_wbnews())
        new_cats = orginize_data(news_list, True)
        cond = {
            'packages': 'com.dolphin.browser.xf',
            'layout': 2
        }
        old_data = contentdb.get_section(cond)
        if len(old_data):
            old_cats = orginize_data(old_data['groups'][0]['cats'])
            if old_cats != new_cats:
                data = old_data['groups']
                data[0]['cats'] = news_list
                update = {
                    '$set':
                    {
                        'groups': data,
                        'time': int(time.time())
                    }
                }
                cond['packages'] = {
                    '$in': [
                        'com.dolphin.browser.xf',
                        'all:all'
                    ]
                }
                contentdb.update_section(cond, update)

                cond['packages'] = 'com.dolphin.browser.iphone.chinese'
                iphone_data = contentdb.get_section(cond)
                if iphone_data:
                    iphone_group = iphone_data['groups']
                    iphone_group[0]['cats'][0][
                        'items'] = news_list[0]['items'][0:5]
                    update = {
                        '$set':
                        {
                            'groups': iphone_group,
                            'time': int(time.time())
                        }
                    }
                    contentdb.update_section(cond, update)
                    logger.info('update iphone news!')
                logger.info('update news!')

    except Exception, e:
        logger.exception(e)


def update_search():
    try:
        tops = content_hotwords()
        cond = {'layout': 1}
        data = [
            {'cats':
             [
                 {
                     'url': '',
                     'items': tops,
                     'order': 1,
                     'title': ''
                 }
             ],
             'group': '',
             'order': 1,
             'api_version': 1
             }
        ]
        update = {
            '$set': {
                'groups': data,
                'time': int(time.time())
            }
        }
        contentdb.update_section(cond, update)
    except Exception, e:
        logger.exception(e)

if __name__ == '__main__':
    try:
        update_hotwords()
        print 'update hotwords done'
        update_search()
        print 'done'
        update_news()
        print 'update news done'
    except Exception, e:
        print e
