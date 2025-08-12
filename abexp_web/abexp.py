from . import utils
import pandas as pd
from .db import get_db
import click

# GENE_MAP = pd.read_csv('data/resources/gene_map.tsv', sep='\t')


def run_abexp(snv_input, tissues, genome, max_score_only):
    db = get_db()

    # Build a small variants DataFrame and perform a set-based join for efficiency
    variant_records = []
    for snv in snv_input:
        chr_name, pos, ref, alt = utils.split_variant(snv)
        variant_records.append({
            'chrom': chr_name,
            'start': pos - 1,  # abexp.start is 0-based
            'ref': ref,
            'alt': alt
        })
    
    if len(variant_records) > 10:
        error_message = "The input must not contain more than 10 variants."
        raise ValueError(error_message)

    if not variant_records:
        # No input variants provided
        df = pd.DataFrame(columns=['variant', 'gene', 'gene_name', 'tissue', 'abexp_score'])
    else:
        variants_df = pd.DataFrame(variant_records)

        # Build UNION ALL subqueries per chromosome for better partition pruning
        chromosome_queries = []
        for chrom in variants_df['chrom'].unique():
            chrom_variants = variants_df[variants_df['chrom'] == chrom]
            variant_conditions = []
            for _, row in chrom_variants.iterrows():
                variant_conditions.append(
                    f"(start = {row['start']} AND ref = '{row['ref']}' AND alt = '{row['alt']}')"
                )
            variants_clause = " OR ".join(variant_conditions)
            
            chromosome_queries.append(f"""
            SELECT *
            FROM abexp a
            WHERE a.genome = '{genome}' 
              AND a.chrom = '{chrom}'
              AND a.tissue IN ({','.join(map(repr, tissues))})
              AND ({variants_clause})
            """)
        
        query = f"""
        SELECT u.*, gm.gene_name
        FROM (
            {" UNION ALL ".join(chromosome_queries)}
        ) u
        LEFT JOIN gene_map gm ON u.gene = gm.gene
        """
        df = db.execute(query).fetchdf()

        if df.shape[0] > 0:
            df = df.assign(
                variant=lambda x: x['chrom'].astype(str) + ':' + (x['start'] + 1).astype(str) + ':' + x['ref'] + '>' + x['alt']
            )
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