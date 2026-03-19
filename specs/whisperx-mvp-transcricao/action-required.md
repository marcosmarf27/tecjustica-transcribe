# Ações Manuais: tecjustica-transcribe

Passos que precisam ser executados manualmente por um humano.

## Antes da Implementação

- [ ] **Ter um arquivo MP4 de audiência** - Necessário para testar a transcrição
- [ ] **Criar token HuggingFace** - Acessar https://huggingface.co/settings/tokens, criar token (read), e aceitar os termos do modelo `pyannote/speaker-diarization-3.1` em https://huggingface.co/pyannote/speaker-diarization-3.1

## Durante a Implementação

- [ ] **Fechar aplicações pesadas no Windows** - RAM de 7.6 GB é apertada. Fechar browsers durante testes

## Para Publicação no PyPI

- [ ] **Criar conta no PyPI** - https://pypi.org/account/register/
- [ ] **Gerar API token no PyPI** - https://pypi.org/manage/account/token/
- [ ] **Verificar nome disponível** - Confirmar que `tecjustica-transcribe` não está ocupado no PyPI

---

> Estas ações também estão listadas em contexto no `implementation-plan.md`
