from __future__ import annotations
from typing import List, TYPE_CHECKING

from colorama import Fore, Style

from ..base import BaseLegModal
from .text import Text
from .notes import Notes
from .table import LegTable
from .misc import Container, LabelParaCrossHead, NotRelevant

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class Paragraph(Container):
    contents: list["Text | LabelPara | Example | Container | LegTable | Notes | NotRelevant | LabelParaCrossHead"]

class LabelPara(BaseLegModal):
    label: str | None
    para: "Paragraph"
    deletion_status: str | None

    def children(self) -> list["BaseLegModal"]:
        return [self.para]

    def as_text(self, indent=0) -> str:
        s = ""
        next_indent = indent
        if self.label:
            s += self.indent(indent, self.label + ": ")
            next_indent += 1
        if self.deletion_status:
            s += self.indent(indent, f" [{self.deletion_status}]")
        s += ("\n".join([child.as_text(indent=next_indent) for child in self.children()])).strip()
        return s

    def print(self, indent=0):
        self.print_chunk_id(indent)
        if self.label:
            print("  " * indent, self.label + ":")
        if self.deletion_status:
            print("  " * indent, Fore.BLUE + "[", self.deletion_status, "]" + Style.RESET_ALL)
        for child in self.children():
            child.print(indent=indent+1)

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'LabelPara':
        label = cls.get_text(node.find("label"))
        label = None if label == "" else label
        if label is not None:
            chunk_id = f"{parent_chunk_id}, ({label})"
            next_chunk_id = chunk_id
        else:
            chunk_id = None
            next_chunk_id = parent_chunk_id
        children = parser.parse_children(node, ignore_keys=["label", "para"], parent_chunk_id=next_chunk_id)
        if len(node.findall("para")) > 1:
            raise Exception("LabelPara has more than one para")
        return cls(
            label=label,
            para=parser.parse_node(node.find("para"), parent_chunk_id=next_chunk_id),
            deletion_status=node.get("deletion-status"),
            chunk_id=chunk_id
        )

class HeadingPara(BaseLegModal):
    heading: str | None
    content: list["Paragraph"]

    def as_text(self, indent=0) -> str:
        s = self.indent(indent, self.heading)
        s += "\n" + "\n".join([child.as_text(indent=indent) for child in self.content])
        return s

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, self.heading)
        for child in self.content:
            child.print(indent=indent+1)

    def children(self) -> list["BaseLegModal"]:
        return self.content

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'HeadingPara':
        children = parser.parse_children(node, ignore_keys=["heading"], parent_chunk_id=parent_chunk_id)
        return cls(heading=cls.get_text(node.find("heading")), content=children)

class Example(HeadingPara):
    pass