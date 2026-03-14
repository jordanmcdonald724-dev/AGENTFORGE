#!/usr/bin/env python3
"""Update agent system prompts in database with enhanced luxury-tier standards"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Import agent configs
import sys
sys.path.append('/app/backend')
from routes.agents import AGENT_CONFIGS
from models.base import Agent

async def update_prompts():
    """Update agent system prompts in MongoDB and create new agents"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'agentforge')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Updating agent system prompts...")
    
    for role, config in AGENT_CONFIGS.items():
        # Try to update existing agent
        result = await db.agents.update_one(
            {"role": role},
            {"$set": {"system_prompt": config["system_prompt"]}}
        )
        
        if result.matched_count > 0:
            print(f"✅ Updated {config['name']} ({role})")
        else:
            # Agent doesn't exist, create it
            print(f"📝 Creating new agent {config['name']} ({role})")
            agent = Agent(
                name=config["name"],
                role=config["role"],
                avatar=config["avatar"],
                system_prompt=config["system_prompt"],
                specialization=config["specialization"]
            )
            doc = agent.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.agents.insert_one(doc)
            print(f"✅ Created {config['name']} ({role})")
    
    # Count total agents
    total = await db.agents.count_documents({})
    print(f"\n🎉 Agent system updated successfully!")
    print(f"📊 Total agents: {total}")
    print("All agents configured for 100% complete, luxury-tier output.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_prompts())
