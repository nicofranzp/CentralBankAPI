# Dowload series from the Central Bank of Chile
library("xlsx")
library("dotenv")
source("getseries.R")

# Inputs for the API
load_dot_env()
user	<- Sys.getenv("CBAPIUSR")
pw	<-  Sys.getenv("CBAPIPW")
initD	<- "1900-01-01"
endD	<- Sys.Date()

# Read series from the excel file
seriesJoined <- read.xlsx("series_en.xlsx", 3, header = FALSE)[1, 1]
series <- unlist(strsplit(as.character(head(seriesJoined)), split = ","))
# If you don't want to use the xlsx spreadsheet, create a char variable "series" with the code of the variables you would like to download.

# Request data to the Central Bank
Data <- getseries(user, pw, initD, endD, series)

# Export data into csv
for (name in names(Data)){
	write.csv(as.data.frame(t(as.matrix(Data[[name]]))), paste(toString(name), ".csv"))
}