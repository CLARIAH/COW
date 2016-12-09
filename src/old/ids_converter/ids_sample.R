rm(list=ls())

library("data.table")

sample_id = function(id, share=0.01){
    id_unq = unique(id)
    return(sample(id_unq, size=length(id_unq) * share, replace=F))
}

sedd = data.table::fread('~/Downloads/data/qqt/Complete_SEDD-IDS_PUBLIC_3_1/SEDD-IDS_PUBLIC_3_1.txt')

sampled = sample_id(sedd$V1, share=0.001)
sedd_smpld = sedd[V1 %in% sampled, ]
write.csv(sedd_smpld, '~/downloads/data/qqt/Complete_SEDD-IDS_PUBLIC_3_1/Complete_SEDD-IDS_PUBLIC_3_1_smpl.csv', row.names=F)