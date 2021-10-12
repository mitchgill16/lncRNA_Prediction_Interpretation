# Will go through the top 50 file and return a p value for each motif

#file = "Br_motif_top50.txt"
#total_wo=$(wc -l < random_intervals_flanked_wo.fa)
total=$(wc -l < random_fasta_flanked.fa)
#total="$((total_wo+total_w))"
echo $total
for x in $(cat 'At_motif_top50.txt');
do
#	lncrna_wo=$(grep $x lncRNAs_without_gene_cantata.gff3unique.gff3_flanked.fa | wc -l)
	lncrna=$(grep $x at_lncrna_flanked.fa | wc -l)
#	random_wo=$(grep $x random_intervals_flanked_wo.fa | wc -l)
	random=$(grep $x random_fasta_flanked.fa | wc -l)
#	lncrna="$((lncrna_wo+lncrna_w))"
#	random="$((random_wo+random_w))"
	echo $lncrna
	echo $random
	echo $x >> motif_sigs.txt
	y=$(Rscript chi_script.R $lncrna $random $total)
	echo $y >> motif_sigs.txt
	
done
