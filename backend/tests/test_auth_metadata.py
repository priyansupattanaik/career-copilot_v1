from app.auth import _metadata_full_name


def test_metadata_full_name_from_sign_up():
    assert _metadata_full_name({"user_metadata": {"full_name": "Priya Sharma"}}) == "Priya Sharma"


def test_metadata_full_name_fallback_keys():
    assert _metadata_full_name({"user_metadata": {"name": "Alex"}}) == "Alex"
    assert _metadata_full_name({"user_metadata": {"fullName": "Sam"}}) == "Sam"


def test_metadata_full_name_empty():
    assert _metadata_full_name({}) is None
    assert _metadata_full_name({"user_metadata": {}}) is None
    assert _metadata_full_name({"user_metadata": {"full_name": "  "}}) is None
