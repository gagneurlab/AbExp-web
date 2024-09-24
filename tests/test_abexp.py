from abexp_web.db import get_db


def test_db(app):
    with app.app_context():
        db = get_db()
        assert db is not None
        df = db.execute("""
        SELECT * FROM abexp_veff WHERE
           chrom = 'chr18' AND start = 10472381
           AND "end" = 10472382 AND ref = 'C'
           AND alt = 'T' AND genome = 'hg19' AND tissue = 'Adrenal Gland';
        """).fetchdf()
        assert df.shape[0] == 1
        assert df['abexp_v1.1'].values[0] == -0.003749131589629193

# def test_hello(client):
#     response = client.get('/hello')
#     assert response.data == b'Hello, World!'
