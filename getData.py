# Import series from Central Bank of Chile 
import xlrd
import pandas as pd
from datetime import date
import os 
# cd current file folder
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
print(path)
from getseries import getSeries

# Inputs for the API
user	="INPUT YOUR USERNAME" 
pw	="INPUT YOUR PASSWORD" 
initD	="1900-01-01" 
today	= date.today()
endD	= today.strftime("%Y-%m-%d")

# Read the selected series in the xlsx file
wBook	= xlrd.open_workbook('series_en.xlsx')
sheet	= wBook.sheet_by_name('csv code')
series	= sheet.cell(0,0).value 
series	= series.replace(' ','')
series	= series.split(",")
series=[x.upper() for x in series]

# Get the series
Dta = getSeries(user,pw,initD,endD,series)
# Process the data and export to csv, for each frequency 
for i in list(Dta.keys()):
	name = str(i)
	name = Dta[i].T
	# For each series, remove points from name
	for j in list(name.keys()):
		name[j.replace('.', '')] = name.pop(j)
	name.to_csv(i+'_data.csv')



