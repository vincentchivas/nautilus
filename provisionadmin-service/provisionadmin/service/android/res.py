#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Created on 2014-07-04
# @author: chzhong


import sys
import os
import os.path
import threading

import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

def utf8(s):
    if isinstance(s, unicode):
      return s.encode('utf8')
    return s

class AndroidResourceTreeBuilder(ET.TreeBuilder):

    def __init__(self, element_factory=None):
        ET.TreeBuilder.__init__(self, element_factory)

    def comment(self, text):
        self._flush()
        self._last = elem = ET.Comment(text)
        if self._elem:
            self._elem[-1].append(elem)
        self._tail = 1
        return elem

class AndroidResourceXmlParser(ET.XMLParser):

    def __init__(self, html=0, target=None, encoding=None, comment_as_element=False):
        ET.XMLParser.__init__(self, html, target, encoding)
        self.parser.StartNamespaceDeclHandler = self._start_ns_decl
        self.parser.EndNamespaceDeclHandler = self._end_ns_decl
        self._encoding = encoding
        self._comments = []
        self._namespaces = {}
        self._namespaces_inv = {}
        self._comment_as_element = comment_as_element

    def _fix_node(self, node):
        node.ns_map = dict(self._namespaces)
        node.ns_map_inv = dict(self._namespaces_inv)
        if not self._comment_as_element:
            node.comments = self._drainComments()
        return node

    def _start(self, tag, attrib_in):
        node = ET.XMLParser._start(self, tag, attrib_in)
        self._fix_node(node)
        return node

    def _start_list(self, tag, attrib_in):
        node = ET.XMLParser._start_list(self, tag, attrib_in)
        self._fix_node(node)
        return node

    def _start_ns_decl(self, prefix, uri):
        prefix = utf8(prefix or "")
        uri = utf8(uri or "")

        self._namespaces[prefix] = uri
        self._namespaces_inv[uri] = prefix

    def _end_ns_decl(self, prefix):
        prefix = utf8(prefix or "")
        uri = self._namespaces.get(prefix)
        if uri is not None:
            del self._namespaces_inv[uri]
        del self._namespaces[prefix]

    def _handle_as_prefix(self, data):
        comment_text = self._fixtext(data)
        if comment_text:
            self._comments.append(comment_text)

    def _comment(self, data):
        if self._comment_as_element:
            return ET.XMLParser._comment(self, data)
        else:
            self._handle_as_prefix(data)

    def _drainComments(self):
        comments = self._comments
        self._comments = []
        return comments

def parse_xml(file, comment_as_element=False):
    root = None
    ns_map = []
    ns_map_inv = []
    parser = AndroidResourceXmlParser(target=AndroidResourceTreeBuilder(), comment_as_element=comment_as_element)
    return ET.parse(file, parser)

def normalize_tag(name, ns_map_inv):
    if name[0] == "{":
        uri, tag = name[1:].split("}")
        if uri in ns_map_inv:
            uri = ns_map_inv[uri]
        return uri + ':' + tag
    else:
        return name

def innerXML(node):
    if len(node) > 0:
        text = xml_escape(node.text or '')
        for child in node:
            text += outterXML(child)
            if child.tail:
                text += xml_escape(child.tail)
        return text or ''
    else:
        return xml_escape(node.text or '')

def outterXML(node):
    attribs = ''
    for k in node.attrib:
        v = node.attrib[k]
        attribs += ' %(key)s="%(value)s"' % { 'key' : normalize_tag(k, node.ns_map_inv), 'value' : v }
    # for k in node.ns_map:
    #    v = node.attrib[k]
    #    attribs += ' xmlns:%(key)s="%(value)s"' % { 'key' : k, 'value' : v }
    args = { 'tag' : normalize_tag(node.tag, node.ns_map_inv), 'attrib' : attribs }
    if 0 == len(node) and 0 == len(node.text):
        return '<%(tag)s%(attrib)s/>' % args
    else:
        args['innerXML'] = innerXML(node)
        return '<%(tag)s%(attrib)s>%(innerXML)s</%(tag)s>' % args

class BaseEntry(object):

    def __init__(self):
        self._attributes = {}
        self._comments = []
        self._tails = None

    @classmethod
    def tagName(self):
        raise NotImplemented()

    def getAttribute(self, attrName, defaultValue=None):
        return self._attributes.get(attrName, defaultValue)

    def setAttribute(self, attrName, attrValue):
        self._attributes[attrName] = attrValue

    def mergeAttributes(self, attrib):
        self._attributes.update(attrib)

    def mergeNode(self, node):
        self._comments.extend(node.comments)
        for k in node.attrib:
            self._attributes[normalize_tag(k, node.ns_map_inv)] = node.attrib[k]
        if node.tail:
            n = node.tail.count('\n')
            if n > 1:
                self._tails = '\n'

    def addComment(self, comment):
        self._comments.append(comment)

    def toXml(self, specifiers, **kwargs):
        indentLevel = kwargs.get('indentLevel', 0)
        indentText = kwargs.get('indentText', '    ')
        comments = ''
        for comment in self._comments:
            if '\n' in comment:
                lines = comment.split('\n')
                comments += indentText * indentLevel + "<!--\n"
                for line in lines:
                    lv = line.count(' ') / 4
                    intent = '' if  lv >= indentLevel else indentText * (indentLevel - lv)
                    comments += intent + line + "\n" if line.strip() else ''
                comments += indentText * indentLevel + "-->\n"
            else:
                comments += indentText * indentLevel + "<!--" + comment + "-->\n"

        startElement = self._startElement(specifiers, **kwargs)
        content = self._content(specifiers, **kwargs)
        endElement = self._endElement(specifiers, **kwargs)
        tail = self._tails if self._tails else ''

        return comments + startElement + content + endElement + tail

    def _startElement(self, specifiers, **kwargs):
        indentLevel = kwargs.get('indentLevel', 0)
        indentText = kwargs.get('indentText', '    ')
        attributes = ''
        for k in self._attributes:
            v = self._attributes[k]
            attributes += ' %(key)s="%(value)s"' % { 'key' : k, 'value' : v }

        return "%(indent)s<%(tag)s%(attributes)s>" % { 'indent' : indentText * indentLevel, 'tag' : self.tagName(), 'attributes' : attributes }

    def _endElement(self, specifiers, **kwargs):
        return "</%(tag)s>\n" % { 'tag' : self.tagName() }

    def _content(self, specifiers, **kwargs):
        # TODO Convert self to XML format
        raise NotImplemented()

class BaseValueEntry(BaseEntry):

    def __init__(self, name):
        BaseEntry.__init__(self)
        self.setAttribute('name', name)
        self._valueMap = {}

    @property
    def name(self):
        return self.getAttribute('name')

    @property
    def translatable(self):
        return False

    @property
    def i18n(self):
        return False

    @property
    def formatted(self):
        return False

    def getValue(self, specifiers = ''):
        return self._valueMap[specifiers]

    def setValue(self, specifiers, value):
        self._valueMap[specifiers] = value

    def deleteValue(self, specifiers):
        del self._valueMap[specifiers]

    def makeNoDefaultEntry(self, specifiers):
        self.setValue(specifiers, self.getValue())
        self.deleteValue('')
        return self

    @property
    def supportedSpecifiers(self):
        return sorted(list(self._valueMap.keys()))

    def supportsSpecifiers(self, specifiers):
        return specifiers in self._valueMap

class WrapperEntry(BaseValueEntry):

    def __init__(self, name, node):
        BaseValueEntry.__init__(self, name)
        self._valueMap[''] = node

    def _content(self, specifiers, **kwargs):
        node = self.getValue(specifiers)
        return innerXML(node)

    @classmethod
    def tagName(cls):
        return node.tag

class ValueEntry(BaseValueEntry):

    def __init__(self, name, value):
        BaseValueEntry.__init__(self, name)
        self._valueMap[''] = value

    def _content(self, specifiers, **kwargs):
        text = self.getValue(specifiers)
        return text

class BoolEntry(BaseValueEntry):

    def __init__(self, name, value):
        ValueEntry.__init__(self, name, value)

    @classmethod
    def tagName(cls):
        return "bool"

class ColorEntry(BaseValueEntry):

    def __init__(self, name, value):
        ValueEntry.__init__(self, name, value)

    @classmethod
    def tagName(cls):
        return "color"

class DimensionEntry(BaseValueEntry):

    def __init__(self, name, value):
        ValueEntry.__init__(self, name, value)

    @classmethod
    def tagName(cls):
        return "dimen"

class IdEntry(BaseEntry):

    def __init__(self, name, type):
        BaseEntry.__init__(self)
        self.setAttribute('name', name)
        self.setAttribute('type', type)

    @property
    def type(self):
        return self.getAttribute('type')

    @property
    def name(self):
        return self.getAttribute('name')

    @property
    def translatable(self):
        return False

    @property
    def i18n(self):
        return False

    @property
    def formatted(self):
        return False

    @classmethod
    def tagName(cls):
        return "item"

    @property
    def supportedSpecifiers(self):
        return ['']

    def supportsSpecifiers(self, specifiers):
        return specifiers == ''

    def _startElement(self, specifiers, **kwargs):
        indentLevel = kwargs.get('indentLevel', 0)
        indentText = kwargs.get('indentText', '    ')
        attributes = ''
        for k in self._attributes:
            v = self._attributes[k]
            attributes += ' %(key)s="%(value)s"' % { 'key' : k, 'value' : v }

        return "%(indent)s<%(tag)s%(attributes)s />\n" % { 'indent' : indentText * indentLevel, 'tag' : self.tagName(), 'attributes' : attributes }

    def _endElement(self, specifiers, **kwargs):
        return ""

    def _content(self, specifiers, **kwargs):
        return ""

class IntegerEntry(BaseValueEntry):

    def __init__(self, name, value):
        ValueEntry.__init__(self, name, value)

    @classmethod
    def tagName(cls):
        return "integer"

class StringEntry(ValueEntry):

    def __init__(self, name, value):
        ValueEntry.__init__(self, name, value)

    @property
    def translatable(self):
        return self.getAttribute('translatable', 'true') != 'false'

    @property
    def i18n(self):
        return self.getAttribute('i18n', 'true') != 'false'

    @property
    def formatted(self):
        return self.getAttribute('formatted', 'true') != 'false'

    @classmethod
    def tagName(cls):
        return "string"

class BaseItemEntry(BaseEntry):

    def __init__(self, value):
        BaseEntry.__init__(self)
        self._value = value

    @classmethod
    def tagName(cls):
        return "item"

    @property
    def value(self):
        return self._value

    def _content(self, specifiers, **kwargs):
        return self._value

class ItemsEntry(BaseValueEntry):

    def __init__(self, name, items):
        BaseValueEntry.__init__(self, name)
        self._valueMap[''] = items

    def getItems(self, specifiers = ''):
        return self.getValue(specifiers)

    def setItems(self, specifiers, items):
        self.setValue(specifiers, items)

    def deleteItems(self, specifiers):
        self.deleteValue(specifiers)

    def _content(self, specifiers, **kwargs):
        indentLevel = kwargs.get('indentLevel', 0)
        indentText = kwargs.get('indentText', '    ')
        itemkwArgs = kwargs.copy()
        itemkwArgs['indentLevel'] = indentLevel + 1
        itemList = self.getItems(specifiers)
        items = ''
        for item in itemList:
            items += item.toXml(specifiers, **itemkwArgs)

        return "\n%(items)s%(indent)s" % { 'indent' : indentText * indentLevel, 'items' : items }

class IntegerItemEntry(BaseItemEntry):

    def __init__(self, value):
        BaseItemEntry.__init__(self, value)

    def asIntegerEntry(self, name):
        return IntegerEntry(name, self._value)

class IntegerArrayEntry(ItemsEntry):

    @classmethod
    def tagName(cls):
        return "integer-array"

class TypedItemEntry(BaseItemEntry):

    def __init__(self, value):
        BaseItemEntry.__init__(self, value)

class TypedArrayEntry(ItemsEntry):

    @classmethod
    def tagName(cls):
        return "array"

class StringItemEntry(BaseItemEntry):
    def __init__(self, value):
        BaseItemEntry.__init__(self, value)

    def asStringEntry(self, name):
        return StringEntry(name, self._value)

class StringArrayEntry(ItemsEntry):

    @classmethod
    def tagName(cls):
        return "string-array"

    @property
    def translatable(self):
        return self.getAttribute('translatable', 'true') != 'false'

    @property
    def i18n(self):
        return self.getAttribute('i18n', 'true') != 'false'

    @property
    def formatted(self):
        return self.getAttribute('formatted', 'true') != 'false'

class StyleItemEntry(BaseItemEntry):
    def __init__(self, value):
        BaseItemEntry.__init__(self, value)

class StyleEntry(ItemsEntry):

    @classmethod
    def tagName(cls):
        return "style"

class PluralItem(BaseItemEntry):

    def __init__(self, quantity, value):
        BaseItemEntry.__init__(self, value)
        self.setAttribute('quantity', quantity)

    @property
    def quantity(self):
        return self.getAttribute('quantity')

class PluralEntry(ItemsEntry):

    def __init__(self, name, items):
        ItemsEntry.__init__(self, name, items)

    @classmethod
    def tagName(cls):
        return "plurals"

    @property
    def translatable(self):
        return self.getAttribute('translatable', 'true') != 'false'

    @property
    def i18n(self):
        return self.getAttribute('i18n', 'true') != 'false'

    @property
    def formatted(self):
        return self.getAttribute('formatted', 'true') != 'false'

class ResourceFile(BaseEntry):

    def __init__(self, path):
        BaseEntry.__init__(self)
        self._path = path
        self._entries = []
        self._entryMap = {}
        dirname = os.path.dirname(path)
        self._dirname = dirname
        dirbase = os.path.basename(dirname)
        if '-' in dirbase:
            specifiers = dirbase.split('-')
            self._type = specifiers[0]
            self._specifiers = '-'.join(specifiers[1:])
        else:
            self._type = dirbase
            self._specifiers = ''
        self._writtenCount = 0


    @classmethod
    def tagName(cls):
        return "resources"

    @property
    def path(self):
        return self._path

    @property
    def dirname(self):
        return self._dirname

    @property
    def type(self):
        return self._type

    @property
    def entries(self):
        return self._entries

    @property
    def specifiers(self):
        return self._specifiers

    def _content(self, specifiers, **kwargs):
        indentLevel = kwargs.get('indentLevel', 0)
        indentText = kwargs.get('indentText', '    ')
        dumpMissing = kwargs.get('dumpMissing', False)
        droppedNames = kwargs.get('droppedNames', [])
        itemkwArgs = kwargs.copy()
        itemkwArgs['indentLevel'] = indentLevel + 1
        writtenCount = 0
        checkSpecifiers = specifiers
        dumpSpecifiers = '' if dumpMissing else specifiers
        items = ''
        for item in self._entries:
            if item.name in droppedNames \
            or (not dumpMissing and not item.supportsSpecifiers(checkSpecifiers)) \
            or (dumpMissing and (not item.translatable or not item.i18n or item.supportsSpecifiers(checkSpecifiers))):
                continue
            items += item.toXml(dumpSpecifiers, **itemkwArgs)
            writtenCount += 1
        self._writtenCount = writtenCount

        return "\n%(items)s%(indent)s" % { 'indent' : indentText * indentLevel, 'items' : items }

    def addEntry(self, specifiers, entry):
        oldEntry = self._entryMap.get(entry.name)
        if not oldEntry:
            return False
        elif not oldEntry.translatable:
            return False
        if oldEntry.supportsSpecifiers(specifiers):
            while True:
                choice = input('Duplicated translation "%s" for %s found:\n1: %s\n2: %s\nUse which one? ' \
                               % (entry.name, specifiers, utf8(oldEntry.getValue(specifiers)), utf8(entry.getValue())))
                if choice in (1, 2):
                    break
                print 'Invalid choice "%s"' % repr(choice)
            if 2 == choice:
                print 'Overwrite "%s" for %s with "%s".' % (entry.name, specifiers, entry.getValue())
        else:
            oldEntry.setValue(specifiers, entry.getValue())

        return True

    def createEntry(self, entry):
        oldEntry = self._entryMap.get(entry.name)
        if oldEntry is not None:
            return self.addEntry('', entry)
        self._entries.append(entry)
        self._entryMap[entry.name] = entry
        return True

    def getEntry(self, name):
        return self._entryMap.get(name)

    def removeEntry(self, entry):
        if isinstance(entry, basestring):
            entryName = entry
            if entryName not in self._entryMap:
                return
            entry = self._entryMap[entryName]
        del self._entryMap[entry.name]
        self._entries.remove(entry)

    def loadEntries(self):
        xt = parse_xml(self._path)
        root = xt.getroot()
        for prefix in root.ns_map:
            self.setAttribute('xmlns:' + prefix, root.ns_map[prefix])
        self.mergeNode(root)
        for child in root:
            entry = None
            if 'string' == child.tag:
                entry = StringEntry(child.attrib['name'], innerXML(child))
            elif 'string-array' == child.tag:
                items = []
                for item in child:
                    stringItem = StringItemEntry(innerXML(item))
                    stringItem.mergeNode(item)
                    items.append(stringItem)
                entry = StringArrayEntry(child.attrib['name'], items)
            elif 'plurals' == child.tag:
                items = []
                for item in child:
                    pluralItem = PluralItem(item.attrib['quantity'], innerXML(item))
                    pluralItem.mergeNode(item)
                    items.append(pluralItem)
                entry = PluralEntry(child.attrib['name'], items)
            elif 'item' == child.tag:
                entry = IdEntry(child.attrib['name'], child.attrib['type'])
            #else:
            #    entry = WrapperEntry(child.attrib['name'], child)
            if entry:
                entry.mergeNode(child)
                self._entryMap[entry.name] = entry
                self._entries.append(entry)
        return self._entries

    def saveEntries(self, resourceDir, specifier, **kwargs):
        dumpMissing = kwargs.get('dumpMissing', False)
        droppedNames = kwargs.get('droppedNames', [])

        self._writtenCount = 0
        resourceFolder = os.path.join(resourceDir, 'values-' + specifier if specifier else 'values')
        fileName = os.path.basename(self._path)
        resPath = os.path.join(resourceFolder, fileName)
        if not os.path.exists(os.path.dirname(resPath)):
            os.makedirs(os.path.dirname(resPath))
        with open(resPath, "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(utf8(self.toXml(specifier, droppedNames=droppedNames)))
        if self._writtenCount > 0:
            print 'Written %d string(s) to %s.' % (self._writtenCount, resPath)
        else:
            os.remove(resPath)
        if dumpMissing:
            self._writtenCount = 0
            missingResourceFolder = os.path.normpath(os.path.join(resourceDir, "../res-missing", 'values-' + specifier if specifier else 'values'))
            missingFileName = "%s_missing%s" % os.path.splitext(fileName)
            missingResPath = os.path.join(missingResourceFolder, missingFileName)
            if not os.path.exists(os.path.dirname(missingResPath)):
                os.makedirs(os.path.dirname(missingResPath))
            with open(missingResPath, "w") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write(utf8(self.toXml(specifier, dumpMissing=True, droppedNames=droppedNames)))
            if self._writtenCount > 0:
                print 'Written %d missing string(s) to %s.' % (self._writtenCount, missingResPath)
            else:
                os.remove(missingResPath)

        return resPath

    def translateEntries(self, srcSpecifier, destSpecifier, translator, **kwargs):
        translatedCount = 0
        for item in self._entries:
            if  not item.translatable or not item.i18n \
            or item.supportsSpecifiers(destSpecifier) or not item.supportsSpecifiers(srcSpecifier):
                continue
            if isinstance(item, StringEntry):
                srcText = item.getValue(srcSpecifier)
                destText = translator(srcText)
                item.setValue(destSpecifier, destText)
                translatedCount += 1
            elif isinstance(item, StringArrayEntry):
                destArray = []
                srcItems = item.getItems(srcSpecifier)
                for srcItem in srcItems:
                    srcText = srcItem.value
                    destText = translator(srcText)
                    destItem = StringItemEntry(destText)
                    destArray.append(destItem)
                item.setItems(destSpecifier, destArray)
                translatedCount += 1
            elif isinstance(item, PluralEntry):
                destArray = []
                srcItems = item.getItems(srcSpecifier)
                for srcItem in srcItems:
                    srcText = srcItem.value
                    destText = translator(srcText)
                    destItem = PluralItem(srcItem.quantity, destText)
                    destArray.append(destItem)
                item.setItems(destSpecifier, destArray)
                translatedCount += 1


class NoDefaultResourceFile(ResourceFile):

    def __init__(self, path):
        ResourceFile.__init__(self, path)
        self.setAttribute('xmlns:xliff', 'urn:oasis:names:tc:xliff:document:1.2')


    def addEntry(self, specifiers, entry):
        oldEntry = self._entryMap.get(entry.name)
        if not oldEntry:
            entry.makeNoDefaultEntry(specifiers)
            self._entryMap[entry.name] = entry
            self._entries.append(entry)
            return True
        oldEntry.setValue(specifiers, entry.getValue())
        return True

class ResourceMap(object):

    MISSING_DEFAULT_XML_NAME = 'extra_strings.xml'
    IDS_XML_NAME = 'ids.xml'

    def __init__(self, projectDir):
        self._resourceFileMap = {}
        self._resourceNameMap = {
            'string' : {},
            'string-array' : {},
            'plurals' : {}
        }
        self._localizedFiles = []
        self._specifiers = set()
        self._specifiers.add('')
        self._entryCount = 0
        self._projectDir = projectDir;
        missingDefaultResFile = NoDefaultResourceFile(os.path.join(projectDir, 'res/values', ResourceMap.MISSING_DEFAULT_XML_NAME))
        self._missingDefaultResFile =  missingDefaultResFile
        self._idResFlie = None

    @property
    def entryCount(self):
        return self._entryCount

    @property
    def projectDir(self):
        return self._projectDir

    @property
    def noDefaultEntryCount(self):
        return len(self._missingDefaultResFile.entries)

    @property
    def specifiers(self):
        return list(self._specifiers)

    def addResourceFile(self, fileName, resFile):
        if len(resFile.entries) <= 0:
            return
        if fileName == ResourceMap.IDS_XML_NAME:
            print 'Ids file: %s, %d defined item(s).' % (fileName, len(resFile.entries))
            self._idResFlie = resFile
            return
        self._resourceFileMap[fileName] = resFile
        itemAdded = 0
        itemsRemoved = []
        for entry in resFile.entries:
            if isinstance(entry, IdEntry):
                continue
            itemAdded += 1
            name = entry.name
            type = entry.tagName()
            if name in self._resourceNameMap[type]:
                prevFileName = self._resourceNameMap[type][name]
                prevResFile =  self._resourceFileMap[prevFileName]
                prevEntry = prevResFile.getEntry(name)
                while True:
                    choice = input('Duplicated string "%s" found:\n1: %s: %s\n2: %s: %s\nUse which one? ' \
                                   % (name, prevFileName, prevEntry.getValue(), fileName, entry.getValue()))
                    if choice in (1, 2):
                        break
                    print 'Invalid choice "%s"' % repr(choice)
                if 2 == choice:
                    print 'Removed %s from %s.' % (name, prevFileName)
                    prevResFile.removeEntry(name)
                    self._resourceNameMap[type][name] = fileName
                else:
                    itemsRemoved.append(entry)
            else:
                self._resourceNameMap[type][name] = fileName
        for itemToRemove in itemsRemoved:
            print 'Removed %s from %s.' % (itemToRemove.name, fileName)
            resFile.removeEntry(itemToRemove)
        if itemAdded == 0:
            del self._resourceFileMap[fileName]
            return
        print '%s: %d string(s).' % (fileName, len(resFile.entries))
        self._entryCount += len(resFile.entries)

    def findResourceFile(self, type, name):
        fileName = self._resourceNameMap[type].get(name, None)
        if not fileName:
            return self._missingDefaultResFile
        return self._resourceFileMap[fileName]

    def fixIds(self):
        if not self._idResFlie:
            idResFile = ResourceFile(os.path.join(self._projectDir, 'res/values', ResourceMap.IDS_XML_NAME))
            self._idResFlie =  idResFile
        else:
            idResFile = self._idResFlie
        for type in self._resourceNameMap:
            nameMap = self._resourceNameMap[type]
            for name in nameMap:
                entry = idResFile.getEntry(name)
                if not entry or entry.type != type:
                    idEntry = IdEntry(name, type)
                    idResFile.createEntry(idEntry)

    def translateStrings(self, srcSpecifier, destSpecifier, translator, **kwargs):
        for fileName in sorted(self._resourceFileMap.keys()):
            print 'Performance translation from %s to %s for %s...' % (srcSpecifier, destSpecifier, fileName)
            resFile = self._resourceFileMap[fileName]
            resFile.translateEntries(srcSpecifier, destSpecifier, translator, **kwargs)
        self._specifiers.add(destSpecifier)

    def _translateStringFile(self, resFile, resourceDir, **kwargs):
        entries = resFile.entries
        for specifier in self._specifiers:
            resFile.saveEntries(resourceDir, specifier, **kwargs)

    def organizeResourceFile(self, resFile):
        entries = resFile.entries
        if len(entries) <= 0:
            return
        self._localizedFiles.append(resFile.path)
        specifiers = resFile.specifiers
        self._specifiers.add(specifiers)
        for entry in entries:
            name = entry.name
            type = entry.tagName()
            organizedResFile = self.findResourceFile(type, name)
            if not organizedResFile.addEntry(specifiers, entry):
                self._missingDefaultResFile.addEntry(specifiers, entry)

    def describeTranslationStats(self):
        sorted_specifiers = sorted(list(self._specifiers))
        print 'Languages: %d\n  %s.' % (len(self._specifiers), ", ".join(sorted_specifiers))
        print 'Total entries: %d' % self.entryCount
        statsTable = []
        statHeader = ['File', 'NLS', 'NIS', '(en)']
        statHeader.extend(sorted_specifiers[1:])
        statsTable.append(statHeader)
        specifierCount = len(sorted_specifiers)
        print '\t'.join(statHeader)

        for fileName in sorted(self._resourceFileMap.keys()):
            statRow = [0] * len(statHeader)
            statRow[0] = fileName
            resFile = self._resourceFileMap[fileName]
            entries = resFile.entries
            for entry in entries:
                if not entry.translatable:
                    statRow[1] += 1
                elif not entry.i18n:
                    statRow[2] += 1
                else:
                    statRow[3] += 1
                specifierIndex = 4
                for specifier in sorted_specifiers[1:]:
                    if entry.supportsSpecifiers(specifier) and entry.i18n:
                        statRow[specifierIndex] += 1
                    specifierIndex += 1
            statsTable.append(statRow)
            print '\t'.join([str(i) for i in statRow])
        print ''
        entries = self._missingDefaultResFile.entries
        statRow = [0] * len(statHeader)
        statRow[0] = 'Extras'
        statRow[1] = 0
        statRow[2] = 0
        statRow[3] = 0
        for entry in entries:
            specifierIndex = 4
            for specifier in sorted_specifiers[1:]:
                if entry.supportsSpecifiers(specifier):
                    statRow[specifierIndex] += 1
                specifierIndex += 1
        statsTable.append(statRow)
        print '\t'.join([str(i) for i in statRow])
        print '\n'
        return statsTable

    def describeMissingTranslations(self):
        print '%d entries, %d entries without default translation.' % (self.entryCount, self.noDefaultEntryCount)
        print 'Languages: %d\n  %s.' % (len(self._specifiers), ", ".join(sorted(list(self._specifiers))))
        print 'Missing Translations:'
        for fileName in sorted(self._resourceFileMap.keys()):
            print 'File: %s' % fileName
            resFile = self._resourceFileMap[fileName]
            self._describeMissingResourceSpecifiers(resFile)
        print '\n\nExtra translations:'
        entries = self._missingDefaultResFile.entries
        for entry in entries:
            print '  %s "%s": %s' % (entry.tagName(), entry.name, ', '.join(sorted(list(entry.supportedSpecifiers))))

    def _describeMissingResourceSpecifiers(self, resFile):
        entries = resFile.entries
        for entry in entries:
            if not entry.translatable or not entry.i18n:
                continue
            missingSpecifiers = set(self._specifiers) - set(entry.supportedSpecifiers)
            if len(missingSpecifiers) > 0:
                print '  %s "%s": %s' % (entry.tagName(), entry.name, ', '.join(sorted(list(missingSpecifiers))))

    def extractString(self, arrayName, arrayIndex, stringName, destFileName=None):
        srcResFile = self.findResourceFile('string-array', arrayName)
        destResFile = self._resourceFileMap[destFileName] if destFileName else srcResFile
        if srcResFile != self._missingDefaultResFile:
            array = srcResFile.getEntry(arrayName)

            items = array.getItems()
            text = items[arrayIndex].asStringEntry(stringName)
            destResFile.createEntry(text)
            if not array.translatable:
                array = self._missingDefaultResFile.getEntry(arrayName)
            sorted_specifiers = sorted(array.supportedSpecifiers)
            if '' in sorted_specifiers:
                sorted_specifiers.remove('')
            for specifier in sorted_specifiers:
                items = array.getItems(specifier)
                text = items[arrayIndex].asStringEntry(stringName)
                destResFile.addEntry(specifier, text)
        else:
            print 'String array %s not found.' % arrayName

    def moveEntry(self, type, name, destFileName):
        srcResFile = self.findResourceFile(type, name)
        destResFile = self._resourceFileMap[destFileName]
        if restFile != self._missingDefaultResFile:
            entry = srcResFile.getEntry(name)
            sorted_specifiers = sorted(list(self._specifiers))
            for specifier in sorted_specifiers:
                if not entry.supportsSpecifiers(specifier):
                    continue
                if not specifier:
                    destResFile.createEntry(entry)
                else:
                    destResFile.addEntry(specifier, entry)
            srcResFile.removeEntry(entry)

    def writeStrings(self, **kwargs):
        dumpExtras = kwargs.get('dumpExtras', True)
        testRun = kwargs.get('testRun', False)
        generateIds = kwargs.get('generateIds', False)

        for path in self._localizedFiles:
            print "Cleaning localized file %s." % path
            if not testRun:
                os.remove(path)
        resourceDir = os.path.join(self._projectDir, 'test/res/') if testRun else os.path.join(self._projectDir, 'res/')
        for fileName in sorted(self._resourceFileMap.keys()):
            print 'Writing strings for %s...' % fileName
            resFile = self._resourceFileMap[fileName]
            self._writeStringFiles(resFile, resourceDir, **kwargs)
        if dumpExtras:
            kwargs['dumpMissing'] = False
            self._writeStringFiles(self._missingDefaultResFile, resourceDir, **kwargs)
        if generateIds:
            self.fixIds()
            self._idResFlie.saveEntries(resourceDir, '')

    def _writeStringFiles(self, resFile, resourceDir, **kwargs):
        specifiers_to_write = self._specifiers
        if not kwargs.get('updateDefault', False) and '' in specifiers_to_write:
            specifiers_to_write.remove('')
        for specifier in self._specifiers:
            resFile.saveEntries(resourceDir, specifier, **kwargs)
