"""Página de transcrição — seleção de arquivo + progresso + resultado."""

from __future__ import annotations

import queue
import tempfile
import threading
from pathlib import Path

from nicegui import events, ui

from tecjustica_transcribe.core.config import obter_token_hf
from tecjustica_transcribe.core.transcription import (
    TranscriptionConfig,
    TranscriptionResult,
    executar_pipeline,
)

ETAPAS_PROGRESSO = {
    "modelo": 0.10,
    "audio": 0.25,
    "transcricao": 0.50,
    "alinhamento": 0.70,
    "diarizacao": 0.90,
    "salvando": 1.00,
}


def conteudo() -> None:
    """Renderiza a página de transcrição."""
    progress_queue: queue.Queue = queue.Queue()
    estado = {"transcrevendo": False}

    ui.label("Transcrever Audiência").classes("text-h5 text-bold q-mb-md")

    # --- Seleção de arquivo ---
    with ui.card().classes("w-full q-mb-md"):
        ui.label("Arquivo de Áudio/Vídeo").classes("text-subtitle1 text-bold")

        caminho_input = ui.input(
            label="Caminho do arquivo",
            placeholder="/mnt/c/.../audiencia.mp4",
        ).classes("w-full")

        def on_upload(e: events.UploadEventArguments) -> None:
            temp_dir = Path(tempfile.gettempdir()) / "tecjustica"
            temp_dir.mkdir(exist_ok=True)
            dest = temp_dir / e.name
            dest.write_bytes(e.content.read())
            caminho_input.value = str(dest)
            ui.notify(f"Arquivo carregado: {e.name}", type="positive")

        ui.upload(
            label="Ou arraste um arquivo aqui",
            on_upload=on_upload,
            auto_upload=True,
        ).props('accept=".mp4,.wav,.mp3,.m4a,.ogg,.flac" max-file-size=524288000').classes(
            "w-full"
        )

    # --- Opções ---
    with ui.card().classes("w-full q-mb-md"):
        ui.label("Opções").classes("text-subtitle1 text-bold")

        with ui.row().classes("w-full items-end gap-4"):
            output_input = ui.input(
                label="Pasta de saída",
                value="./transcricoes",
            ).classes("flex-1")

            modelo_select = ui.select(
                options=["large-v2", "medium", "small", "tiny"],
                value="large-v2",
                label="Modelo",
            ).classes("w-40")

        diarizacao_switch = ui.switch(
            "Identificar falantes (diarização)", value=True
        ).classes("q-mt-sm")

    # --- Progresso (oculto até iniciar) ---
    progresso_card = ui.card().classes("w-full q-mb-md")
    progresso_card.visible = False

    with progresso_card:
        progresso_label = ui.label("Iniciando...").classes("text-subtitle2")
        progresso_bar = ui.linear_progress(value=0, show_value=False).classes(
            "w-full"
        )

    # --- Resultado (oculto até concluir) ---
    resultado_card = ui.card().classes("w-full q-mb-md")
    resultado_card.visible = False

    with resultado_card:
        ui.icon("check_circle", color="positive").classes("text-3xl")
        resultado_label = ui.label("").classes("q-mt-sm")

    # --- Erro (oculto) ---
    erro_label = ui.label("").classes("text-negative text-bold")
    erro_label.visible = False

    # --- Timer para consumir fila de progresso ---
    def check_progress() -> None:
        while not progress_queue.empty():
            try:
                item = progress_queue.get_nowait()
            except queue.Empty:
                break

            if item[0] == "progress":
                _, etapa, msg = item
                progresso_label.text = msg
                if etapa in ETAPAS_PROGRESSO:
                    progresso_bar.value = ETAPAS_PROGRESSO[etapa]

            elif item[0] == "done":
                result: TranscriptionResult = item[1]
                estado["transcrevendo"] = False
                btn_transcrever.enable()
                progresso_label.text = "Concluído!"
                progresso_bar.value = 1.0
                resultado_card.visible = True
                resultado_label.text = (
                    f"Arquivos gerados em {result.caminho_txt.parent}/:\n"
                    f"  {result.caminho_txt.name} (texto puro)\n"
                    f"  {result.caminho_srt.name} (legendas)\n"
                    f"  {result.caminho_json.name} (dados completos)"
                )
                ui.notify("Transcrição concluída!", type="positive")

            elif item[0] == "error":
                error_msg = item[1]
                estado["transcrevendo"] = False
                btn_transcrever.enable()
                progresso_card.visible = False
                erro_label.text = f"Erro: {error_msg}"
                erro_label.visible = True
                ui.notify(f"Erro: {error_msg}", type="negative")

    ui.timer(0.5, check_progress)

    # --- Botão transcrever ---
    def transcrever() -> None:
        arquivo = caminho_input.value.strip()
        if not arquivo:
            ui.notify("Selecione um arquivo primeiro", type="warning")
            return

        if not Path(arquivo).exists():
            ui.notify(f"Arquivo não encontrado: {arquivo}", type="negative")
            return

        token: str | None = None
        if diarizacao_switch.value:
            token = obter_token_hf()
            if not token:
                ui.notify(
                    "Token HuggingFace não configurado. Vá em Configurações.",
                    type="negative",
                )
                return

        # Resetar UI
        estado["transcrevendo"] = True
        btn_transcrever.disable()
        progresso_card.visible = True
        resultado_card.visible = False
        erro_label.visible = False
        progresso_bar.value = 0
        progresso_label.text = "Iniciando..."

        config = TranscriptionConfig(
            arquivo=Path(arquivo),
            output_dir=Path(output_input.value),
            diarizacao=diarizacao_switch.value,
            modelo=modelo_select.value,
        )

        def run() -> None:
            try:
                result = executar_pipeline(
                    config,
                    hf_token=token,
                    on_progress=lambda etapa, msg: progress_queue.put(
                        ("progress", etapa, msg)
                    ),
                )
                progress_queue.put(("done", result))
            except Exception as e:
                progress_queue.put(("error", str(e)))

        threading.Thread(target=run, daemon=True).start()

    btn_transcrever = ui.button(
        "Transcrever", icon="mic", on_click=transcrever
    ).classes("bg-primary text-white text-bold")
