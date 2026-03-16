"""
Compatibility layer for provider integrations.

The concrete client implementations now live in AgentForgeOS/providers.
This shim keeps existing import paths working while the architecture
transitions to the new provider layer.
"""

from AgentForgeOS.providers.clients import *  # noqa: F401,F403
