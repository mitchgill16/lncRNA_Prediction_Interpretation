# lncRNA_Prediction_Interpretation
Notebooks, Data and Scripts for lncRNA Prediction &amp; Interpretation

Preprint: https://doi.org/10.1101/2022.02.09.479647 

Each folder is for a given crop.
at = Arabidopsis thaliana
bn = Brassica napus
bo = Brassica oleracea
br = Brassica rapa
gm = Glycine max
os = Oryza sativa
zm = Zea mays

In each folder is a notebook which will be able to finetune a pretrained BERT model which has been installed following the instructions at the DNABERT repository (https://github.com/jerryji1993/DNABERT) for dnalong models. There were a couple changes made for interpretation, so if you eventually want to use the transformers interpret section of the notebook replace the modeling_bert.py file in your installation with the modeling_bert.py file in the scripts folder of this repository.
There will also be 2x fasta files. One fasta file is lncrna sequences specific to the given crop acquired from the cantataDB2.0 database (http://cantata.amu.edu.pl/download.php). The pipeline to generate this data was as follows: Download the relevant gtf file --> use the add_flanks.py script (to add 500bp either side of the lncrna) --> use bedtools get fasta for the reference genome on cantataDB2.0 and the flanked lncrna gtf file to generate crop specific lncrna flanked fasta--> use bedtools shuffle on the flanked gtf file to randomise the same intervals throughout the genome --> use bedtools get fasta to gnerate random fasta sequences.
You can follow the same pipeline if you'd like to finetune a DNABERT model for a different crop.

After finetuning models you can interpret the models by installing the transformers interpret package (https://github.com/cdpierse/transformers-interpret). For my finetuning of DNABERT I set the max sequence length to 2048, which isn't compatible to the standard transformers max seq length of 512. If you have changed to the max seq length (in 512 intervals as dictated by the DNABERT repo for dnalong models) replace the attributions.py and explainer.py in the installation folder of transformers interpret with the respective files in the scripts folder of this repo. I would recommend having your max seq length as 2048 as these changes Ive made were specific to 2048. If you did a different max length you would have to change my code which reshapes pytorch tensors to (4,512) etc.
There is also a do_chi_motifs.sh script which utilises the chi_script.R script to return a list of motifs and their significant value. This is ran after the motifs have been generated in the relevant jupyter notebook. The general script is for at (Arabidopsis thaliana).
