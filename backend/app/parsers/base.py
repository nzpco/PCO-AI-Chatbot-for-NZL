from __future__ import annotations
from lxml import etree
from pydantic import BaseModel
from typing import ClassVar, TYPE_CHECKING
from colorama import Fore, Style
from beanie.operators import Set

from ..db.models import LegislationDocument, LegislationFragment

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

class HeirarchyContext(BaseModel):
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

    def print(self):
        print("From:")
        if self.act_name:
            print(f"  Act: {self.act_name} ({self.act_year} no. {self.act_number})")
        if self.schedule_name:
            print(f"  Schedule: ({self.schedule_label}) {self.schedule_name} ")
        if self.part_name:
            print(f"  Part: ({self.part_label}) {self.part_name}")
        if self.subpart_name:
            print(f"  Subpart: ({self.subpart_label}) {self.subpart_name}")
        if self.crosshead_name:
            print(f"  Heading: {self.crosshead_name}")
        if self.section_name:
            print(f"  Section: ({self.section_label}) {self.section_name}")
        if len(self.paragraph_label) > 0:
            print(f"  Paragraph: ({'), ('.join(self.paragraph_label)})")

    def add_sibling_context(self, model: "BaseLegModal") -> "HeirarchyContext":
        node_type = model.node_type()
        if node_type == "CrossHead":
            return self.model_copy(update={
                "crosshead_name": model.heading,
            })
        return self

    def add_child_context(self, model: "BaseLegModal") -> "HeirarchyContext":
        node_type = model.node_type()
        if node_type == "Act":
            return self.model_copy(update={
                "act_name": model.title,
                "act_number": model.no,
                "act_year": model.year
            })
        elif node_type == "Part":
            return self.model_copy(update={
                "part_name": model.heading,
                "part_label": model.label,
                "section_name": None,
                "section_label": None,
                "subpart_name": None,
                "subpart_label": None,
                "crosshead_name": None,
                "paragraph_label": [],
            })
        elif node_type == "Subpart":
            return self.model_copy(update={
                "subpart_name": model.heading,
                "subpart_label": model.label,
                "section_name": None,
                "section_label": None,
                "crosshead_name": None,
                "paragraph_label": [],
            })
        elif node_type == "Section":
            return self.model_copy(update={
                "section_name": model.heading,
                "section_label": model.label,
                "paragraph_label": [],
            })
        elif node_type == "Schedule":
            return self.model_copy(update={
                "schedule_name": model.heading,
                "schedule_label": model.label,
                "part_name": None,
                "part_label": None,
                "subpart_name": None,
                "subpart_label": None,
                "section_name": None,
                "section_label": None,
                "crosshead_name": None,
                "paragraph_label": [],
            })
        elif node_type == "LabelPara":
            return self.model_copy(update={
                "paragraph_label": self.paragraph_label + [model.label],
            })
        return self

class BaseLegModal(BaseModel):
    chunk_id: str | None = None
    order_counter: ClassVar[int] = 0
    order: int

    def __init__(self, **data):
        order = BaseLegModal.order_counter
        BaseLegModal.order_counter += 1
        super().__init__(**data, order=order)

    @classmethod
    def reset_order(cls):
        cls.order_counter = 0

    def print_chunk_id(self, indent=0):
        if self.chunk_id:
            print("  " * indent, Fore.GREEN + self.chunk_id + Style.RESET_ALL)

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, self)

    def node_type(self) -> str:
        return self.__class__.__name__

    async def generate_fragments(self, document: LegislationDocument, parent_fragment: Optional[LegislationFragment] = None, context: "HeirarchyContext" = HeirarchyContext()):
        child_context = context.add_child_context(self)
        if self.chunk_id is not None:
            fields = self.model_dump()
            fragment_data = {
                "chunk_id": self.chunk_id,
                "order": self.order,
                "text": self.as_text(),
                "document": document,
                "parent_fragment": parent_fragment,
                "fragment_type": self.node_type(),
                "fragment_label": fields.get("label", None),
                "descriptive_label": fields.get("descriptive_label", None),
                "heading": fields.get("heading", fields.get("title", None)),
                **context.model_dump()
            }

            # Delete any existing fragment with this chunk_id
            await LegislationFragment.find(
                LegislationFragment.chunk_id == self.chunk_id
            ).delete()

            # Create and save new fragment
            fragment = LegislationFragment(**fragment_data)
            await fragment.save()
        else:
            fragment = parent_fragment
        for child in self.children():
            child_context = child_context.add_child_context(child)
            await child.generate_fragments(document, fragment, child_context)

    def generate_nodes(self, store: dict[str, list[dict]] = None, context: "HeirarchyContext" = HeirarchyContext()):
        if store is None:
            store = {}

        child_context = context.add_child_context(self)
        if self.chunk_id is not None:
            type = self.node_type()
            store.setdefault(type, []).append({
                "chunk_id": self.chunk_id,
                "order": self.order,
                "text": self.as_text(),
                "context": child_context
            })
        for child in self.children():
            if context:
                child_context = child_context.add_sibling_context(child)
            child.generate_nodes(store, child_context)
        return store

    def indent(self, indent=0, string=""):
        return "  " * indent + string

    def children(self) -> list["BaseLegModal"]:
        return []

    @staticmethod
    def get_text(node: etree.Element) -> str:
        if node is None:
            return ""
        return etree.tostring(node, encoding="unicode", method="text")

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'BaseLegModal':
        pass

class Container(BaseLegModal):
    contents: list["BaseLegModal"]
    type: str

    def print(self, indent=0):
        self.print_chunk_id(indent)
        for child in self.contents:
            child.print(indent=indent+1)

    def as_text(self, indent=0) -> str:
        return "\n".join([child.as_text(indent=indent) for child in self.contents])

    def children(self) -> list["BaseLegModal"]:
        return self.contents

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'Container':
        children = parser.parse_children(node, parent_chunk_id=parent_chunk_id)
        return cls(contents=children, type=node.tag)

class LabeledContainer(Container):
    label: str
    descriptive_label: str
    heading: str
    deletion_status: str | None

    def print(self, indent=0):
        self.print_chunk_id(indent)
        print("  " * indent, f"{self.__class__.__name__}: {self.label} {self.heading}")
        if self.deletion_status:
            print("  " * indent, Fore.BLUE + "[", self.deletion_status, "]" + Style.RESET_ALL)
        self._print_contents(indent)

    def _print_contents(self, indent):
        for child in self.contents:
            child.print(indent=indent+1)

    def as_text(self, indent=0) -> str:
        s = self.indent(indent, f"{self.descriptive_label}: {self.heading}\n")
        if self.deletion_status:
            s += self.indent(indent, f"\n [{self.deletion_status}]")
        s += "\n".join([child.as_text(indent=indent+1) for child in self.children()])
        return s

    @classmethod
    def _descriptive_label(cls, label: str) -> str:
        return f"{cls.__name__} {label}"

    @classmethod
    def _parse_label_and_heading(cls, node: etree.Element, parent_chunk_id: str | None = None) -> tuple[str, str, str]:
        label = cls.get_text(node.find("label"))
        heading = cls.get_text(node.find("heading"))
        descriptive_label = cls._descriptive_label(label)
        chunk_id = f"{parent_chunk_id}, {descriptive_label}"
        return label, descriptive_label, heading, chunk_id

    @classmethod
    def _parse_children(cls, node: etree.Element, parser: XMLParser, chunk_id: str | None = None) -> list["BaseLegModal"]:
        children = parser.parse_children(node, ignore_keys=["label", "heading"], parent_chunk_id=chunk_id)
        return children

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'LabeledContainer':
        label, descriptive_label, heading, chunk_id = cls._parse_label_and_heading(node, parent_chunk_id)
        children = cls._parse_children(node, parser, chunk_id)
        return cls(
            label=label,
            descriptive_label=descriptive_label,
            heading=heading,
            contents=children,
            deletion_status=node.get("deletion-status"),
            type=node.tag,
            chunk_id=chunk_id
        )
