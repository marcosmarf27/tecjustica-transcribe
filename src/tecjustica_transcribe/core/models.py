"""Gerenciamento de modelos WhisperX — listar, baixar, excluir."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

MODELOS_WHISPER = {
    "large-v2": {"repo": "Systran/faster-whisper-large-v2", "tamanho_mb": 3100},
    "medium": {"repo": "Systran/faster-whisper-medium", "tamanho_mb": 1500},
    "small": {"repo": "Systran/faster-whisper-small", "tamanho_mb": 500},
    "tiny": {"repo": "Systran/faster-whisper-tiny", "tamanho_mb": 150},
}


@dataclass
class ModelInfo:
    name: str
    size_mb: int
    downloaded: bool
    cache_path: Path | None = None


def _cache_dir() -> Path:
    """Retorna o diretório de cache do HuggingFace."""
    return Path.home() / ".cache" / "huggingface" / "hub"


def listar_modelos() -> list[ModelInfo]:
    """Lista modelos disponíveis com status de download."""
    cache = _cache_dir()
    resultado = []
    for name, info in MODELOS_WHISPER.items():
        repo = info["repo"]
        cache_name = f"models--{repo.replace('/', '--')}"
        cache_path = cache / cache_name
        downloaded = (
            cache_path.exists() and any(cache_path.iterdir())
            if cache_path.exists()
            else False
        )
        resultado.append(
            ModelInfo(
                name=name,
                size_mb=info["tamanho_mb"],
                downloaded=downloaded,
                cache_path=cache_path if downloaded else None,
            )
        )
    return resultado


def baixar_modelo(
    name: str,
    on_progress: Callable[[str], None] | None = None,
) -> Path:
    """Baixa um modelo WhisperX via huggingface_hub."""
    if name not in MODELOS_WHISPER:
        raise ValueError(
            f"Modelo desconhecido: {name}. Disponíveis: {list(MODELOS_WHISPER.keys())}"
        )

    repo = MODELOS_WHISPER[name]["repo"]

    if on_progress:
        on_progress(f"Baixando {name}...")

    from huggingface_hub import snapshot_download

    cache_path = snapshot_download(repo_id=repo)

    if on_progress:
        on_progress(f"{name} baixado com sucesso")

    return Path(cache_path)


def deletar_modelo(name: str) -> bool:
    """Remove modelo do cache local. Retorna True se removido."""
    if name not in MODELOS_WHISPER:
        raise ValueError(f"Modelo desconhecido: {name}")

    repo = MODELOS_WHISPER[name]["repo"]
    cache_name = f"models--{repo.replace('/', '--')}"
    cache_path = _cache_dir() / cache_name

    if cache_path.exists():
        shutil.rmtree(cache_path)
        return True
    return False
