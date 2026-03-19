"""Página de diagnóstico — verificações do sistema com indicadores visuais."""

from __future__ import annotations

from nicegui import ui

from tecjustica_transcribe.core.checks import executar_todas_verificacoes


def conteudo() -> None:
    """Renderiza a página de diagnóstico do sistema."""
    ui.label("Diagnóstico do Sistema").classes("text-h5 text-bold q-mb-md")

    container = ui.column().classes("w-full")

    def verificar() -> None:
        container.clear()
        resultados = executar_todas_verificacoes()

        with container:
            with ui.card().classes("w-full"):
                for r in resultados:
                    with ui.row().classes("w-full items-center q-py-sm"):
                        if r.ok:
                            ui.icon("check_circle", color="positive").classes(
                                "text-xl"
                            )
                        else:
                            ui.icon("cancel", color="negative").classes("text-xl")
                        ui.label(r.nome).classes("text-bold").style("min-width:180px")
                        ui.label(r.detalhe).classes("text-grey")

            # Resumo
            falhas = [r for r in resultados if not r.ok]
            if not falhas:
                ui.label("Tudo pronto para transcrever!").classes(
                    "text-positive text-bold q-mt-md"
                )
            else:
                ui.label(
                    f"{len(falhas)} problema(s) encontrado(s). Resolva antes de transcrever."
                ).classes("text-warning text-bold q-mt-md")

    verificar()

    ui.button("Re-verificar", icon="refresh", on_click=verificar).classes("q-mt-md")
