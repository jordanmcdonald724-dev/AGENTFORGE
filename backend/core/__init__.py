# Core module - Database, config, utilities, helpers, agents

from .database import db
from .clients import llm_client, tts_client
from .agents import AGENT_CONFIGS, DELEGATION_KEYWORDS, PROJECT_THUMBNAILS
from .helpers import (
    serialize_doc, extract_code_blocks, extract_delegations,
    detect_delegation_need, call_agent, stream_agent_response,
    build_project_context, generate_image_fal, get_or_create_agents
)
