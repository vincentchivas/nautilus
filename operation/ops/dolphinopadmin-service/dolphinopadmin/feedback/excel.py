'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author: Wenyuan Wu
@Date: 2011-11-30
'''

from pyExcelerator import Workbook


def export_data_to_excel(column_names, export_data, path):
    workbook = Workbook()
    sheet = workbook.add_sheet('sheet0')
    length = len(column_names)
    for i in range(length):
        sheet.write(0, i, column_names[i])
    for i in range(len(export_data)):
        for j in range(length):
            sheet.write(i + 1, j, export_data[i][j])
    workbook.save(path)
