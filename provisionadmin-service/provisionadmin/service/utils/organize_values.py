#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Created on 2014-07-04
# @author: chzhong

import sys
import os
from optparse import OptionParser, OptionGroup

sys.path.append(os.path.dirname(__file__))

from provisionadmin.service.android import res
'''
import jianfan

def zhs2t(s):
    return jianfan.jtof(s)

def translator_zhs2t(s):
    return res.utf8(zhs2t(res.utf8(s)))

TRANSLATORS = {
    'zh-rCN:zh-rHK' : translator_zhs2t
}
'''


def loadResDirCallback(resourceMap, dirname, fileNames):
    basename = os.path.basename(dirname)
    if basename == "res":
        fileNames[:] = sorted(fileNames)
        return
    if not basename.startswith('values'):
        return
    fileNames[:] = sorted(filter(lambda name: 'build_info' not in name and 'provider' not in name and '_config' not in name and '_arrays' not in name, fileNames))
    isDefault = basename == 'values'
    for fileName in fileNames:
        path = os.path.join(dirname, fileName)
        if os.path.isdir(path):
            continue
        resFile = res.ResourceFile(path)
        resFile.loadEntries()
        if isDefault:
            resourceMap.addResourceFile(fileName, resFile)
        else:
            resourceMap.organizeResourceFile(resFile)


def loadStrings(projectDir, options):
    resDir = os.path.join(projectDir, 'res')
    resourceMap = res.ResourceMap(projectDir)
    os.path.walk(resDir, loadResDirCallback, resourceMap)
    #resourceMap.translateStrings('zh-rCN', 'zh-rHK', translator_zhs2t)
    #resourceMap.extractString('pref_development_ua_choices', 1, 'pref_development_ua_desktop', 'settings_strings.xml')
    #resourceMap.extractString('pref_development_ua_choices', 4, 'pref_development_ua_custom', 'settings_strings.xml')
    if options.reportStat:
         resourceMap.describeTranslationStats()
    if options.describeMissing:
        resourceMap.describeMissingTranslations()
    if options.doOrganize:
        resourceMap.writeStrings(testRun=options.testRun,
                                 updateDefault=options.updateDefault,
                                 generateIds=options.generateIds,
                                 dumpMissing=options.dumpMissing,
                                 dumpExtras=not options.trimExtras,
                                 droppedNames=options.trimStrings)
    return resourceMap


def oragnizeStrings(projectDir, options):
    resourceFiles = loadStrings(projectDir, options)


def _parse_arguments(fakeArgs):
    usage = "Organize strings in xml files.\n"
    usage += "%prog [OPTION]... projectDir...\n"
    print usage

    parser = OptionParser(usage=usage)
    parser.add_option('--describe-missing', dest='describeMissing', action="store_true", help="List about missing translations.")
    parser.add_option('--stat', dest='reportStat', action="store_true", help="Report translation stats.")
    parser.add_option('-o', '--organize', dest='doOrganize', action="store_true", help="Organize strings.")
    organize_group = parser.add_option_group("Organize Options")
    organize_group.add_option('--test-run', dest='testRun', action="store_true", help='Perform a test run and write result to a separate directory.')
    organize_group.add_option('-d', '--update-default', dest='updateDefault', action="store_true", help='Also update default translation.')
    organize_group.add_option('--dump-missing', dest='dumpMissing', action="store_true", help='Also dump missing translations.')
    organize_group.add_option('-T', '--trim-extras', dest='trimExtras',action="store_true",help='Trim extra translations that should\'t be translated or not exists in default translation.')
    organize_group.add_option('--gen-ids', dest='generateIds',action="store_true", help='Generate string ids.')
    organize_group.add_option('-r', '--remove', '--trim', dest='trimStrings', action="append",default=[], metavar='NAME',help='Trim extra translations with specified name.')

    return parser.parse_args(fakeArgs)


def merge_xml(xml_path):
    fakeArgs = ['-o']
    fakeArgs.append(xml_path)
    print "yyyyyyy%s" % fakeArgs
    options, args = _parse_arguments(fakeArgs)
    print options
    print args

    for arg in args:
        oragnizeStrings(arg, options)
