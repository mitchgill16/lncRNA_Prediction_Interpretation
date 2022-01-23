import pandas as pd
import sys
my_file = sys.argv[1]
print(my_file)
col_heads = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", "qstart", "qend", "sstart", "send", "evalue", "bitscore"]
df = pd.read_csv(my_file, sep = "\t", header=None)
df.columns = col_heads
outfile = my_file+"_to_filter.txt"
f = open(outfile, "w")
for index, row in df.iterrows():
   length = row["length"]
   cell = row["qseqid"]
   cell = cell.split(':')
   cell = cell[3].split('-')
   l = int(cell[1]) - int(cell[0])
   l = l*0.9
   if(length >= l):
       f.write(row["qseqid"] + "\n")
f.close()
