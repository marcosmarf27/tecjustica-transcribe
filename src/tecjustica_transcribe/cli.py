"""CLI principal — comandos init e transcrever."""

import contextlib
import logging
import os
import warnings

# Suprimir warnings inofensivos ANTES de qualquer import pesado
# pyannote/torchcodec emitem UserWarning multiline no import — filtrar por módulo
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
warnings.filterwarnings("ignore", category=UserWarning, module="torchcodec")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*TensorFloat-32.*")
warnings.filterwarnings("ignore", message=".*degrees of freedom.*")
# Lightning upgrade message e whisperx info logs
logging.getLogger("lightning.pytorch.utilities.migration").setLevel(logging.ERROR)
logging.getLogger("lightning.pytorch").setLevel(logging.ERROR)
logging.getLogger("lightning").setLevel(logging.ERROR)
logging.getLogger("whisperx").setLevel(logging.WARNING)
# onnxruntime C++ stderr — precisa da env var antes do import
os.environ["ORT_LOG_LEVEL"] = "3"
os.environ["ONNXRUNTIME_LOG_SEVERITY_LEVEL"] = "3"


@contextlib.contextmanager
def _suprimir_stderr():
    """Redireciona stderr para /dev/null temporariamente (captura warnings C++)."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    stderr_original = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(stderr_original, 2)
        os.close(stderr_original)

import click

from tecjustica_transcribe import __version__


@click.group()
@click.version_option(version=__version__, prog_name="tecjustica-transcribe")
def main() -> None:
    """TecJustiça Transcribe — transcrição de audiências judiciais com WhisperX."""


@main.command()
def init() -> None:
    """Diagnostica e prepara a máquina para transcrição."""
    with _suprimir_stderr():
        from tecjustica_transcribe.diagnostico import executar_diagnostico

    executar_diagnostico()


@main.command()
@click.argument("arquivo", type=click.Path(exists=True))
@click.option("--output", "-o", default="./transcricoes", help="Pasta de saída.")
@click.option("--sem-diarizacao", is_flag=True, help="Transcrever sem identificar falantes.")
def transcrever(arquivo: str, output: str, sem_diarizacao: bool) -> None:
    """Transcreve um arquivo MP4 de audiência judicial."""
    with _suprimir_stderr():
        from tecjustica_transcribe.transcrever import executar_transcricao

    executar_transcricao(arquivo, output, sem_diarizacao=sem_diarizacao)
