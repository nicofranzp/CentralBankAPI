library(XML)
library(xml2)
library(plyr)
library(stringi)
library(httr)

# TODO: check the fields with respect the python code

#Funcion para entrar el web service
getseries <- function(user, password, firstDate, lastDate, lista_serie){
    lista_serie<-unique(lista_serie)
    lista_serie<-toupper(lista_serie)
    lista_serie<-as.vector(lista_serie)
    lista_serie_aux<- stri_sub(lista_serie, -1)
    lista_serie_aux<-unlist(lapply(lista_serie_aux, tolower))
    right_freq<-c("d","m","t","a")
    bool_right_ser<-lista_serie_aux %in% right_freq
    if (sum(!bool_right_ser)>=1){
        print(paste("The series ",paste(lista_serie[!bool_right_ser],collapse=", ")," do not exist. Please double check the codes",sep=""))
    }
    lista_serie<-lista_serie[bool_right_ser]
    FrequencyCode<- unique(stri_sub(lista_serie, -1))
    FrequencyCode <- gsub("A", "ANNUAL", FrequencyCode)
    FrequencyCode <- gsub("T","QUARTERLY", FrequencyCode)
    FrequencyCode <- gsub("M", "MONTHLY", FrequencyCode)
    FrequencyCode <- gsub("D","DAILY", FrequencyCode)
    dfFinal1 <- data.frame()
    headerFields <-c('Content-Type' = "text/xml; charset=utf-8")
    for (Frec in FrequencyCode){
        body1 <- paste('<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                    <SearchSeries xmlns="http://bancocentral.org/">
                    <user>',user,'</user>
                    <password>',password,'</password>
                    <frequencyCode>',Frec,'</frequencyCode>
                    </SearchSeries>
                    </soap:Body>
                    </soap:Envelope>', sep = "")
        for (intento1 in 1:4){
            tryCatch({
                response1<-httr::POST(url = "https://si3.bcentral.cl/SieteWs/SieteWS.asmx",
                                body= body1,
                                add_headers(headerFields))
                response1<-content(response1)
                test1<- xmlTreeParse(response1)[["doc"]]
                xmltest<- xmlToList(test1[[1]][[1]][[1]][[1]])
                if (xmltest$Codigo=="-1"){
                    error_gen/2
                }
                if (class(xmltest$SeriesInfos)=="matrix"){
                    xmltest$SeriesInfos<-apply(xmltest$SeriesInfos, 2, as.list)
                }
                EnglishTitle <- unlist(lapply(xmltest$SeriesInfos,function(x){if (is.null(x$englishTitle)) {NA} else {x$englishTitle}}))
                Frequency <- unlist(lapply(xmltest$SeriesInfos,function(x){if (is.null(x$frequencyCode)) {NA} else {x$frequencyCode}}))
                # Observed <- unlist(lapply(xmltest$SeriesInfos,function(x){if (is.null(x$observed)) {NA} else {x$observed}}))
                Series1 <- unlist(lapply(xmltest$SeriesInfos,function(x){if (is.null(x$seriesId)) {NA} else {x$seriesId}}))
                df_aux1<- data.frame(EnglishTitle = EnglishTitle, Frequency=Frequency)
                rownames(df_aux1) <- Series1
                valid_row1 <- intersect(rownames(df_aux1),lista_serie)
                df_aux1 <- df_aux1[valid_row1,]
                dfFinal1 <- rbind(dfFinal1,df_aux1)
                print(paste("Frequency ",Frec, " found. Adding",sep=""))
                break
            },error = function(e){
                    message("Try number ", intento1,": the frequency ",Frec, " was not found")
                    print(e)
                    Sys.sleep(20)
                    if (intento1==4){
                        stop(paste("Frequency ",Frec," was not found. Aborting",sep=""))
                    }
                }
            )
        }
    }

    dfFinal <- data.frame()
    row_name <- c()

    for(serie in lista_serie){
        body <- paste('<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                <GetSeries xmlns="http://bancocentral.org/">
                <user>',user,'</user>,
                <password>',password,'</password>
                <firstDate>',firstDate,'</firstDate>
                <lastDate>',lastDate,'</lastDate>
                <seriesIds>
                <string>',serie,'</string>
                </seriesIds>
                </GetSeries>
                </soap:Body>
                </soap:Envelope>', sep="")

        for (intento in 1:4){
            tryCatch({
                response<-httr::POST(url = "https://si3.bcentral.cl/SieteWs/SieteWS.asmx",
                                body= body,
                                add_headers(headerFields))
                response<-content(response)
                if (xml_text(xml_find_all(response,"//*")[5])!="0"){
                    error_gen/2
                }
                Fecha <-  xml_text(xml_find_all(response, "//obs/indexDateString"))
                Value <-  xml_text(xml_find_all(response, "//obs/value"))
                if (length(Fecha)==0){
                    print(paste("The serie ",serie, " does not have data for the selected period. Ommitting",sep=""))
                    break
                }
                df_aux<- data.frame(t(data.frame(Value)))
                colnames(df_aux) <- Fecha
                dfFinal <- rbind.fill(dfFinal,df_aux)
                row_name <- append(row_name,serie)
                print(paste("Series ",serie, " found. Adding",sep=""))
                break
                },

                error = function(e){
                    print(paste("Try number " , intento , ": the serie " , serie , " was not found",sep=""))
                    Sys.sleep(20)
                    if (intento==4){
                        print(paste("The serie " , serie , " not found. Omitiendo",sep=""))
                    }
                }
            )
            }
    }

    row_name<- unlist(row_name)
    rownames(dfFinal) <-row_name
    dfFinal[dfFinal=="NaN"]<- NA
    dfFinal <- dfFinal[,order(as.Date(colnames(dfFinal),format="%d-%m-%Y"))]
    rownames_inter<-intersect(rownames(dfFinal),rownames(dfFinal1))
    dfList <- cbind(dfFinal1[rownames_inter,], dfFinal[rownames_inter,])
    colsstr <- c(1, 2)
    colsnum <- 3:ncol(dfList)
    dfList[,colsstr] <- apply(dfList[,colsstr], 2, function(x) as.character(x))
    dfList[,colsnum] <- apply(dfList[,colsnum], 2, function(x) 
    as.numeric(x))
    Encoding(dfList[,1])<-"UTF-8"
    dfList<-split(dfList , f = dfList$Frequency)
    dfList <- lapply(dfList,function(x){Filter(function(x)!all(is.na(x)), x)})
    return(dfList)
}