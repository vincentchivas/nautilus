import sys
import os
import traceback
import xml.etree.cElementTree as ET

miss_path = None
origin_path = None


def diff_locale_origin(locale_dir, origin_dir):
    origin_xml_files = os.listdir(os.path.join(origin_path, origin_dir))
    locale_xml_files = os.listdir(os.path.join(origin_path, locale_dir))

    locale_miss_dir = os.path.join(miss_path, locale_dir)
    
    for xml_file in origin_xml_files:
        o_xml_path = os.path.join(os.path.join(origin_path, origin_dir), xml_file)
        o_xml_tree = ET.ElementTree(file=o_xml_path)
        o_xml_root = o_xml_tree.getroot()
        l_xml_path = os.path.join(os.path.join(origin_path, locale_dir), xml_file)
        miss_xml_path = os.path.join(os.path.join(miss_path, locale_dir), xml_file)
        remove_list = []
        if not os.path.exists(l_xml_path):
            for o_ele in o_xml_root:
                if o_ele.tag not in ['string', 'string-array', 'plurals']:
                    remove_list.append(o_ele)
                    continue
                o_ele_name = o_ele.attrib.get('name') 
                translatable = o_ele.attrib.get('translatable')
                if translatable == 'false':
                    remove_list.append(o_ele)
                    continue 
                i18n_enable = o_ele.attrib.get('i18n')
                if i18n_enable == 'false':
                    remove_list.append(o_ele)
                    continue 

            for r_ele in remove_list:
                o_xml_root.remove(r_ele) 

        else:
            l_xml_tree = ET.ElementTree(file=l_xml_path)
            l_xml_root = l_xml_tree.getroot()
            for o_ele in o_xml_root:
                if o_ele.tag not in ['string', 'string-array', 'plurals']:
                    remove_list.append(o_ele)
                    continue
                o_ele_name = o_ele.attrib.get('name') 
                translatable = o_ele.attrib.get('translatable')
                if translatable == 'false':
                    remove_list.append(o_ele)
                    continue 
                i18n_enable = o_ele.attrib.get('i18n')
                if i18n_enable == 'false':
                    remove_list.append(o_ele)
                    continue 
                if l_xml_tree.find('%s[@name="%s"]' % (o_ele.tag, o_ele_name))\
                        is not None:
                    remove_list.append(o_ele)

            for r_ele in remove_list:
                o_xml_root.remove(r_ele) 
                
        if len(o_xml_root) > 0:
            ET.register_namespace('xliff', 'urn:oasis:names:tc:xliff:document:1.2')
            ET.register_namespace('tools', 'http://schemas.android.com/tools')
            ET.ElementTree(o_xml_root).write(miss_xml_path, encoding='utf-8', xml_declaration=True)
                    


def diff_xml(o_path, m_path):
    global miss_path
    global origin_path
    miss_path = m_path
    origin_path = o_path

    f = lambda s: s.endswith('.xml')
    origin_values_dir = 'values'
    locale_values_dirs = filter(lambda s: s.startswith('values-'), os.listdir(origin_path))
    '''
    check miss dir
    '''
    for l in locale_values_dirs:
        if not os.path.exists(os.path.join(miss_path, l)):
            os.mkdir(os.path.join(miss_path, l))
        diff_locale_origin(l, origin_values_dir)
