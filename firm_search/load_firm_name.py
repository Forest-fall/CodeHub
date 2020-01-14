import xlwt  
import xlrd
from xlutils.copy import copy
import numpy as np

path = "客户信息查询.xlsx"
worksheet = xlrd.open_workbook(path)
sheet_names= worksheet.sheet_names()
print(sheet_names)
sheet = worksheet.sheet_by_name(sheet_names[0])
firm_name = [sheet.cell_value(i, 0) for i in range(sheet.nrows)]
print(firm_name)
# np.save('firm_name.npy', firm_name)