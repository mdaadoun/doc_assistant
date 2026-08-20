"""Evaluation domain models for RAG benchmarking and dataset validation."""

from pydantic import Field

from models.base import BaseDomainModel


class EvalGroundTruthCitation(BaseDomainModel):
    """Ground-truth citation reference with source document attribution."""

    file_name: str = Field(..., description="Source document file name")
    page_number: int = Field(default=1, ge=1, description="1-indexed page number")
    chunk_id: str = Field(..., description="Target ground-truth chunk ID")
    excerpt: str = Field(default="", description="Relevant reference excerpt")


class EvalDatasetItem(BaseDomainModel):
    """Annotated evaluation query-answer record for RAG evaluation."""

    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., min_length=1, description="Evaluation user query")
    ground_truth_answer: str = Field(
        ..., min_length=1, description="Expected ground-truth response"
    )
    ground_truth_citations: list[EvalGroundTruthCitation] = Field(
        default_factory=list, description="Supporting ground-truth citations"
    )
    is_out_of_corpus: bool = Field(
        default=False,
        description="Whether query is out-of-corpus expecting refusal",
    )
    category: str = Field(
        default="general",
        description="Domain category e.g. hr_policy, sla, legal, out_of_corpus",
    )


class EvalDataset(BaseDomainModel):
    """Collection container for validated evaluation dataset records."""

    items: list[EvalDatasetItem] = Field(
        default_factory=list, description="List of evaluation dataset items"
    )
    version: str = Field(
        default="1.0.0", description="Dataset schema and content version"
    )

    @property
    def total_queries(self) -> int:
        """Return total count of queries in dataset."""
        return len(self.items)

    @property
    def out_of_corpus_count(self) -> int:
        """Return count of out-of-corpus queries in dataset."""
        return sum(1 for item in self.items if item.is_out_of_corpus)

    @property
    def in_corpus_count(self) -> int:
        """Return count of in-corpus queries in dataset."""
        return sum(1 for item in self.items if not item.is_out_of_corpus)
