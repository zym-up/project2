@echo off
chcp 65001 >nul
echo Starting DS Agent v2 Backend (LangChain + LangGraph)...
uvicorn backend.main:app --reload --port 8502 --host 0.0.0.0
pause
