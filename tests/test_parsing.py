from app.parsing import estimate_years_experience, normalize_location, parse_contact


def test_normalize_location():
    assert normalize_location("Gurgaon") == "gurugram"


def test_parse_contact():
    text = "Email: test@example.com Phone: +1 555-123-4567"
    result = parse_contact(text)
    assert result["email"] == "test@example.com"
    assert "555" in (result["phone"] or "")


def test_estimate_years_experience_explicit():
    assert estimate_years_experience("Has 6 years of experience") == 6.0
