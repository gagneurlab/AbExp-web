from abexp_web.db import get_db
from abexp_web.abexp import run_abexp


def test_db(app):
    with app.app_context():
        db = get_db()
        assert db is not None
        df = db.execute("""
        SELECT * FROM abexp WHERE
           chrom = 'chr18' AND start = 10472381
           AND ref = 'C' AND alt = 'T' AND genome = 'hg19' AND tissue = 'Adrenal Gland';
        """).fetchdf()
        assert df.shape[0] == 1
        assert df['abexp_score'].values[0] == -0.003749131589629193


def test_run_abexp(app):
    with app.app_context():
        df = run_abexp(['chr18:10472382:C>T', 'chr18:10472382:C>A'], ['Adrenal Gland'], 'hg19', False)
        print(df)
        assert df.shape[0] == 2
        assert list(df.columns) == ['variant', 'gene', 'gene_name', 'tissue_type', 'tissue', 'abexp_score']
        df = run_abexp(['chr18:10372382:C>T'], ['Adrenal Gland'], 'hg19', False)
        print(df)
        assert df.shape[0] == 0
        assert list(df.columns) == ['variant', 'gene', 'gene_name', 'tissue_type', 'tissue', 'abexp_score']
