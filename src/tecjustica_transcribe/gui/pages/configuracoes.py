"""Página de configurações — token HF, pasta padrão, GPU/CPU."""

from __future__ import annotations

from nicegui import ui

from tecjustica_transcribe.core.config import carregar_config, salvar_config, salvar_token_hf


def conteudo() -> None:
    """Renderiza a página de configurações."""
    config = carregar_config()

    ui.label("Configurações").classes("text-h5 text-bold q-mb-md")

    # --- Token HuggingFace ---
    with ui.card().classes("w-full q-mb-md"):
        ui.label("Token HuggingFace").classes("text-subtitle1 text-bold")
        ui.label(
            "Necessário para diarização (identificação de falantes)."
        ).classes("text-caption text-grey q-mb-sm")

        token_input = ui.input(
            label="Token",
            value=config.get("hf_token", ""),
            password=True,
            password_toggle_button=True,
        ).classes("w-full")

        def salvar_token() -> None:
            token = token_input.value.strip()
            if token:
                salvar_token_hf(token)
                ui.notify("Token salvo!", type="positive")
            else:
                ui.notify("Token vazio — diarização não funcionará.", type="warning")

        with ui.row().classes("items-center gap-4 q-mt-sm"):
            ui.button("Salvar token", icon="save", on_click=salvar_token).props(
                "color=primary"
            )
            ui.link(
                "Obter token no HuggingFace",
                "https://huggingface.co/settings/tokens",
                new_tab=True,
            ).classes("text-sm")

        ui.label(
            "Também aceite os termos em: huggingface.co/pyannote/speaker-diarization-3.1"
        ).classes("text-caption text-grey q-mt-sm")

    # --- Preferências de transcrição ---
    with ui.card().classes("w-full q-mb-md"):
        ui.label("Preferências de Transcrição").classes("text-subtitle1 text-bold")

        output_input = ui.input(
            label="Pasta de saída padrão",
            value=config.get("output_dir", "./transcricoes"),
        ).classes("w-full")

        with ui.row().classes("items-end gap-4 q-mt-sm"):
            device_select = ui.select(
                options=["auto", "cuda", "cpu"],
                value=config.get("device", "auto"),
                label="Dispositivo",
            ).classes("w-40")

            batch_input = ui.number(
                label="Batch size (0 = automático)",
                value=config.get("batch_size", 0),
                min=0,
                max=32,
            ).classes("w-48")

        def salvar_preferencias() -> None:
            cfg = carregar_config()
            cfg["output_dir"] = output_input.value
            cfg["device"] = device_select.value
            cfg["batch_size"] = int(batch_input.value or 0)
            salvar_config(cfg)
            ui.notify("Configurações salvas!", type="positive")

        ui.button(
            "Salvar preferências", icon="save", on_click=salvar_preferencias
        ).props("color=primary").classes("q-mt-md")

    # --- Info do config ---
    with ui.expansion("Arquivo de configuração", icon="info").classes("w-full"):
        from tecjustica_transcribe.core.config import CONFIG_FILE

        ui.label(f"Localização: {CONFIG_FILE}").classes("text-caption text-grey")
