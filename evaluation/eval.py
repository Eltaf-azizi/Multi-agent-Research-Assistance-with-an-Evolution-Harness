"""
EVAL.PY - Complete Evaluation System
"""

import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ResearchOrchestrator
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Evaluator:
    """Complete evaluation system with multiple scoring methods"""
    
    def __init__(self):
        print("📊 Initializing Evaluator...")
        self.orchestrator = ResearchOrchestrator()
        self.judge_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.results = []
        self.start_time = None
    
    def load_test_set(self) -> list:
        """Load test questions"""
        filepath = Path(__file__).parent / "test_set.json"
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data['test_questions']
    
    def keyword_score(self, text: str, keywords: list) -> float:
        """Keyword match percentage"""
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        return (matches / len(keywords)) * 100
    
    def llm_judge_score(self, question: str, generated: str, gold: str) -> tuple:
        """LLM evaluates answer quality (0-5)"""
        
        prompt = f"""Rate this answer from 0-5:
        
Question: {question}
Gold Standard: {gold}
Generated Answer: {generated[:500]}

0=Completely wrong, 5=Perfect. Return format: "SCORE:X|REASON:brief" """
        
        try:
            response = self.judge_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            text = response.choices[0].message.content
            
            # Parse score
            score = 0
            reason = "No reason"
            
            if "SCORE:" in text:
                parts = text.split("|")
                for part in parts:
                    if "SCORE:" in part:
                        for char in part:
                            if char.isdigit() and 0 <= int(char) <= 5:
                                score = int(char)
                                break
                    if "REASON:" in part:
                        reason = part.split("REASON:")[-1].strip()
            
            return score, reason
            
        except Exception as e:
            return 0, f"Judge error: {e}"
    
    def factual_accuracy_score(self, generated: str, gold: str) -> float:
        """Simple factual overlap score"""
        gold_words = set(gold.lower().split())
        gen_words = set(generated.lower().split())
        
        if not gold_words:
            return 0.0
        
        overlap = gold_words.intersection(gen_words)
        return (len(overlap) / len(gold_words)) * 100
    
    def run_evaluation(self) -> list:
        """Run complete evaluation"""
        
        self.start_time = time.time()
        test_questions = self.load_test_set()
        
        print(f"\n{'='*70}")
        print(f"📊 EVALUATION STARTED")
        print(f"{'='*70}")
        print(f"Questions: {len(test_questions)}")
        print(f"Methods: Keyword Match, LLM Judge, Factual Accuracy\n")
        
        for i, test in enumerate(test_questions, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(test_questions)}] {test['question'][:60]}...")
            print(f"{'='*70}")
            
            # Run research
            q_start = time.time()
            result = self.orchestrator.research(test['question'], verbose=False)
            q_time = time.time() - q_start
            
            # Calculate scores
            kw_score = self.keyword_score(result['brief'], test['keywords'])
            llm_score, reason = self.llm_judge_score(
                test['question'], result['brief'], test['gold_answer']
            )
            fact_score = self.factual_accuracy_score(result['brief'], test['gold_answer'])
            
            # Combined score (weighted)
            combined = (kw_score * 0.3) + (llm_score * 20 * 0.4) + (fact_score * 0.3)
            
            # Store result
            eval_result = {
                'id': test['id'],
                'question': test['question'][:50],
                'keyword_score': round(kw_score, 1),
                'llm_score': llm_score,
                'factual_score': round(fact_score, 1),
                'combined_score': round(combined, 1),
                'sources': result['sources_count'],
                'time': round(q_time, 2),
                'brief_length': len(result['brief']),
                'reason': reason[:100]
            }
            
            self.results.append(eval_result)
            
            print(f"   KW: {kw_score:.1f}% | LLM: {llm_score}/5 | Fact: {fact_score:.1f}% | Combined: {combined:.1f}%")
        
        # Print and save
        self.print_table()
        self.save_results()
        
        return self.results
    
    