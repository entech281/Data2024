import team_analysis
import pandas as pd

def test_that_tests_run():
    pass

def test_loading_raw_data():
    (analyzed, summary) = team_analysis.load_2024_data()
    assert 37 == len(analyzed)
    assert 32 == len(summary)
