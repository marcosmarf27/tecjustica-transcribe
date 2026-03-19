"""Entry point da GUI — layout com menu lateral."""

from __future__ import annotations

from typing import Callable


def _obter_info_sistema() -> str:
    """Retorna string com info GPU/CUDA para a barra de status."""
    try:
        import torch

        if torch.cuda.is_available():
            gpu = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return f"GPU: {gpu} ({vram:.1f} GB) | CUDA {torch.version.cuda}"
        return "CPU (sem GPU CUDA)"
    except ImportError:
        return "PyTorch não instalado"


def _layout(pagina_ativa: str, conteudo_fn: Callable[[], None]) -> None:
    """Layout padrão com menu lateral e barra de status."""
    from nicegui import ui

    ui.dark_mode(True)

    menu_items = [
        ("Transcrever", "/", "mic"),
        ("Modelos", "/modelos", "download"),
        ("Configurações", "/configuracoes", "settings"),
        ("Sistema", "/diagnostico", "monitor_heart"),
    ]

    with ui.header().classes("bg-[#1a1a2e] items-center"):
        ui.icon("gavel").classes("text-2xl q-mr-sm")
        ui.label("TecJustiça Transcribe").classes("text-h6 text-bold")

    with ui.left_drawer(value=True).classes("bg-[#16213e]"):
        ui.label("Menu").classes("text-overline text-grey-5 q-pa-sm")
        for label, path, icon in menu_items:
            btn = ui.button(
                label, icon=icon, on_click=lambda p=path: ui.navigate.to(p)
            )
            btn.props("flat align=left no-caps").classes("w-full text-white")
            if label == pagina_ativa:
                btn.classes("bg-primary")

    with ui.column().classes("w-full max-w-4xl mx-auto p-6"):
        conteudo_fn()

    with ui.footer().classes("bg-[#1a1a2e] q-pa-xs"):
        ui.label(_obter_info_sistema()).classes("text-xs text-grey-5")


def main() -> None:
    """Inicia a GUI desktop."""
    from nicegui import ui

    from tecjustica_transcribe.gui.pages import (
        configuracoes,
        diagnostico,
        modelos,
        transcricao,
    )

    @ui.page("/")
    def page_transcricao():
        _layout("Transcrever", transcricao.conteudo)

    @ui.page("/modelos")
    def page_modelos():
        _layout("Modelos", modelos.conteudo)

    @ui.page("/configuracoes")
    def page_configuracoes():
        _layout("Configurações", configuracoes.conteudo)

    @ui.page("/diagnostico")
    def page_diagnostico():
        _layout("Sistema", diagnostico.conteudo)

    ui.run(
        title="TecJustiça Transcribe",
        native=True,
        window_size=(1050, 750),
        reload=False,
    )
