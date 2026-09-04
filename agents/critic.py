from .base_agent import BaseAgent

class CriticAgent(BaseAgent):
    """Agent that reviews and improves the brief (Stretch Goal)"""
    
    def __init__(self):
        super().__init__("Critic")
    
    def review_brief(self, brief, research_data):
        """Review and suggest improvements for the brief"""
        
        system_prompt = """You are a critical reviewer. Analyze the research brief for:
        1. Factual accuracy (compare with research data)
        2. Citation completeness
        3. Clarity and structure
        4. Missing important information
        
        Provide specific, actionable feedback."""
        
        user_prompt = f"""Review this research brief:

BRIEF:
{brief}

RESEARCH DATA (for fact-checking):
{research_data}

Provide your critique and suggestions."""
        
        feedback = self.call_llm(system_prompt, user_prompt, temperature=0.3)
        return feedback
    
    def improve_brief(self, brief, feedback):
        """Revise the brief based on critic feedback"""
        
        system_prompt = """You are an editor. Revise the brief based on the critic's feedback.
        Maintain all correct citations and improve the brief."""
        
        user_prompt = f"""ORIGINAL BRIEF:
{brief}

CRITIC FEEDBACK:
{feedback}

Please produce the improved brief."""
        
        improved = self.call_llm(system_prompt, user_prompt, temperature=0.3)
        return improved