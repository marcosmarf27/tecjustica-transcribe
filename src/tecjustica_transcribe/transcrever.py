"""Lógica do comando transcrever — wrapper Rich sobre core/transcription."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from tecjustica_transcribe.core.config import obter_token_hf
from tecjustica_transcribe.core.transcription import (
    TranscriptionConfig,
    executar_pipeline,
)

console = Console()


def executar_transcricao(
    arquivo: str,
    output: str,
    *,
    sem_diarizacao: bool = False,
) -> None:
    """Transcreve um arquivo MP4 usando WhisperX."""
    arquivo_path = Path(arquivo)
    output_path = Path(output)

    # Validações
    if not arquivo_path.exists():
        console.print(f"[red]❌ Arquivo não encontrado: {arquivo}[/red]")
        sys.exit(1)

    token: str | None = None
    if not sem_diarizacao:
        token = obter_token_hf()
        if not token:
            console.print(
                "[red]❌ Token HuggingFace não configurado.[/red]\n"
                "Execute [bold]tecjustica-transcribe init[/bold] primeiro,\n"
                "ou use [bold]--sem-diarizacao[/bold] para transcrever sem identificar falantes."
            )
            sys.exit(1)

    console.print(f"\n[bold cyan]🎙️  Transcrevendo:[/bold cyan] {arquivo_path.name}")

    config = TranscriptionConfig(
        arquivo=arquivo_path,
        output_dir=output_path,
        diarizacao=not sem_diarizacao,
    )

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Iniciando...", total=None)

            def on_progress(etapa: str, msg: str) -> None:
                progress.update(task, description=msg)

            result = executar_pipeline(
                config, hf_token=token, on_progress=on_progress
            )

        console.print("\n[bold green]✅ Transcrição concluída![/bold green]")
        console.print(f"[bold]📁 Arquivos gerados em {output_path}/:[/bold]")
        console.print(f"   • {result.caminho_txt.name}  (texto puro)")
        console.print(f"   • {result.caminho_srt.name}  (legendas com timestamps)")
        console.print(f"   • {result.caminho_json.name} (dados completos + falantes)")

    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            console.print(
                "\n[red]❌ Memória da GPU insuficiente (OOM).[/red]\n"
                "Tente fechar outras aplicações ou use um vídeo mais curto."
            )
        else:
            console.print(f"\n[red]❌ Erro durante transcrição: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Erro durante transcrição: {e}[/red]")
        sys.exit(1)
