from __future__ import annotations

from lxml import etree
from colorama import Fore, Style
from typing import Dict, Type

from .base import BaseLegModal, Container, LabeledContainer
from .models import (
    Act, Cover, CoverRePrintNote, Body, Front,
    Section, Subsection,
    Part, Subpart,
    Schedule, ScheduleAmendments, ScheduleAmendmentsGroup1, ScheduleAmendmentsGroup2, ScheduleMisc, ScheduleProvisions,
    Paragraph, LabelPara, HeadingPara, Example,
    Notes, HistoryNote, AmendsNote, History, EditorialNote,
    Text, Citation, AdminOffice,
    LegTable,
    CrossHead, LabelParaCrossHead, LegList, DefPara, End, Amend, Contents,
    NotRelevant
)

from ..db.models import LegislationDocument

class XMLParser:
    # Explicit mapping of XML tags to model classes
    TAG_TO_MODEL: Dict[str, Type[BaseLegModal]] = {
        "act": Act,
        "cover": Cover,
        "cover.reprint-note": CoverRePrintNote,
        "body": Body,
        "front": Front,
        "prov": Section,
        "subprov": Subsection,
        "part": Part,
        "subpart": Subpart,
        "schedule": Schedule,
        "schedule.amendments": ScheduleAmendments,
        "schedule.amendments.group1": ScheduleAmendmentsGroup1,
        "schedule.amendments.group2": ScheduleAmendmentsGroup2,
        "schedule.misc": ScheduleMisc,
        "schedule.provisions": ScheduleProvisions,
        "para": Paragraph,
        "label-para": LabelPara,
        "notes": Notes,
        "example": Example,
        "history-note": HistoryNote,
        "amends-note": AmendsNote,
        "history": History,
        "editorial-note": EditorialNote,
        "text": Text,
        "citation": Citation,
        "admin-office": AdminOffice,
        "legtable": LegTable,
        "crosshead": CrossHead,
        "subprov.crosshead": CrossHead,
        "label-para.crosshead": LabelParaCrossHead,
        "list": LegList,
        "def-para": DefPara,
        "end": End,
        "amend": Amend,
        "contents": Contents,
    }

    def __init__(self):
        self.missing_keys = set()

    def parse_node(self, node: etree.Element, parent_chunk_id: str | None = None) -> BaseLegModal:
        if node is None:
            print("Warning: Attempted to parse None node")
            return NotRelevant.from_xml(node, self)

        try:
            model_class = self.TAG_TO_MODEL.get(node.tag)
            if model_class is None:
                print(f"Warning: No parser registered for tag '{node.tag}'")
                print("At node: ", node.getroottree().getpath(node))
                self.missing_keys.add(node.tag)
                return NotRelevant.from_xml(node, self)

            try:
                return model_class.from_xml(node, self, parent_chunk_id)
            except Exception as e:
                print(f"Error: Failed to parse node with tag '{node.tag}' using {model_class.__name__}")
                print(f"Error details: {str(e)}")
                print("At node: ", node.getroottree().getpath(node))
                raise

        except Exception as e:
            print(f"Error: Unexpected error while parsing tag '{node.tag}'")
            print(f"Error details: {str(e)}")
            print("At node: ", node.getroottree().getpath(node))
            raise

    def parse_children(self, node: etree.Element, ignore_keys: list[str] = [], parent_chunk_id: str | None = None) -> list[BaseLegModal]:
        return [self.parse_node(child, parent_chunk_id) for child in node if child.tag not in ignore_keys]

    async def parse_xml(self, file_path: str) -> dict:
        BaseLegModal.reset_order()
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(file_path, parser)
        act = self.parse_node(doc.getroot())
        act.print()

        print("Missing keys: ", self.missing_keys)


        document = LegislationDocument(
            title=act.title,
            year=act.year,
            type=act.type,
            date_assent=act.date_assent,
            date_as_at=act.date_as_at,
            administered_by=act.administered_by,
            id=act.id,
            no=act.no,
        )
        await document.save()
        await act.generate_fragments(document)

        all_nodes = act.generate_nodes()
        print(all_nodes["Section"][0])
        for type, nodes in all_nodes.items():
            print("-" * 100)
            print(Fore.BLUE + type + Style.RESET_ALL, "(" + str(len(nodes)) + ")")
            print("\n")
            for node in nodes[:10]:
                print(Fore.GREEN + node["chunk_id"] + Style.RESET_ALL)
                node["context"].print()
                print(node["text"] if len(node["text"]) < 1000 else node["text"][:1000] + Fore.RED + "..." + Style.RESET_ALL)

        all_nodes_dict = {
            type: [{
                "chunk_id": node["chunk_id"],
                "order": node["order"],
                "text": node["text"],
                "context": node["context"].model_dump()
            } for node in nodes]
            for type, nodes in all_nodes.items()
        }
        return all_nodes_dict