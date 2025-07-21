from __future__ import annotations
from typing import List, ClassVar, Dict, TYPE_CHECKING
from ..base import BaseLegModal, Container
from .text import TextContent

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class Notes(BaseLegModal):
    contents: list["HistoryNote | AmendsNote | History | EditorialNote"]

    def as_text(self, indent=0) -> str:
        s = self.indent(indent, "-- Notes --\n")
        s += "\n".join([child.as_text(indent=indent) for child in self.contents])
        s += "\n" + self.indent(indent, "-----------\n")
        return s

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, "Notes")
        for child in self.contents:
            child.print(indent=indent+1)

    count_by_parent_id: ClassVar[dict[str, int]] = dict()

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'Notes':
        count = cls.count_by_parent_id.get(parent_chunk_id, 1)
        cls.count_by_parent_id[parent_chunk_id] = count + 1
        chunk_id = f"{parent_chunk_id}, Notes {count}"
        children = parser.parse_children(node, parent_chunk_id=chunk_id)
        return cls(contents=children, chunk_id=chunk_id)

class HistoryNote(TextContent):
    pass

class AmendsNote(TextContent):
    pass

class History(Container):
    pass

class EditorialNote(TextContent):
    pass