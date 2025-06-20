"""
Response cache for common questions to reduce latency
"""
import re
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ResponseCache:
    """Cache for common responses to reduce LLM calls"""
    
    def __init__(self):
        # Common FAQ patterns and responses
        self.faq_patterns: List[Tuple[re.Pattern, str]] = [
            # Pricing questions
            (re.compile(r'\b(price|cost|pricing|how much|fee)\b', re.I), 
             "From 10 dollars per property per month. 14-day free trial, no credit card needed."),
            
            # Free trial
            (re.compile(r'\b(free trial|trial|try.*free)\b', re.I),
             "Yes! 14 days free, full access, no credit card required."),
            
            # Integrations
            (re.compile(r'\b(integrate|integration|work with|compatible)\b.*\b(guesty|hostaway|lodgify)\b', re.I),
             "Yes, we integrate with Guesty, Hostaway, and Lodgify."),
            
            # Languages
            (re.compile(r'\b(language|languages|multilingual)\b', re.I),
             "Botel AI supports practically all major languages."),
            
            # Support
            (re.compile(r'\b(support|help|assistance)\b', re.I),
             "24/7 email and chat support. Phone support on higher plans."),
            
            # Security
            (re.compile(r'\b(secure|security|safe|data protection)\b', re.I),
             "AES-256 encryption, TLS 1.2+, GDPR/CCPA compliant. Your data is secure."),
            
            # Cancel
            (re.compile(r'\b(cancel|cancellation|contract)\b', re.I),
             "Cancel anytime. No long-term contracts or cancellation fees."),
            
            # Setup
            (re.compile(r'\b(setup|onboarding|getting started)\b', re.I),
             "Guided onboarding included. Most users are up and running in under 15 minutes."),
            
            # ROI
            (re.compile(r'\b(roi|return.*investment|save.*money)\b', re.I),
             "Most customers recoup their investment in the first month through time savings and increased bookings."),
            
            # Yes responses
            (re.compile(r'^(yes|yeah|yep|sure|ok|okay|sounds good|great)$', re.I),
             None),  # Don't cache simple acknowledgments
            
            # No responses  
            (re.compile(r'^(no|nope|not really|nah)$', re.I),
             None),  # Don't cache simple negatives
        ]
        
        # Track cache hits for optimization
        self.cache_hits = 0
        self.total_queries = 0
    
    def get_cached_response(self, user_input: str) -> Optional[str]:
        """
        Check if user input matches a cached pattern and return response
        Returns None if no match found
        """
        self.total_queries += 1
        
        # Clean input
        cleaned_input = user_input.strip().lower()
        
        # Check each pattern
        for pattern, response in self.faq_patterns:
            if pattern.match(cleaned_input) and response:
                self.cache_hits += 1
                logger.info(f"Cache hit for: {user_input[:50]}... ({self.cache_hits}/{self.total_queries})")
                return response
        
        return None
    
    def add_pattern(self, pattern: str, response: str):
        """Add a new pattern to the cache"""
        compiled_pattern = re.compile(pattern, re.I)
        self.faq_patterns.append((compiled_pattern, response))
    
    def get_stats(self) -> Dict[str, float]:
        """Get cache performance statistics"""
        hit_rate = (self.cache_hits / self.total_queries * 100) if self.total_queries > 0 else 0
        return {
            "cache_hits": self.cache_hits,
            "total_queries": self.total_queries,
            "hit_rate": hit_rate
        }

# Global cache instance
response_cache = ResponseCache()