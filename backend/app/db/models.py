from typing import List, Optional, Dict, Any
from beanie import Document, Indexed, Link
from pydantic import Field, computed_field

class LegislationFragment(Document):
    """MongoDB document model for legislation fragments"""
    chunk_id: Indexed(str, unique=True)
    order: int
    fragment_type: str
    fragment_label: str | None = None
    descriptive_label: str | None = None

    summary: str | None = None
    summary_long: str | None = None
    summary_context: str | None = None

    embedding: list[float] | None = None

    act_name: str | None = None
    act_number: str | None = None
    act_year: str | None = None

    schedule_label: str | None = None
    schedule_name: str | None = None

    part_label: str | None = None
    part_name: str | None = None

    subpart_label: str | None = None
    subpart_name: str | None = None

    crosshead_name: str | None = None

    section_label: str | None = None
    section_name: str | None = None

    paragraph_label: list[str] = []

    heading: str | None = None
    text: str
    xml: str | None = None

    document: Link["LegislationDocument"] = Field(default=None, ref_type="LegislationDocument")
    parent_fragment: Link["LegislationFragment"] = Field(default=None, ref_type="LegislationFragment")

    @computed_field
    @property
    def token_count(self) -> int:
        """Count the number of tokens in the text field.
        This is a simple implementation that splits on whitespace.
        For more accurate token counting, you might want to use a proper tokenizer."""
        return len(self.text.split())

    class Settings:
        name = "legislation_fragments"
        indexes = [
            "chunk_id",
            "order",
            "document_id",
            "fragment_type",
            "fragment_label",
            "descriptive_label",
            "title",
            "parent_fragment_id"
        ]

class LegislationDocument(Document):
    """MongoDB document model for the main legislation act"""
    title: str
    year: str
    type: str
    id: str
    no: str
    date_assent: str
    date_as_at: str
    administered_by: Optional[str]

    class Settings:
        name = "legislation_documents"
        indexes = [
            "year",
            "type",
            "administered_by"
        ]