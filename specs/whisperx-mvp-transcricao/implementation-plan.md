# Plano de Implementação: tecjustica-transcribe

## Visão Geral

Criar um pacote Python CLI chamado `tecjustica-transcribe`, publicável no PyPI, que encapsula WhisperX com dois comandos principais: `init` (diagnóstico e setup) e `transcrever` (transcrição com diarização). Gerenciado com `uv`.

## Fase 1: Estrutura do Projeto

Criar a estrutura do pacote Python com `pyproject.toml` e entry points.

### Tarefas

- [x] Criar estrutura de diretórios do pacote
- [x] Criar `pyproject.toml` com metadados, dependências e entry point CLI
- [x] Criar módulo principal com CLI (usando `click` ou `typer`)
- [x] Configurar build system (`hatchling` ou `setuptools`)

### Detalhes Técnicos

```
~/whisperx/
├── pyproject.toml
├── README.md
├── src/
│   └── tecjustica_transcribe/
│       ├── __init__.py
│       ├── __main__.py        # python -m tecjustica_transcribe
│       ├── cli.py             # comandos click/typer
│       ├── diagnostico.py     # lógica do init
│       └── transcrever.py     # lógica de transcrição
```

```toml
# pyproject.toml (essencial)
[project]
name = "tecjustica-transcribe"
version = "0.1.0"
requires-python = ">=3.10,<3.14"
dependencies = [
    "whisperx>=3.8.2",
    "click>=8.0",
    "rich>=13.0",  # output bonito no terminal
]

[project.scripts]
tecjustica-transcribe = "tecjustica_transcribe.cli:main"
```

## Fase 2: Comando `init` — Diagnóstico e Setup

Comando que verifica todos os pré-requisitos e prepara a máquina.

### Tarefas

- [x] Implementar verificação de driver NVIDIA (`nvidia-smi`)
- [x] Implementar verificação de CUDA (via PyTorch)
- [x] Implementar verificação de ffmpeg
- [x] Implementar verificação de VRAM disponível
- [x] Implementar download dos modelos WhisperX (large-v2 + wav2vec2-pt)
- [x] Implementar configuração do token HuggingFace (para diarização)
- [x] Implementar relatório de diagnóstico com status visual (rich)

### Detalhes Técnicos

```bash
# Uso esperado:
tecjustica-transcribe init

# Saída esperada:
# ┌─────────────────────────────────────────┐
# │  TecJustiça Transcribe — Diagnóstico    │
# ├─────────────────────────────────────────┤
# │ Driver NVIDIA    ✅ 591.44              │
# │ CUDA             ✅ 13.1                │
# │ GPU              ✅ RTX 3050 (6 GB)     │
# │ ffmpeg           ✅ 6.1.1               │
# │ Python           ✅ 3.12.3              │
# │ Modelos          ⬇️  Baixando large-v2... │
# │ Token HuggingFace ❌ Não configurado    │
# └─────────────────────────────────────────┘
#
# ⚠️  Token HuggingFace necessário para diarização.
# Cole seu token (huggingface.co/settings/tokens): ___
```

Verificações no `diagnostico.py`:
```python
# NVIDIA driver
subprocess.run(["nvidia-smi"], capture_output=True)

# CUDA via PyTorch
import torch
torch.cuda.is_available()
torch.cuda.get_device_name(0)
torch.cuda.get_device_properties(0).total_mem

# ffmpeg
subprocess.run(["ffmpeg", "-version"], capture_output=True)

# Modelos — pré-baixar para evitar surpresa na primeira transcrição
from faster_whisper import WhisperModel
model = WhisperModel("large-v2", device="cuda", compute_type="float16")

# Token HuggingFace — salvar em ~/.config/tecjustica/config.json
```

## Fase 3: Comando `transcrever` — Transcrição com Diarização

Comando principal que recebe um MP4 e gera a transcrição com identificação de falantes.

### Tarefas

- [x] Implementar comando `transcrever` que aceita caminho do MP4
- [x] Integrar WhisperX para transcrição (large-v2, pt, float16)
- [x] Integrar diarização com pyannote (lê token salvo pelo `init`)
- [x] Gerar saída em .srt, .txt e .json
- [x] Ajustar batch_size automaticamente baseado na VRAM disponível
- [x] Mostrar progresso no terminal (rich progress bar)
- [x] Tratar erros comuns (OOM, arquivo não encontrado, token ausente)

### Detalhes Técnicos

```bash
# Uso esperado:
tecjustica-transcribe transcrever audiencia.mp4
tecjustica-transcribe transcrever audiencia.mp4 --output ./saida
tecjustica-transcribe transcrever audiencia.mp4 --sem-diarizacao
tecjustica-transcribe transcrever /mnt/c/Users/marcos/Downloads/audiencia.mp4

# Saída esperada:
# 🎙️  Transcrevendo: audiencia.mp4
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:02:15
#
# ✅ Transcrição concluída!
# 📁 Arquivos gerados em ./transcricoes/:
#    • audiencia.txt  (texto puro)
#    • audiencia.srt  (legendas com timestamps)
#    • audiencia.json (dados completos + falantes)
```

Lógica no `transcrever.py`:
```python
import whisperx

# 1. Carregar modelo
model = whisperx.load_model("large-v2", device="cuda", compute_type="float16", language="pt")

# 2. Transcrever
audio = whisperx.load_audio(arquivo_mp4)
result = model.transcribe(audio, batch_size=batch_size)

# 3. Alinhar timestamps
model_a, metadata = whisperx.load_align_model(language_code="pt", device="cuda")
result = whisperx.align(result["segments"], model_a, metadata, audio, device="cuda")

# 4. Diarizar (identificar falantes)
diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device="cuda")
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)

# 5. Auto-ajuste de batch_size baseado na VRAM
vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024**3)
batch_size = 8 if vram_gb >= 6 else 4
```

## Fase 4: Empacotamento e Teste Local

Testar o pacote localmente antes de publicar.

### Tarefas

- [x] Instalar o pacote localmente com `uv pip install -e .`
- [x] Testar `tecjustica-transcribe init`
- [x] Testar `tecjustica-transcribe transcrever` com MP4 real
- [x] Verificar que a diarização identifica falantes no .json e .srt
- [x] Testar `uv tool install .` para simular instalação do PyPI

### Detalhes Técnicos

```bash
cd ~/whisperx

# Instalar em modo desenvolvimento
uv pip install -e .

# Testar
tecjustica-transcribe init
tecjustica-transcribe transcrever audiencia.mp4

# Simular instalação como ferramenta global
uv tool install .
tecjustica-transcribe --help
```

## Fase 5: Publicar no PyPI

Publicar o pacote para que qualquer pessoa possa instalar.

### Tarefas

- [x] Criar conta no PyPI (se não tiver)
- [x] Configurar token de publicação
- [x] Build do pacote: `uv build`
- [x] Publicar: `uv publish`
- [x] Testar instalação limpa: `uv tool install tecjustica-transcribe`

### Detalhes Técnicos

```bash
# Build
uv build

# Publicar (precisa de token PyPI)
uv publish

# Testar instalação do PyPI
uv tool install tecjustica-transcribe

# Uso final pelo cliente:
tecjustica-transcribe init
tecjustica-transcribe transcrever minha-audiencia.mp4
```
