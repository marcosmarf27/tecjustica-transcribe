"""Lógica do comando init — diagnóstico e setup (wrapper Rich sobre core/)."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tecjustica_transcribe.core.checks import CheckResult, executar_todas_verificacoes
from tecjustica_transcribe.core.config import salvar_token_hf

console = Console()


def configurar_token_hf() -> None:
    """Pede o token HuggingFace ao usuário e salva."""
    console.print()
    console.print(
        "[yellow]⚠️  Token HuggingFace necessário para diarização.[/yellow]"
    )
    console.print(
        "Obtenha seu token em: [link=https://huggingface.co/settings/tokens]"
        "huggingface.co/settings/tokens[/link]"
    )
    console.print(
        "Aceite os termos em: [link=https://huggingface.co/pyannote/speaker-diarization-3.1]"
        "huggingface.co/pyannote/speaker-diarization-3.1[/link]"
    )
    console.print()

    token = console.input("Cole seu token: ").strip()
    if token:
        salvar_token_hf(token)
        console.print("[green]✅ Token salvo![/green]")
    else:
        console.print("[red]Token vazio — diarização não funcionará.[/red]")


def baixar_modelos() -> CheckResult:
    """Pré-baixa os modelos WhisperX para evitar surpresa na primeira transcrição."""
    try:
        console.print("\n[cyan]⬇️  Verificando modelos WhisperX...[/cyan]")
        from faster_whisper import WhisperModel

        console.print("   Carregando large-v2 (pode demorar no primeiro uso)...")
        WhisperModel("large-v2", device="cuda", compute_type="float16")
        return CheckResult("Modelos", True, "large-v2 pronto")
    except Exception as e:
        return CheckResult("Modelos", False, str(e)[:80])


def _mostrar_relatorio(resultados: list[CheckResult]) -> None:
    """Exibe o relatório de diagnóstico como tabela rich."""
    table = Table(show_header=False, border_style="cyan", pad_edge=False)
    table.add_column("Item", min_width=20)
    table.add_column("Status", min_width=40)

    for r in resultados:
        icone = "[green]✅[/green]" if r.ok else "[red]❌[/red]"
        table.add_row(r.nome, f"{icone} {r.detalhe}")

    panel = Panel(
        table,
        title="[bold]TecJustiça Transcribe — Diagnóstico[/bold]",
        border_style="cyan",
    )
    console.print(panel)


def executar_diagnostico() -> None:
    """Verifica pré-requisitos e prepara a máquina."""
    resultados = executar_todas_verificacoes()

    _mostrar_relatorio(resultados)

    # Token HuggingFace — oferecer configuração se ausente
    check_token = next(
        (r for r in resultados if r.nome == "Token HuggingFace"), None
    )
    if check_token and not check_token.ok:
        configurar_token_hf()

    # Download de modelos — só se GPU estiver OK
    check_gpu = next((r for r in resultados if r.nome == "GPU"), None)
    if check_gpu and check_gpu.ok:
        resultado_modelos = baixar_modelos()
        console.print()
        icone = "[green]✅[/green]" if resultado_modelos.ok else "[red]❌[/red]"
        console.print(f"Modelos: {icone} {resultado_modelos.detalhe}")
    else:
        console.print(
            "\n[yellow]⚠️  GPU não detectada — pulando download de modelos.[/yellow]"
        )

    # Resumo
    falhas = [r for r in resultados if not r.ok]
    console.print()
    if not falhas:
        console.print("[bold green]✅ Tudo pronto para transcrever![/bold green]")
    else:
        console.print(
            f"[bold yellow]⚠️  {len(falhas)} problema(s) encontrado(s). "
            "Resolva antes de transcrever.[/bold yellow]"
        )
