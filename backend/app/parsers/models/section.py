from __future__ import annotations
from typing import List, TYPE_CHECKING

from colorama import Fore, Style

from ..base import BaseLegModal, LabeledContainer
from .paragraph import Paragraph, Example
from .notes import Notes
from .text import Citation
from .misc import CrossHead

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class NotesContainer:
    @classmethod
    def _parse_notes(cls, node: etree.Element, parser: XMLParser, chunk_id: str) -> "Notes | None":
        note_node = node.find("notes")
        if note_node is not None:
            return parser.parse_node(note_node, parent_chunk_id=chunk_id)
        return None

class Section(LabeledContainer, NotesContainer):
    contents: list["Subsection | CrossHead | Paragraph | Example"]
    notes: "Notes | None"
    citations: list["Citation"]

    def children(self) -> list["BaseLegModal"]:
        notes = [self.notes] if self.notes is not None else []
        return self.contents + notes + self.citations

    def as_text(self, indent=0) -> str:
        s = self.indent(indent, f"{self.label}: {self.heading}\n")
        if self.deletion_status:
            s += self.indent(indent, f"\n [{self.deletion_status}]")
        s += "\n".join([child.as_text(indent=indent+1) for child in self.children()])
        return s

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'Section':
        label, descriptive_label, heading, chunk_id = cls._parse_label_and_heading(node, parent_chunk_id)

        children = parser.parse_children(node.find("prov.body"), parent_chunk_id=chunk_id)
        cf = node.find("cf")
        citations = parser.parse_children(cf, parent_chunk_id=chunk_id) if cf is not None else []
        notes = cls._parse_notes(node, parser, chunk_id)

        parser.parse_children(node, ignore_keys=["label", "heading", "prov.body", "cf", "notes"])

        return cls(
            label=label,
            descriptive_label=descriptive_label,
            heading=heading,
            notes=notes,
            citations=citations,
            contents=children,
            deletion_status=node.get("deletion-status"),
            chunk_id=chunk_id,
            type=node.tag
        )

class Subsection(BaseLegModal, NotesContainer):
    label: str | None
    paragraph: "Paragraph | None"
    examples: list["Example"]
    notes: "Notes | None"
    deletion_status: str | None

    def children(self) -> list["BaseLegModal"]:
        children = []
        if self.paragraph is not None:
            children.append(self.paragraph)
        children.extend(self.examples)
        if self.notes is not None:
            children.append(self.notes)
        return children

    def print(self, indent=0):
        self.print_chunk_id(indent)
        if self.label:
            print("  " * indent, self.label)
        if self.deletion_status:
            print("  " * indent, Fore.BLUE + "[", self.deletion_status, "]" + Style.RESET_ALL)
        for child in self.children():
            child.print(indent=indent+1)

    def as_text(self, indent=0) -> str:
        next_indent = indent
        if self.label:
            s = self.indent(indent, self.label + '. ')
            next_indent += 1
        else:
            s = ""
        if self.deletion_status:
            s += self.indent(indent, f"\n [{self.deletion_status}] ")
        s += ("\n".join([child.as_text(indent=next_indent) for child in self.children()])).strip()
        return s

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'SubSection':
        para = node.find("para")
        label = cls.get_text(node.find("label"))
        chunk_id = f"{parent_chunk_id}, Subsection ({label})" if label else parent_chunk_id

        examples = parser.parse_children(node, ignore_keys=["label", "para", "notes"], parent_chunk_id=chunk_id)
        notes = cls._parse_notes(node, parser, chunk_id)
        paragraph = parser.parse_node(para, parent_chunk_id=chunk_id) if para is not None else None

        return cls(
            label=label,
            paragraph=paragraph,
            examples=examples,
            notes=notes,
            deletion_status=node.get("deletion-status"),
            chunk_id=chunk_id if label else None
        )