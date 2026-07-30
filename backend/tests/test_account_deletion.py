from app.account_deletion import CONFIRM_PHRASE, confirmation_is_valid, email_matches_account


def test_confirm_phrase_constant():
    assert CONFIRM_PHRASE == "DELETE MY ACCOUNT"


def test_confirmation_is_valid():
    assert confirmation_is_valid("DELETE MY ACCOUNT")
    assert confirmation_is_valid("  DELETE MY ACCOUNT  ")
    assert not confirmation_is_valid("delete my account")
    assert not confirmation_is_valid("")
    assert not confirmation_is_valid(None)


def test_email_matches_account():
    assert email_matches_account(None, "a@b.com")
    assert email_matches_account("", "a@b.com")
    assert email_matches_account("A@B.com", "a@b.com")
    assert not email_matches_account("other@b.com", "a@b.com")
    assert not email_matches_account("a@b.com", None)
