# Setting up environment
import os
import pandas as pd
from constants import *

# Column names for dbSNP tables
DBSNP_COLS = [
    'chrom', 'chromStart', 'chromEnd', 'name', 'ref', 'altCount', 'alts',
    'shiftBases', 'freqSourceCount', 'minorAlleleFreq', 'majorAllele',
    'minorAllele', 'maxFuncImpact', 'varType', 'ucscNotes',
    '_dataOffset', '_dataLen'
]

for file in os.listdir(DBSNP_PATH):

    # Only process plain-text chromosome files
    if not file.endswith(".txt"):
        continue

    path = f"{DBSNP_PATH}/{file}"

    # Load table
    df = pd.read_csv(path, sep='\t', names=DBSNP_COLS)

    # Filter SNVs only
    snvs = df[df['varType'] == 'snv']

    # Keep only variants with "commonAll" in ucscNotes
    common_snvs = snvs[snvs['ucscNotes']
                       .astype(str)
                       .str.split(',')
                       .apply(lambda notes: 'commonAll' in notes)]

    # Select needed columns
    common_snvs = common_snvs[['chrom', 'chromStart', 'ref', 'alts']]

    # Split multi-alt into rows
    common_snvs = (
        common_snvs
        .assign(alt=common_snvs['alts'].str.split(','))
        .explode('alt')
        .dropna(subset=['alt'])
        .reset_index(drop=True)
    )

    # Format fields
    common_snvs['chromStart'] = common_snvs['chromStart'].astype('Int64')
    common_snvs['ref_alt'] = common_snvs['ref'] + "/" + common_snvs['alt']

    # Overwrite file with cleaned format
    common_snvs[['chrom', 'chromStart', 'ref_alt']].to_csv(
        path, header=None, index=False
    )

    print(f"{file} has been converted to the proper format")
