from fastapi import APIRouter, HTTPException
from typing import List
from ..db.models import LegislationDocument, LegislationFragment
from beanie import PydanticObjectId

router = APIRouter(prefix="/api/legislation", tags=["legislation"])

@router.get("")
async def get_legislation_list():
    """Get a list of all legislation documents"""
    documents = await LegislationDocument.find_all().to_list()
    return documents

@router.get("/{document_id}")
async def get_legislation_document(document_id: str):
    """Get a specific legislation document and its root fragments"""
    try:
        # Find document by its id field instead of _id
        document = await LegislationDocument.find_one(LegislationDocument.id == document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get root fragments (fragments without parents)
        root_fragments = await LegislationFragment.find(
            LegislationFragment.document.id == document_id,
            LegislationFragment.parent_fragment.id == None
        ).to_list()

        return {
            "document": document,
            "root_fragments": root_fragments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fragment/{fragment_id}")
async def get_fragment(fragment_id: str):
    """Get a specific fragment and its children"""
    try:
        fragment = await LegislationFragment.get(PydanticObjectId(fragment_id))
        if not fragment:
            raise HTTPException(status_code=404, detail="Fragment not found")

        # Get child fragments
        child_fragments = await LegislationFragment.find(
            LegislationFragment.parent_fragment.id == PydanticObjectId(fragment_id)
        ).to_list()

        return {
            "fragment": fragment,
            "child_fragments": child_fragments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))