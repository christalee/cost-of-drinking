import tabula

pdf = 'Mapping_the_worlds_prices_2019.pdf'
# df = tabula.read_pdf(pdf, pages='all')

tabula.convert_into(pdf, 'monthly-salary.csv', output_format='csv', pages='8')
tabula.convert_into(pdf, 'litres-of-coca-cola.csv', output_format='csv', pages='17')
tabula.convert_into(pdf, 'beer-pub.csv', output_format='csv', pages='18')
tabula.convert_into(pdf, 'litre-of-gas.csv', output_format='csv', pages='23')
tabula.convert_into(pdf, 'cappuccino.csv', output_format='csv', pages='33')
tabula.convert_into(pdf, 'basic-dinner-for-two.csv', output_format='csv', pages='29')
