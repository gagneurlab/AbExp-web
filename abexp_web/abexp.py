from . import utils
import pandas as pd
import duckdb
from .db import get_db
import click

# GENE_MAP = pd.read_csv('data/resources/gene_map.tsv', sep='\t')


def run_abexp(snv_input, tissues, genome, max_score_only):
    db = get_db()
    tissue_list = ",".join([f"'{t}'" for t in tissues])

    all_dfs = []
    
    for snv in snv_input:
        chr_name, pos, ref, alt = utils.split_variant(snv)
        
        df = db.execute(f"""
        SELECT * FROM (
            SELECT * FROM abexp 
            WHERE genome = '{genome}' AND 
                tissue IN ({tissue_list}) AND
                chrom = '{chr_name}' AND
                start = {pos - 1} AND
                ref = '{ref}' AND
                alt = '{alt}'
        ) a LEFT JOIN gene_map ON a.gene = gene_map.gene;
        """).fetchdf()
        
        if df.shape[0] > 0:
            df = df.assign(
                variant=lambda x: x['chrom'].astype(str) + ':' + (x['start'] + 1).astype(str) + ':' + x['ref'] + '>' + x['alt']
            )
            all_dfs.append(df)
    
    if all_dfs:
        df = pd.concat(all_dfs, ignore_index=True)
    else:
        df = pd.DataFrame(columns=['variant', 'gene', 'gene_name', 'tissue', 'abexp_score'])

    if df.shape[0] != 0:
        if max_score_only:
            df = df.assign(abs_abexp_score=df['abexp_score'].abs())
            max_values = df.groupby(['variant', 'gene'])['abs_abexp_score'].max().reset_index()
            df_max = pd.merge(df, max_values, on=['variant', 'gene', 'abs_abexp_score'], how='inner').drop_duplicates(
                subset=['variant', 'gene'])
            df_max['tissue'] = 'Max score over tissues'
            del df_max['abs_abexp_score']
            df = df_max

    expected_order = ['variant', 'gene', 'gene_name', 'tissue', 'abexp_score']
    df = df.round(5).sort_values(by=['variant', 'abexp_score'], ascending=[True, True])[expected_order]

    return df


def get_tissues():
    db = get_db()
    tissues = db.execute("SELECT enum_range(NULL::tissue) AS tissue;").fetchone()[0]
    return tissues