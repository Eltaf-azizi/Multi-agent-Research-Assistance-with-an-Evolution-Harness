<h1 align="center"> Multi-agent-Research-Assistance-with-an-Evolution-Harness </h1>

**Retrieval-Augmented Generation over Real Constitutional Documents with Grounded Citations**

A production-grade RAG system that answers questions about constitutional documents from six nations with full source citations and hallucination prevention.

## 📋 Table of Contents
 - About the Project
 - Features
 - Demo
 - System Architecture
 - Countries Covered
 - Tech Stack
 - Getting Started
   - Prerequisites
   - Installation
   - Quick Start
 - Usage
   - Command Line
   - Web Interface
   - Example Queries
 - Configuration
 - Evaluation
 - Project Structure
 - Testing
 - Troubleshooting
 - Contributing
 - License
 - Acknowledgments

## 📖 About the Project
This project implements a Retrieval-Augmented Generation (RAG) pipeline that grounds Large Language Model outputs in verified constitutional documents. The system retrieves semantically relevant passages, generates answers with mandatory citations, and refuses to respond when confidence is insufficient.

Built as part of the Eltaf Year 1 curriculum — **E2 Project · Q3 History & Politics.**

## Why RAG?
Large Language Models hallucinate. In domains requiring factual precision — such as constitutional law — this is unacceptable. RAG solves this by:

1. Retrieving relevant context from verified documents
2. Grounding the LLM's answer exclusively in that context
3. Citing every claim with the source file and page number
4. Refusing when confidence falls below a threshold

## 🎬 Demo
### Web Interface
```text
┌─────────────────────────────────────────────────────────┐
│  📜 Constitutional RAG Q&A                              │
│  ───────────────────────────────────────────────────── │
│  🔍 Ask a Question                                      │
│  [What fundamental rights are guaranteed?]              │
│                                                         │
│  ───────────────────────────────────────────────────── │
│  📝 Answer                                              │
│  Citizens have the right to freedom of speech,          │
│  assembly, and religion [Source: constitution_usa.pdf,  │
│  Page: 5]. Equality before law is guaranteed            │
│  [Source: constitution_pakistan.pdf, Page: 12]...       │
│                                                         │
│  📚 Sources Used                                        │
│  📄 constitution_usa.pdf — Page 5 (92.3%)              │
│  📄 constitution_pakistan.pdf — Page 12 (87.1%)        │
└─────────────────────────────────────────────────────────┘
```

## Refusal Example
```text
Q: What is the recipe for chocolate cake?
A: "I don't have enough information in the provided 
   documents to answer this question."
```
