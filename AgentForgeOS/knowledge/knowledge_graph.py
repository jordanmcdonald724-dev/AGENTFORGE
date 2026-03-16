"""
Knowledge Graph (shared)
========================
Thin wrapper that reuses the services-layer KnowledgeGraph for read-heavy flows.
"""

from AgentForgeOS.services.knowledge_graph import KnowledgeGraph  # re-export

__all__ = ["KnowledgeGraph"]
