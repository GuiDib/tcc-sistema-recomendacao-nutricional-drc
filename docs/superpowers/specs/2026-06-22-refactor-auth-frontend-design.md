# Design — Refatoração, Autenticação e Melhorias de Frontend (OntoDRC)

**Data:** 2026-06-22
**Autor:** Guilherme Bessa (via Claude Code)
**Escopo:** Refatorar o motor preservando resultados, adicionar autenticação por senha
única, corrigir bugs e polir o frontend, e adicionar testes unitários.

## Constraint inegociável

A classificação dos alimentos **não pode mudar**. Os 20 casos de `testes_formais.py`
e a distribuição por estágio (baseline abaixo) devem permanecer idênticos após o
refactor. Verificação obrigatória antes de cada commit.

Baseline (sem comorbidade, exceto onde indicado): G1 46/2/4 · G2 46/2/4 · G3a 39/8/5 ·
G3b 18/17/17 · G4 12/13/27 · G5 6/13/33. TRAN 100%, 20/20 testes.

## Decisões (confirmadas pelo usuário)

- **Autenticação:** senha única compartilhada, via sessão Flask.
- **Frontend:** corrigir bugs + polir (mantém identidade visual atual).
- **Backend:** refatorar preservando resultados.

## 1. Backend — `motor_recomendacao.py`

- **Tabela de limiares por estágio** (`LIMIARES_POR_ESTAGIO`, dict de dicts) substitui a
  cadeia `if/elif` com números mágicos. Valores idênticos aos atuais.
- **Multiplicador de hipertensão** (sódio × 0.8, `int`) mantido exatamente.
- **`_calcular_limiares(estagio, perfil)`** — remove o parâmetro `restricoes` (nunca usado).
- **Remove código morto:** `buscar_riscos_nutriente()` (nunca chamado).
- **Lazy-load da ontologia:** `_get_onto()` com cache de módulo, em vez de carregar no import.
- **Validação de entrada:** `recommend(perfil)` valida campos obrigatórios (`tfg`) e tipos;
  lança `ValueError` com mensagem clara em vez de `KeyError`.
- **Nome de exibição:** cada alimento ganha `nome_exibicao` (camelCase → "Banana Prata")
  via `_formatar_nome()`. Não altera o ID/`nome` usado nos testes.

## 2. Autenticação — `app.py`

- `SECRET_KEY` e `SENHA_ACESSO` lidos de variável de ambiente, com fallback
  (`ontodrc2026`) para a apresentação.
- Rotas `/login` (GET/POST) e `/logout`. Template novo `login.html`.
- Decorator `@requer_login` protege `/` e `/recomendar`.
- Validação: erro de formulário mostra mensagem amigável, sem vazar stack/exceção crua.

## 3. Frontend

- **`templates/base.html`** + **`static/style.css`** compartilhado. `index`, `resultado`
  e `login` passam a estender a base. Elimina CSS duplicado.
- **Bugs corrigidos:**
  - Nomes legíveis (`nome_exibicao`).
  - Nome × categoria em linhas separadas (espaçamento).
  - `peso` formatado.
  - Fallback de restrições considera proteína/líquido; remove `·` solto.
- **Acessibilidade:** status não depende só de cor (texto + ícone + `aria-label`); foco visível.
- **UX:** busca/filtro por categoria nas listas da tela de resultado (JS vanilla, sem libs).

## 4. Testes — `test_motor.py` (pytest)

- Fronteiras de `classificar_estagio` (G1–G5 + diálise).
- Tabela de limiares (valores corretos por estágio + multiplicador de hipertensão).
- Validação de entrada de `recommend` (erros claros).
- Formatação de nome (camelCase → legível).
- Regressão: distribuição por estágio == baseline.
- `testes_formais.py` continua funcionando. `pytest>=8.0` adicionado ao `requirements.txt`.

## Plano de execução (ordem + verificação)

1. Refatorar `motor_recomendacao.py` → rodar `testes_formais.py` (deve dar 20/20 idêntico).
2. Criar `test_motor.py` → `pytest` verde.
3. Auth em `app.py` + `login.html`.
4. `base.html` + `static/style.css` + refatorar templates + correções + busca.
5. Subir app, validar login/GET/POST via curl.
6. Atualizar `requirements.txt`, `CLAUDE.md`, `README.md`.
7. Commit(s) + push.

## Fora de escopo

- Contas individuais / banco de usuários (escolhido: senha única).
- Revisão das regras clínicas / mudança de limiares (escolhido: preservar resultados).
- Divergências artigo×código (ex.: `.tex` diz G1=49, código=46) — anotadas para tratar
  depois, junto com a revisão do `.tex`.
