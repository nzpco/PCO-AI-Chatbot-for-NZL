from __future__ import annotations
from typing import List, TYPE_CHECKING
from colorama import Fore, Style

from ..base import BaseLegModal, Container

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class NotRelevant(BaseLegModal):
    xml: str | None = None

    def print(self, indent=0):
        self.print_chunk_id(indent)
        if self.xml:
            print("  " * indent, Fore.RED + self.xml + Style.RESET_ALL)

    def as_text(self, indent=0) -> str:
        return ""

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'NotRelevant':
        return cls(xml=etree.tostring(node, encoding="unicode", pretty_print=True))

class CrossHead(BaseLegModal):
    heading: str

    def as_text(self, indent=0) -> str:
        return "\n" + self.indent(indent, "# " + self.heading) + "\n"

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, "Crosshead: ", self.heading)

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'CrossHead':
        return cls(heading=cls.get_text(node))

class LabelParaCrossHead(CrossHead):
    pass

class LegList(Container):
    pass

class DefPara(Container):
    pass

class End(NotRelevant):
    pass

class Amend(NotRelevant):
    pass

class Contents(NotRelevant):
    pass

