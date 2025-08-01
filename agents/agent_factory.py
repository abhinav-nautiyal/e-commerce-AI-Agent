from typing import Dict, Optional
from .amazon_agent import AmazonAgent
from .flipkart_agent import FlipkartAgent
from .aliexpress_agent import AliExpressAgent
import logging

class AgentFactory:
    _instances: Dict[str, object] = {}
    
    @classmethod
    async def get_agent(cls, platform: str):
        """Get or create an agent for the specified platform"""
        platform = platform.lower()
        
        if platform not in cls._instances:
            if platform == "amazon":
                agent = AmazonAgent()
            elif platform == "flipkart":
                agent = FlipkartAgent()
            elif platform == "aliexpress":
                agent = AliExpressAgent()
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            await agent.initialize()
            cls._instances[platform] = agent
            
        return cls._instances[platform]
    
    @classmethod
    async def close_all(cls):
        """Close all active agents"""
        for agent in cls._instances.values():
            try:
                await agent.close()
            except Exception as e:
                logging.error(f"Error closing agent: {str(e)}")
        cls._instances.clear() 