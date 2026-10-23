from ovos_bm25_solver import BM25CorpusSolver


def test_indexing_and_querying_write_nothing_to_stderr(capfd):
    solver = BM25CorpusSolver({"lang": "en-US"})
    solver.load_corpus(["the cat sat on the mat", "dogs bark at night", "a cat chased a mouse"])
    results = list(solver.query("cat", k=2))
    err = capfd.readouterr().err
    assert len(results) == 2
    assert "BM25S" not in err and "Split strings" not in err
