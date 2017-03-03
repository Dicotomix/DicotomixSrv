#dico = dictionnary
dico <- read.csv("LexiqueComplet.csv", header=F, sep=";")
colnames(dico) <- c("word", "root", "type", "root_freq_movie", "root_freq_books", "word_freq_movie", "word_freq_books")

head(dico, 20)


#keep only root data (remove two last cols)

dico$word_freq_movie <- NULL
dico$word_freq_books <- NULL

head(dico,20)

#kept in case it is needed later
#get only one root
#dico.filtered <- unique(dico[2:5])


#normalize movie and books
dico.norm <- dico
dico.norm$root_freq_movie <- dico$root_freq_movie/sum(dico$word_freq_movie)
dico.norm$root_freq_books <- dico$root_freq_books/sum(dico$word_freq_books)
dico.norm$word_freq_movie <- dico$word_freq_movie/sum(dico$word_freq_movie)
dico.norm$word_freq_books <- dico$word_freq_books/sum(dico$word_freq_books)



#df for dico final
df <- dico.norm[,1:3]
df$root_freq <- (dico.norm$root_freq_movie + dico.norm$root_freq_books)/2
df$word_freq <- (dico.norm$word_freq_movie + dico.norm$word_freq_books)/2


head(df)

#range it better
factor <- 10000000
df$root_freq <- df$root_freq * factor
df$word_freq <- df$word_freq * factor

#just checking
df[which.max(df$root_freq),]
df[which.min(df$root_freq),]

df[which.max(df$word_freq),]
df[which.min(df$word_freq),]


#export
write.table(df, "LexiqueCompletPretraite.csv", row.names = F, quote=F, sep=";")
