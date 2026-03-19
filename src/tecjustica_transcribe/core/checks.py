"""Verificações do sistema — lógica pura sem UI."""

from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import dataclass

from tecjustica_transcribe.core.config import carregar_config


@dataclass
class CheckResult:
    nome: str
    ok: bool
    detalhe: str = ""


def verificar_python() -> CheckResult:
    """Verifica versão do Python."""
    versao = platform.python_version()
    major, minor = sys.version_info[:2]
    if major == 3 and 10 <= minor < 14:
        return CheckResult("Python", True, versao)
    return CheckResult("Python", False, f"{versao} — requer >=3.10,<3.14")


def verificar_nvidia() -> CheckResult:
    """Verifica driver NVIDIA via nvidia-smi."""
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            versao = r.stdout.strip().split("\n")[0]
            return CheckResult("Driver NVIDIA", True, versao)
        return CheckResult("Driver NVIDIA", False, "nvidia-smi falhou")
    except FileNotFoundError:
        return CheckResult("Driver NVIDIA", False, "nvidia-smi não encontrado")


def verificar_cuda() -> CheckResult:
    """Verifica CUDA via PyTorch."""
    try:
        import torch

        if torch.cuda.is_available():
            versao = torch.version.cuda or "desconhecida"
            return CheckResult("CUDA", True, versao)
        return CheckResult("CUDA", False, "CUDA não disponível no PyTorch")
    except ImportError:
        return CheckResult("CUDA", False, "PyTorch não instalado")


def verificar_gpu() -> CheckResult:
    """Verifica GPU e VRAM disponível."""
    try:
        import torch

        if torch.cuda.is_available():
            nome = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory
            vram_gb = vram / (1024**3)
            detalhe = f"{nome} ({vram_gb:.1f} GB)"
            if vram_gb < 5.5:
                return CheckResult(
                    "GPU", False, f"{detalhe} — mínimo 6 GB de VRAM"
                )
            return CheckResult("GPU", True, detalhe)
        return CheckResult("GPU", False, "Nenhuma GPU CUDA detectada")
    except ImportError:
        return CheckResult("GPU", False, "PyTorch não instalado")


def verificar_ffmpeg() -> CheckResult:
    """Verifica ffmpeg instalado."""
    try:
        r = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            primeira_linha = r.stdout.split("\n")[0]
            partes = primeira_linha.split()
            versao = partes[2] if len(partes) >= 3 else "instalado"
            return CheckResult("ffmpeg", True, versao)
        return CheckResult("ffmpeg", False, "ffmpeg falhou")
    except FileNotFoundError:
        return CheckResult(
            "ffmpeg", False, "não encontrado — instale com: sudo apt install ffmpeg"
        )


def verificar_token_hf() -> CheckResult:
    """Verifica se o token HuggingFace está configurado."""
    config = carregar_config()
    token = config.get("hf_token", "")
    if token:
        return CheckResult("Token HuggingFace", True, f"{token[:8]}...")
    return CheckResult("Token HuggingFace", False, "Não configurado")


def executar_todas_verificacoes() -> list[CheckResult]:
    """Executa todas as verificações e retorna a lista de resultados."""
    return [
        verificar_python(),
        verificar_nvidia(),
        verificar_cuda(),
        verificar_gpu(),
        verificar_ffmpeg(),
        verificar_token_hf(),
    ]
