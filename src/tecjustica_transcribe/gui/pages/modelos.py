"""Página de gerenciamento de modelos — download/exclusão com progresso."""

from __future__ import annotations

import queue
import threading

from nicegui import ui

from tecjustica_transcribe.core.models import (
    baixar_modelo,
    deletar_modelo,
    listar_modelos,
)


def conteudo() -> None:
    """Renderiza a página de modelos."""
    progress_queue: queue.Queue = queue.Queue()

    ui.label("Gerenciamento de Modelos").classes("text-h5 text-bold q-mb-md")
    ui.label(
        "Modelos WhisperX armazenados em ~/.cache/huggingface/hub/"
    ).classes("text-caption text-grey q-mb-md")

    container = ui.column().classes("w-full gap-2")

    def refresh() -> None:
        container.clear()
        modelos = listar_modelos()
        with container:
            for m in modelos:
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label(m.name).classes("text-bold text-lg")
                            tamanho = (
                                f"{m.size_mb / 1000:.1f} GB"
                                if m.size_mb >= 1000
                                else f"{m.size_mb} MB"
                            )
                            ui.label(f"Tamanho: ~{tamanho}").classes(
                                "text-caption text-grey"
                            )

                        with ui.row().classes("items-center gap-2"):
                            if m.downloaded:
                                ui.icon("check_circle", color="positive").classes(
                                    "text-2xl"
                                )
                                ui.label("Baixado").classes("text-positive")
                                ui.button(
                                    "Excluir",
                                    icon="delete",
                                    on_click=lambda n=m.name: confirmar_exclusao(n),
                                ).props("flat color=negative size=sm")
                            else:
                                ui.icon("cloud_download", color="grey").classes(
                                    "text-2xl"
                                )
                                ui.button(
                                    "Baixar",
                                    icon="download",
                                    on_click=lambda n=m.name: download(n),
                                ).props("flat color=primary size=sm")

    def confirmar_exclusao(name: str) -> None:
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Excluir modelo {name}?").classes("text-bold")
            ui.label("O modelo será removido do cache local.").classes("text-grey")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancelar", on_click=dialog.close).props("flat")
                ui.button(
                    "Excluir",
                    icon="delete",
                    on_click=lambda: excluir(name, dialog),
                ).props("color=negative")
        dialog.open()

    def excluir(name: str, dialog: object) -> None:
        deletar_modelo(name)
        dialog.close()  # type: ignore[attr-defined]
        refresh()
        ui.notify(f"Modelo {name} excluído", type="info")

    def download(name: str) -> None:
        ui.notify(f"Baixando modelo {name}... Isso pode demorar.", type="info")

        def run() -> None:
            try:
                baixar_modelo(
                    name,
                    on_progress=lambda msg: progress_queue.put(("info", msg)),
                )
                progress_queue.put(("done", name))
            except Exception as e:
                progress_queue.put(("error", str(e)))

        threading.Thread(target=run, daemon=True).start()

    def check_progress() -> None:
        while not progress_queue.empty():
            try:
                item = progress_queue.get_nowait()
            except queue.Empty:
                break

            if item[0] == "info":
                ui.notify(item[1], type="info")
            elif item[0] == "done":
                ui.notify(f"Modelo {item[1]} baixado!", type="positive")
                refresh()
            elif item[0] == "error":
                ui.notify(f"Erro: {item[1]}", type="negative")

    ui.timer(1.0, check_progress)

    refresh()
