#add flanks to gff3 and gtf files

#arg1 is the filename to add flanks to
#arg2 is the size of flanks
#arg3 is a genome file which descirbes length of chromosomes

import pandas as pd
import numpy as np
import copy
import sys

fn = str(sys.argv[1])
flank_size = int(sys.argv[2])
gfile = str(sys.argv[3])
f = pd.read_csv(fn, delimiter="\t", header=None)
size = f.shape[0]
i = 0
gf = pd.read_csv(gfile, delimiter="\t", header=None)
print(gf)
print(gf.shape)
while( i < size):
   #print(str(f[3][i]) + " : " + str(f[4][i]))
   start = copy.deepcopy((f[3][i]))
   end = copy.deepcopy((f[4][i]))
   new_start = start-flank_size
   new_end = end + flank_size
   chr = f[0][i]
  # print(str(chr))
   if(new_start < 0):
       f[3][i] = 1
   else:
       f[3][i] = new_start
   f[4][i] = new_end
   for x in range(0,gf.shape[0]):
       if((gf[0][x] == chr) and (new_end>gf[1][x])):
           xyz = copy.deepcopy(gf[1][x])
           print(str(xyz))
           f[4][i] = xyz
   #print(str(f[3][i]) + " : " + str(f[4][i]))
   i = i + 1
#print(f[3][1])
f.to_csv("flanks_"+str(flank_size)+"_"+fn, sep="\t", index=False, header = False)
