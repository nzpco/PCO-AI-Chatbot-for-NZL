from __future__ import annotations
from typing import List, TYPE_CHECKING

from ..base import BaseLegModal, Container
from .section import Section
from .part import Part
from .schedule import Schedule
from .misc import CrossHead
if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class CoverRePrintNote(BaseLegModal):
    text: str

    def as_text(self) -> str:
        return self.text

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'CoverRePrintNote':
        children = parser.parse_children(node, parent_chunk_id=parent_chunk_id)
        text = "\n\n".join([child.as_text() for child in children if child is not None])
        return cls(text=text)

class Cover(BaseLegModal):
    reprint_date: str
    title: str
    assent: str
    commencement: str
    cover_reprint_note: str

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'Cover':
        # raise if there are any unexpected children
        parser.parse_children(node, ignore_keys=["reprint-date", "title", "assent", "commencement", "cover.reprint-note"])

        reprint_note = node.find("cover.reprint-note")

        return cls(
            reprint_date=cls.get_text(node.find("reprint-date")),
            title=cls.get_text(node.find("title")),
            assent=cls.get_text(node.find("assent")),
            commencement=cls.get_text(node.find("commencement")),
            cover_reprint_note=parser.parse_node(reprint_note).as_text(),
        )

class Body(Container):
    pass

class Front(Container):
    pass

class Act(BaseLegModal):
    title: str
    year: str
    id: str
    no: str
    type: str
    date_assent: str
    date_as_at: str
    administered_by: str | None
    date_reprint: str
    cover_note: str
    body_content: list["Section | Part | CrossHead"]
    schedules: list["Schedule"]

    def children(self) -> list["BaseLegModal"]:
        return self.body_content + self.schedules

    def as_text(self, indent=0) -> str:
        s = f"Title: {self.title}\n"
        s += f"Year: {self.year}\n"
        s += f"Id: {self.id}\n"
        s += f"No: {self.no}\n"
        s += f"Type: {self.type}\n"
        s += f"Date Assent: {self.date_assent}\n"
        s += f"Date As At: {self.date_as_at}\n"
        s += f"Administered By: {self.administered_by}\n"
        s += f"Date Reprint: {self.date_reprint}\n"
        s += f"Cover Note: {self.cover_note}\n"
        s += "\n" + "\n".join([child.as_text() for child in self.body_content])
        s += "\n" + "\n".join([schedule.as_text() for schedule in self.schedules])
        return s

    def print(self, indent=0):
        print("Title: ", self.title)
        print("Year: ", self.year)
        print("Id: ", self.id)
        print("No: ", self.no)
        print("Type: ", self.type)
        print("Date Assent: ", self.date_assent)
        print("Date As At: ", self.date_as_at)
        print("Administered By: ", self.administered_by)
        print("Date Reprint: ", self.date_reprint)
        print("Cover Note: ", self.cover_note)
        for child in self.body_content:
            child.print(indent=indent+1)
        for schedule in self.schedules:
            schedule.print(indent=indent+1)

    @classmethod
    def from_xml(cls, node: etree.Element, parser: XMLParser, parent_chunk_id: str | None = None) -> 'Act':
        cover = parser.parse_node(node.find("cover"))
        year = node.get("year")
        chunk_id = f"{cover.title}"
        body = parser.parse_node(node.find("body"), parent_chunk_id=chunk_id)
        schedule_group = node.find("schedule.group")
        schedules = parser.parse_children(schedule_group, parent_chunk_id=chunk_id) if schedule_group is not None else []
        children = parser.parse_children(node, ignore_keys=["cover", "body", "schedule.group", "end"])

        return cls(
            title=cover.title,
            year=year,
            id=node.get("id"),
            no=node.get("act.no"),
            type=node.get("act.type"),
            date_assent=node.get("date.assent"),
            date_as_at=node.get("date.as.at"),
            date_reprint=cover.reprint_date,
            cover_note=cover.cover_reprint_note,
            administered_by=None,
            body_content=body.contents,
            schedules=schedules,
            chunk_id=chunk_id
        )