import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def serialize_doc(doc: dict) -> dict:
    """Remove MongoDB _id and convert any remaining ObjectIds"""
    if doc is None:
        return None
    result = {k: v for k, v in doc.items() if k != "_id"}
    return result
