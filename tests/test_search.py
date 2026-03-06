from app.query import RankingWeights, parse_query


def test_parse_query_extracts_constraints():
    intent = parse_query("tech guy based out of Gurugram with more than 5 years of experience")
    assert intent.location == "gurugram"
    assert intent.min_years_experience == 5.0
    assert "software engineer" in intent.title_intent


def test_weights_sum_reasonable():
    w = RankingWeights()
    total = w.skill + w.title + w.experience + w.location + w.vector + w.keyword
    assert round(total, 5) == 1.0
