# Chanakya v1

Chanakya v1 is an autonomous local-first AI platform that combines:
- free and paid LLM support
- local offline model support via Ollama
- automated code generation and safe sandbox execution
- trading and backtesting utilities
- content generation and research workflows
- keyboard and mouse automation for desktop tasks
- feature lock / unlock system and self-learning logic

## Features

- AI model manager with Groq, Gemini, OpenAI, Claude, OpenRouter, and Ollama support
- Safe Python code execution in a sandbox
- Database-backed memory and logs
- Trading engine with moving average, RSI, and Bollinger strategy backtesting
- Research engine for market and topic analysis
- Content engine for YouTube scripts and social posts
- Automation engine for mouse, keyboard, and screen capture
- Self-learning and feature lock systems

## Quick start

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Copy environment variables:

```bash
cp .env.example .env
```

3. Fill in keys if needed. Local offline mode works without paid API keys.

4. Run the app:

```bash
python main.py
```

## Important note

This project is designed to run locally and is intentionally modular. Some features require either:
- API keys for paid providers, or
- a local Ollama model running on your machine

## Repo structure

```text
chanakya-v1/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
├── config.py
├── core/
│   ├── ai_model_manager.py
│   ├── database_manager.py
│   ├── code_generator.py
│   ├── automation_engine.py
│   └── ai_systems.py
├── modules/
│   ├── trading_engine.py
│   ├── content_engine.py
│   └── research_engine.py
└── data/
```

## License

MIT
