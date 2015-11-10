options(stringsAsFactors=FALSE)
library(jsonlite)

ca <- read.csv('~/downloads/data/qqt/canada1901.csv')

candef <- read.csv('canadadefs.txt', header=F)
names(candef) <- c('vrb', 'def')
candef$vrb <- tolower(candef$vrb)

fill <- list()
for (vrb in names(ca)){
    tbl <- rev(sort(table(ca[, vrb])))
    if (length(tbl) > 6e3){
        # fill[[vrb]] <- NA
        fill[[vrb]]$def <- c(candef$def[candef$vrb==vrb])
        next
    }
    fill[[vrb]][['code']] <- names(tbl)
    fill[[vrb]][['label']] <- names(tbl)
    fill[[vrb]][['Freq']] <- c(tbl)
    fill[[vrb]][['def']] <- c(candef$def[candef$vrb==vrb])
}

names(fill)[!names(fill) %in% tolower(candef[,1])]

makecodelist <- function(cdvar, lbvar){
    cds <- aggregate(lbvar, by=list(code=cdvar), function(x) names(rev(sort(table(x))))[1])
    freq <- data.frame(table(cdvar))
    out <- merge(cds, freq, by.x='code', by.y='cdvar', all=F)
    names(out) <- c('code', 'label', 'Freq')
    return(as.list(out))
}

fill$relhead2 <- makecodelist(cdvar=ca$relhead2, lbvar=ca$relhead)
fill$relhead2$def <- candef$def[candef$vrb=='relhead2']

fill$occ1 <- makecodelist(cdvar=ca$occ1, lbvar=ca$occ)
fill$occ1$def <- candef$def[candef$vrb=='relhead2']

fill$religio2 <- makecodelist(cdvar=ca$religio2, lbvar=ca$religion)
fill$religio2$def <- candef$def[candef$vrb=='religio2']

fill$bpl2 <- makecodelist(cdvar=ca$bpl2, lbvar=ca$bpl)
fill$bpl2$def <- candef$def[candef$vrb=='bpl2']

marst <- data.frame(code=c('S', 'M', 'W', 'D', 'P', '!', '#', '=', '=', '?'),
    label=c('for single', 'for married', 'for widowed', 'for divorced ', '(separated)', '(illegible)', '(illogical) ', '(enumerator entered unknown)', '(enumerator entered unknown)', '(in place of illegible characters or to indicate a guess)'))
freqs <- data.frame(table(ca$marst))
marst <- merge(marst, freqs, by.x='code', by.y='Var1', all=T)
names(marst) <- c('code', 'label', 'Freq')
fill$marst <- as.list(marst)
fill$marst$def <- candef$def[candef$vrb=='marst']

earnper <- data.frame(code=c('M', 'W', 'D', 'H', '!', 'P', 'Y'),
    label=c('monthly', 'weekly', 'daily', 'hourly', 'illegible', 'piece', 'yearly'))
freqs <- data.frame(table(ca$earnper))
earnper <- merge(earnper, freqs, by.x='code', by.y='Var1', all=T)
names(earnper) <- c('code', 'label', 'Freq')
fill$earnper <- as.list(earnper)
fill$earnper$def <- candef$def[candef$vrb=='earnper']

sex <- data.frame(code=c('F', 'M', '!', '#', '?', '='),
    label=c('female', 'male', 'illegible', 'illogical', 'in place of illegible characters or to indicate a guess', 'enumerator entered “unknown”'))
freqs <- data.frame(table(ca$sex))
sex <- merge(sex, freqs, by.x='code', by.y='Var1', all=T)
names(sex) <- c('code', 'label', 'Freq')
fill$sex <- as.list(sex)
fill$sex$def <- candef$def[candef$vrb=='sex']

canread <- canwrite <- data.frame(code=c('Y', 'N', '!', '#', '='), 
    label=c('yes', 'no', 'illegible', 'illogical', 'enumerator entered unknown'))
freqs <- data.frame(table(ca$canread))
canread <- merge(canread, freqs, by.x='code', by.y='Var1', all=T)
fill$canread <- as.list(canread)
fill$canread$def <- candef$def[candef$vrb=='canread']

freqs <- data.frame(table(ca$canwrite))
canwrite <- merge(canwrite, freqs, by.x='code', by.y='Var1', all=T)
fill$canwrite <- as.list(canwrite)
fill$canwrite$def <- candef$def[candef$vrb=='canwrite']

jsonout <- toJSON(fill, pretty=TRUE, na='null', dataframe='columns')
write(jsonout, file='canadacodes.json')