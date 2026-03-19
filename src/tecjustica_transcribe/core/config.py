"""Gerenciamento de configuração — carregar/salvar config, token HF."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "tecjustica"
CONFIG_FILE = CONFIG_DIR / "config.json"


def carregar_config() -> dict:
    """Carrega configuração do disco."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def salvar_config(config: dict) -> None:
    """Salva configuração no disco."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def obter_token_hf() -> str | None:
    """Lê o token HuggingFace salvo."""
    config = carregar_config()
    return config.get("hf_token") or None


def salvar_token_hf(token: str) -> None:
    """Salva o token HuggingFace."""
    config = carregar_config()
    config["hf_token"] = token
    salvar_config(config)
