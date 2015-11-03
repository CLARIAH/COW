options(stringsAsFactors=FALSE)
library(foreign)

setwd('~/downloads/data/qqt/')

ca <- read.spss('canada 1901/1901.sav')
ca <- as.data.frame(ca)

# remove trailing and leading whitespace
for (i in 1:ncol(ca)){
    if (class(ca[, i]) == 'character'){
        ca[, i] <- gsub('^\\s{2,}|\\s{2,}$', '', ca[, i])
    }   
}

write.csv(ca, 'canada1901.csv', row.names=F)