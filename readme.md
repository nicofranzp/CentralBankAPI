#  A quick way to download data using the Central Bank of Chile's API

The Central Bank of Chile (CBCh) provides and maintain a [public database](https://si3.bcentral.cl/siete/EN). In order to access the data, users have to perform several steps/mouse-clicks to get the data in their computer. The only format in which the data can be downloaded directly from the database is `*.xls`. 

 To speed up the process and get comma separated values (`*.csv`) files, I provide a `Python` and `R` routines and one excel spreadsheet to speed up the process (important part of the code is borrowed from [here](https://si3.bcentral.cl/estadisticas/Principal1/web_services/index.htm)).  One of the major gains of this workflow is to avoid clicking and get version control systems to work with data changes (`csv` files differences can be tracked by Git, for example). The `csv` file can be read by any statistical or mathematical software.


## What do you need to make it work

1. Get the API username and password
2. Python 3 installed and running
3. Select the series you want to download

## Get the API username and password
Follow the instructions [here](https://si3.bcentral.cl/estadisticas/Principal1/web_services/index_EN.htm) 

Once you have your username and password, copy them into the credentials in `getData.py` (lines 13 and 14)

``` python
# Inputs for the API
user	="INPUT YOUR USERNAME" 
pw	="INPUT YOUR PASSWORD" 
```

If you plan to share your project through GitHub or GitLab, I recommend you to set the username and password as a secret artifact of you project.

## Python
Install Python and the required libraries:

- xlrd
- pandas
- datetime
- os 
- zeep
- numpy
- time
- sys

### Mac OS Python installation
If you are a macOS user, you already have Python 2.7 out of the box. Nonetheless, I would recommend  you to install  `Xcode`, `Command Line Tools`, `homebrew`,  `pip` and, finally `Python 3`. You can follow these steps:
1. Install `Xcode` from the app Store.
2. Open your `Terminal.app` and type `xcode-select --install` to install the `Command Line Tools`
3. To install `Homebrew` type in you terminal 
   
   ```
   ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
   ```
   The scripts will explain the changes it will make and prompt you before it's done. More information on Homebrew [here](https://brew.sh)  
4. Type in your terminal `brew install python`. This will take a couple of minutes and will automatically install `pip` pointing at your python for you
5. Test your installation by typing `python3 --version`. You should get something like 
   ``` 
   Python 3.8.1
   ```
6. To install the `xlrd` library, for example,  type in the terminal `pip install xlrd`

## How to identify the series you want to download

 The most up-to-date data catalog with the `Code` to get access trough the API can be found [here](https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/Webservices/series_en.xls).  In this repo you can find a copy of it plus a couple of extra pages inside.  If you know what series you want to use just add a `1` in the column `use` (which is not in the original file), save the document and you're all good to go. In the third sheet, first cell, you will find the comma separated series you selected. This cell wil be read by the `Python` script `getData.py` to get the desired data. Note that  `getData.py` calls the function `getSeries` which is provided by the Central Bank of Chile. I tweaked the original function to return the series in english and also to get the time aggregation of them (e.g. averages, sum, or last). There is no way, as far as I know to get the units. The `code` of the series provides some information, but not all of it (TODO: example of how to read the series). 
 
 If you don't know what series you want and you want to see them first, the only way to match the online series to the ones in the Excel catalog is by copying the name of the Chapter, Table and Series.  

<details> <summary>Example</summary>

In the first image you can see where to find the chapter, table and series names to find the `Code` in the catalog (second image)
<center> 
<p>
<figcaption>Fig.1 - Online Database</figcaption>
<img src="src/images/BDE.png" alt="on enter key" width=90%>
</p>


<p>
<figcaption>Fig.2 - Data Catalog (selected section)</figcaption>
<img src="src/images/SeriesCatalogEg.png" alt="on enter key" width=90%> 
</p>
</center>
</details> <p></p>

Once you have a selection of the series inside the spreadsheet, you can run the `getData.py`, and, voila, you'll get the `csv` files for the diferent frequencies (i.e. `DAILY.csv`, `MONTHLY.csv`, `QUARTERLY.csv`, and `ANNUAL.csv`)

If you want to contribute to this project, just let me know. It would be nice to have the same routines for `R`, for example.
