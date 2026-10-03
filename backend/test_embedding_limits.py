import unittest
import sys
from types import SimpleNamespace

sys.modules.setdefault("chromadb", SimpleNamespace(PersistentClient=None))
sys.modules.setdefault("dotenv", SimpleNamespace(load_dotenv=lambda: None))
sys.modules.setdefault("docx", SimpleNamespace(Document=None))
sys.modules.setdefault("markdown", SimpleNamespace(markdown=lambda text: text))
sys.modules.setdefault("pypdf", SimpleNamespace(PdfReader=None))
sys.modules.setdefault("sentence_transformers", SimpleNamespace(SentenceTransformer=None))

from rag_pipeline import EmbeddingTokenLimitError, RAGEngine


class FakeTokenizer:
    model_max_length = 10
    last_call = None

    def __call__(
        self,
        texts,
        add_special_tokens=True,
        truncation=False,
        padding=False,
    ):
        self.last_call = {
            "add_special_tokens": add_special_tokens,
            "truncation": truncation,
            "padding": padding,
        }
        input_ids = []
        for text in texts:
            tokens = text.split()
            if add_special_tokens:
                tokens = ["[CLS]", *tokens, "[SEP]"]
            input_ids.append(list(range(len(tokens))))
        return {"input_ids": input_ids}


class FakeEmbedder:
    tokenizer = FakeTokenizer()

    def get_max_seq_length(self):
        return 5


def make_engine():
    engine = RAGEngine.__new__(RAGEngine)
    engine.embedder = FakeEmbedder()
    engine.embedding_model_name = "fake-embedder"
    engine.embedding_token_limit = engine._detect_embedding_token_limit()
    return engine


class EmbeddingTokenLimitTests(unittest.TestCase):
    def test_embedding_token_limit_uses_model_sequence_length(self):
        engine = make_engine()

        self.assertEqual(engine.embedding_token_limit, 5)

    def test_embedding_token_limit_rejects_over_limit_text(self):
        engine = make_engine()

        with self.assertRaises(EmbeddingTokenLimitError):
            engine._validate_embedding_token_limits(["one two three four"], "Query")

    def test_embedding_token_limit_allows_within_limit_text(self):
        engine = make_engine()

        engine._validate_embedding_token_limits(["one two three"], "Query")

    def test_embedding_token_count_uses_exact_model_tokenizer_without_truncation(self):
        engine = make_engine()

        token_counts = engine._count_embedding_tokens(["one two three"])

        self.assertEqual(token_counts, [5])
        self.assertEqual(
            engine.embedder.tokenizer.last_call,
            {
                "add_special_tokens": True,
                "truncation": False,
                "padding": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
