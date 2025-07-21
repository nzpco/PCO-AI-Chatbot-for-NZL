from __future__ import annotations
from typing import List, TYPE_CHECKING

from ..base import BaseLegModal, LabeledContainer, Container
from .part import Part
from .text import Citation
from .misc import Contents
from .paragraph import HeadingPara

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class Schedule(LabeledContainer):
    contents: list["Part | ScheduleProvisions | ScheduleAmendments | ScheduleAmendmentsGroup1 | ScheduleAmendmentsGroup2 | ScheduleMisc | Contents"]
    empowering_prov: list["Citation"]

    def children(self) -> list["BaseLegModal"]:
        return self.contents + self.empowering_prov

    def as_text(self, indent=0) -> str:
        s = self.indent(indent, f"{self.label}: {self.heading}\n")
        if self.deletion_status:
            s += self.indent(indent, f"\n [{self.deletion_status}] ")
        s += "\n".join([child.as_text(indent=indent+1) for child in self.contents])
        return s

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'Schedule':
        label, descriptive_label, heading, chunk_id = cls._parse_label_and_heading(node, parent_chunk_id)
        contents = parser.parse_children(node, ignore_keys=["label", "heading", "empowering-prov", "notes"], parent_chunk_id=chunk_id)

        note_node = node.find("notes")
        if note_node is not None:
            notes = parser.parse_node(note_node, parent_chunk_id=chunk_id)
        else:
            notes = None

        empowering_prov_node = node.find("empowering-prov")
        if empowering_prov_node is not None:
            empowering_prov = parser.parse_children(empowering_prov_node, parent_chunk_id=chunk_id)
        else:
            empowering_prov = []

        return cls(
            label=label,
            descriptive_label=descriptive_label,
            heading=heading,
            notes=notes,
            empowering_prov=empowering_prov,
            contents=contents,
            deletion_status=node.get("deletion-status"),
            chunk_id=chunk_id,
            type=node.tag
        )

class ScheduleAmendments(Container):
    pass

class ScheduleAmendmentsGroup1(Part):
    contents: list["ScheduleAmendmentsGroup2"]

    def node_type(self) -> str:
        return "Part"

    @classmethod
    def descriptive_label(cls, label: str) -> str:
        return label

class ScheduleAmendmentsGroup2(HeadingPara):
    pass

class ScheduleMisc(Container):
    pass

class ScheduleProvisions(Container):
    pass