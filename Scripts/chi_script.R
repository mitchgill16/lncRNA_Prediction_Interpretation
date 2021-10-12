### Accepts 3 arguments
# lncRNA motif count
# random motif count
# total sequences

args = commandArgs(trailingOnly=TRUE)

# test if there is at least 3 arguments: if not, return an error
if (length(args)!=3) {
  stop("3 arguments must be supplied. Arg1 = lncrna count, arg2 = random count, arg 3 is total seq (input file).n", call.=FALSE)
}
lncrna_count <- as.integer(args[1])
random_count <- as.integer(args[2])
total <- as.integer(args[3])

lo1 <- total - lncrna_count
lo2 <- total - random_count

obvs <- c(lncrna_count, lo1)
expected <- c(random_count, lo2)
df <- data.frame(obvs,expected)
x = chisq.test(df)
x = x$p.value
print(x)