from __future__ import annotations
from typing import List, TYPE_CHECKING

from ..base import BaseLegModal, LabeledContainer
from .section import Section
from .misc import CrossHead
from .notes import Notes
from .paragraph import Paragraph

if TYPE_CHECKING:
    from ..xml_parser import XMLParser

from lxml import etree

class Part(LabeledContainer):
    contents: list["Section | Subpart | CrossHead | Notes | Paragraph"]

    @classmethod
    def descriptive_label(cls, label: str) -> str:
        return label

class Subpart(LabeledContainer):
    contents: list["Section | CrossHead | Notes"]
