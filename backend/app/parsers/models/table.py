from __future__ import annotations
from typing import ClassVar, Dict, TYPE_CHECKING

from ..base import BaseLegModal

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class LegTable(BaseLegModal):
    summary: str
    xml_table: str

    def as_text(self, indent=0) -> str:
        return self.indent(indent, self.summary) + "\n" + self.indent(indent, self.xml_table)

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, "LegTable")
        print("  " * indent, self.summary)
        print("  " * indent, self.xml_table)

    count_by_parent_id: ClassVar[dict[str, int]] = dict()

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'LegTable':
        table = node.find("table")
        if table is None:
            raise Exception("LegTable has no table")
        count = cls.count_by_parent_id.get(parent_chunk_id, 1)
        cls.count_by_parent_id[parent_chunk_id] = count + 1
        chunk_id = f"{parent_chunk_id}, Table {count}"
        return cls(
            summary=node.find("summary").text,
            xml_table=etree.tostring(table, encoding="unicode"),
            chunk_id=chunk_id
        )