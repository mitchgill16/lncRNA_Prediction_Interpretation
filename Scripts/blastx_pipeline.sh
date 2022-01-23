#Arg1 = cds of a crop to make the database for blast
#Arg2 = original 'lncrna' fastas to be filtered
cds=$1
query=$2
makeblastdb -dbtype nucl -in $cds
blastn -query $query -db $1 -outfmt 6 -evalue 1e-10 > blast_results.txt
python extract_blast.py blast_results.txt
uniq blast_results.txt_to_filter.txt > transcripts_to_filter.txt      
awk 'BEGIN{while((getline<"transcripts_to_filter.txt")>0)l[">"$1]=1}/^>/{f=!l[$1]}f' $2 > transcripts_filtered.fa
wc -l $2
wc -l transcripts_filtered.fa
wc -l transcripts_to_filter.txt
