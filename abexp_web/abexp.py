from . import utils
import pandas as pd
from .db import get_db

# GENE_MAP = pd.read_csv('data/resources/gene_map.tsv', sep='\t')


def run_abexp(snv_input, max_score_only, tissues, extra_info):
    path_to_prec = f'data/resources/precomputed/absplice/{genome}/multisample/'

    variants_to_run = []
    df_list = []

    # todo
    gtf = gffutils.FeatureDB('data/resources/gencode.hg19.annotation.db')

    # run the tool or retrieve precomputed scores for each variant in the input
    for snv in snv_input:

        chr_name, pos, ref, alt = utils.split_variant(snv)

        if len(alt) > 1 or extra_info:
            variants_to_run.append(snv)
        else:
            gene_ids = utils.get_ensembl_gene_id(f"chr{chr_name}", pos, gtf)

            result = []

            for gene_id in gene_ids:
                # todo
                res = get_precomputed_scores_from_vcf(chr_name, pos, ref, alt, gene_id, tissues, path_to_prec)

                if res.shape[0] == 0:
                    continue
                result.append(res)
            df_list += result

    df_final = pd.concat(df_list).round(2).sort_values(by=['variant', 'AbSplice_DNA'], ascending=[True, False])
    del df_list

    # prepare output for html rendering
    expected_order = ['variant', 'gene_id', 'AbSplice_DNA', 'tissue', 'delta_psi', 'delta_score']
    df_final = df_final[expected_order]

    # todo Add gene names to the output
    return df_final
