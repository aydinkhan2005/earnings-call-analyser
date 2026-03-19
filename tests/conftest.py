import nltk

def pytest_configure(config):
    nltk.download("punkt_tab", quiet=True)