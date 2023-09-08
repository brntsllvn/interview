from src.domain.hello import say_hello


def test_pandas():
    assert say_hello() == "hello"
