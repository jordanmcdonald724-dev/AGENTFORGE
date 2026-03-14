#!/usr/bin/env python3
"""Update agent system prompts in database with enhanced luxury-tier standards"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Import agent configs
import sys
sys.path.append('/app/backend')
from routes.agents import AGENT_CONFIGS

async def update_prompts():
    """Update agent system prompts in MongoDB"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'agentforge')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Updating agent system prompts...")
    
    for role, config in AGENT_CONFIGS.items():
        result = await db.agents.update_one(
            {"role": role},
            {"$set": {"system_prompt": config["system_prompt"]}}
        )
        
        if result.matched_count > 0:
            print(f"✅ Updated {config['name']} ({role})")
        else:
            print(f"⚠️  Agent {role} not found in database")
    
    print("\n🎉 Agent prompts updated successfully!")
    print("Agents will now generate 100% complete, luxury-tier code.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_prompts())
