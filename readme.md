#  A quick way to download data using the Central Bank of Chile's API

The Central Bank of Chile (CBCh) provides a [public database](https://si3.bcentral.cl/siete/EN). In order to access the data, the user has to perform several steps to get the data in his/her computer. To avoid this, I provide a couple of files and routhines to speed the process. 

In this document I explain how to use the `Python` routines in this folder  to get `csv` files to use in with statistical packages or any other software you might like to use. 

## What do you need to make it work

1. Get the API username and password
2. Python 3 installed and running
3. Select the series you want to download

## Get the API username and password
Follow the instructions [here](https://lmgtfy.com/?q=central+bank+of+chile+API) 

[Let Me Google That For You](https://lmgtfy.com/?q=central+bank+of+chile+API)

## Python

[Let Me Google That For You](https://lmgtfy.com/?q=how+to+install+python+3)

## How to identify the series you want to download

 The most up-to-date data catalog with the `Code` to get access trough the API can be found [here](https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/Webservices/series_en.xls).  In this repo you can find a copy of it plus a couple of pages inside.  If you know what series you want to use just add a `1` in the column `use` (which I created), save the document and you're all good to go. In the third sheet, first cell, you will find the comma separated series you selected. This cell wil be read by the `Python` script to get the desired data.
 
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
