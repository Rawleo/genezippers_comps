# Setting up environment
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define file path to dbSNP database
dbSNP_folder_path = "../data/dbSNP/"

for file in os.listdir(dbSNP_folder_path):

    #Only look at chromosomes
    if (file.split(".")[-1] == "txt"):


        path = f"~/Desktop/comps_f25_rgj/dnazip/data/dbSNP/{file}"

        chr_vars = pd.read_csv(path,
                               sep='\t',
                               names=['chrom',
                                'chromStart',
                                'chromEnd',
                                'name',
                                'ref',
                                'altCount',
                                'alts',
                                'shiftBases',
                                'freqSourceCount',
                                'minorAlleleFreq',
                                'majorAllele',
                                'minorAllele',
                                'maxFuncImpact',
                                'varType',
                                'ucscNotes',
                                '_dataOffset',
                                '_dataLen'
                                ]
                              )

        snv_vars = chr_vars.where(chr_vars['varType'] == 'snv').dropna()
        snv_common_vars = snv_vars[snv_vars['ucscNotes'].apply(lambda x: 'commonAll' in str(x).split(','))]
        filterd_snv_cvars = snv_common_vars[['chrom', 'chromStart', 'ref', 'altCount', 'alts']]

        # Given each alternative, make a new entry for it
        filterd_snv_cvars = (filterd_snv_cvars
                  .assign(alt=filterd_snv_cvars['alts'].str.split(','))
                  .explode('alt')
                  .reset_index(drop=True)
                  ) 
        
        # Formatting
        filterd_snv_cvars['chromStart'] = filterd_snv_cvars['chromStart'].astype('Int64')
        filterd_snv_cvars = filterd_snv_cvars.where(filterd_snv_cvars['alt'] != '').dropna()

        filterd_snv_cvars['ref_alt'] = filterd_snv_cvars['ref'] + "/" + filterd_snv_cvars['alt']

        # Rewrite pre-existing file
        filterd_snv_cvars[['chrom', 'chromStart', 'ref_alt']].to_csv(path, 
                                                                      header=None,
                                                                      index=False)
        
        print(f"{file} has been converted to the proper format")

