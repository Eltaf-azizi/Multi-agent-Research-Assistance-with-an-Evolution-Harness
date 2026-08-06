"""
Generate 50 sample documents for local document search
"""

import os
from pathlib import Path

TOPICS = [
    "Artificial Intelligence",
    "Climate Change",
    "Renewable Energy",
    "Space Exploration",
    "Quantum Computing",
    "Biotechnology",
    "Cybersecurity",
    "Robotics",
    "Blockchain",
    "Nanotechnology"
]

def generate():
    """Create 50 sample text documents"""
    docs_dir = Path("data/documents")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(50):
        topic = TOPICS[i % len(TOPICS)]
        filename = docs_dir / f"doc_{i+1:03d}.txt"
        
        content = f"""DOCUMENT {i+1}: {topic} Research Brief

TITLE: Understanding {topic} - A Comprehensive Overview

SUMMARY:
This document provides a comprehensive overview of {topic} and its implications 
for modern society, technology, and future developments.

KEY FACTS:
• {topic} has seen significant advancement in recent years
• Research investment in {topic} reached new highs in 2023-2024
• Multiple industries are adopting {topic} technologies
• {topic} creates new opportunities and challenges

DETAILED ANALYSIS:
The field of {topic} encompasses multiple disciplines and approaches. 
Researchers have identified several key areas of development that promise 
to revolutionize how we understand and apply these concepts.

Applications include:
1. Healthcare and medicine
2. Environmental protection
3. Industrial manufacturing
4. Consumer technology
5. Scientific research

CONCLUSION:
{topic} represents one of the most promising areas of modern research and 
development. Continued investment and study will yield significant benefits.

REFERENCES:
• Research Database {i+1}
• International Journal of {topic}
• Global {topic} Initiative Report 2024

DOCUMENT ID: DOC-{i+1:03d}
DATE: 2024
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Created 50 documents in {docs_dir}/")

if __name__ == "__main__":
    generate()