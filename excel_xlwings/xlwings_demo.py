# code=utf-8

import xlwings as xw

app = xw.App(visible=True, add_book=False)
workbook = app.books.add()

worksheet = workbook.sheets['Sheet1']
worksheet.range('A1').value = '编号'

workbook.save('first_xw.xlsx')
workbook.close()
app.quit()