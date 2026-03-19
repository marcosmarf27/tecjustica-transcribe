# Requisitos: tecjustica-transcribe

## Descrição

CLI publicável no PyPI que transcreve vídeos MP4 de audiências judiciais usando WhisperX. Inclui comando `init` que diagnostica e prepara a máquina automaticamente, e comando de transcrição com diarização (identificação de falantes). Instalável via `uv tool install` ou `pip install`.

## Critérios de Aceitação

- [ ] Pacote instalável via `uv tool install tecjustica-transcribe` ou `pip install tecjustica-transcribe`
- [ ] Comando `tecjustica-transcribe init` verifica: driver NVIDIA, CUDA, ffmpeg, modelos WhisperX — e instala/baixa o que faltar
- [ ] Comando `tecjustica-transcribe transcrever audiencia.mp4` gera .srt, .txt, .json com timestamps e identificação de falantes
- [ ] Diarização funcional (identifica SPEAKER_00, SPEAKER_01, etc.)
- [ ] Funciona em máquinas com 6GB+ de VRAM
- [ ] Saída organizada em pasta `./transcricoes/`
- [ ] Mensagens de erro claras e em português

## Dependências

- Python >=3.10, <3.14
- whisperx >=3.8.2 (core de transcrição)
- torch ~=2.8.0 com CUDA 12.8
- ffmpeg (verificado pelo `init`, não é dep Python)
- Driver NVIDIA compatível com CUDA 12.8+ (verificado pelo `init`)
- Token HuggingFace do usuário (para diarização com pyannote)

## Features Relacionadas

- Futuro: interface web para upload e visualização
- Futuro: API REST para integração com TecJustiça
- Futuro: renomear SPEAKER_XX para "Juíza", "Advogado", etc.
