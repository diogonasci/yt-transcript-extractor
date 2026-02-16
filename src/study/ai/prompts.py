"""Prompt templates for Claude AI processing."""

SYSTEM_PROMPT = (
    "You are a knowledge extraction assistant. "
    "You analyze video transcripts and extract structured knowledge in Brazilian Portuguese (pt-BR). "
    "You always respond with valid JSON, without markdown code fences."
)

USER_PROMPT_TEMPLATE = (
    'Analise a transcricao do video "{title}" e retorne um JSON com:\n'
    "\n"
    '1. "tldr": Resumo de 2-3 linhas em portugues (pt-BR)\n'
    '2. "summary": Resumo detalhado em Markdown, 5-20 paragrafos, em portugues (pt-BR)\n'
    '3. "concepts": Lista de conceitos-chave, cada um com "name" e "definition" em portugues\n'
    "\n"
    "Transcricao:\n"
    "---\n"
    "{transcript}\n"
    "---\n"
    "\n"
    "Retorne APENAS o JSON valido, sem markdown code fences."
)
