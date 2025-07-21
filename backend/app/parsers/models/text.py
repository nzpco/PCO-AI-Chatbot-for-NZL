from __future__ import annotations
from typing import List, TYPE_CHECKING

from ..base import BaseLegModal

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class TextContent(BaseLegModal):
    text: str | None = None

    def as_text(self, indent=0) -> str:
        return self.indent(indent, self.text or "")

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, self.text)

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'TextContent':
        return cls(text=cls.get_text(node))

class Text(TextContent):
    pass

class Citation(TextContent):
    pass

class AdminOffice(TextContent):
    pass