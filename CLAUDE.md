# CLAUDE.md — Contexto do Projeto

## O que é este projeto

**Sistema de Recomendação Nutricional Baseado em Ontologias para Pacientes com Doença Renal Crônica**

TCC de Guilherme França Dib de Oliveira Bessa — UnB/FCTE (2026).
Orientador: Prof. Dr. Cláudio Gottschalg-Duque.
Nome do sistema: **OntoDRC**.

O sistema recebe dados de um paciente renal (idade, peso, TFG, comorbidades), classifica o estágio da DRC (G1-G5 pela KDIGO), consulta uma ontologia OWL com 52 alimentos da tabela TACO e gera recomendações (Permitido/Restrito/Proibido) com justificativas semânticas.

## Stack tecnológico

- **Python 3.10+** — linguagem principal
- **owlready2** — carregamento e manipulação da ontologia OWL
- **Flask** — interface web
- **OWL 2 / Protégé 5.6** — modelagem da ontologia
- **HermiT** — raciocinador (via owlready2)
- **Tabela TACO (Unicamp)** — base nutricional dos alimentos
- **Diretrizes KDIGO/KDOQI** — regras clínicas por estágio

## Estrutura do repositório

```
tcc-sistema-recomendacao-nutricional-drc/
├── CLAUDE.md                  ← Este arquivo (contexto para Claude Code)
├── README.md                  ← Documentação do projeto
├── requirements.txt           ← Dependências Python
├── .gitignore
├── app.py                     ← Aplicação Flask
├── motor_recomendacao.py      ← Módulo principal: recommend(perfil)
├── expandir_ontologia.py      ← Script para expandir de 25→52 alimentos
├── testes_formais.py          ← 20 casos de teste + TRAN + métricas
├── test_motor.py              ← Testes unitários (pytest)
├── ontologia_nutricional_renal_v2.owl  ← 25 alimentos (base)
├── ontologia_nutricional_renal_v3.owl  ← 52 alimentos (atual)
├── templates/
│   ├── base.html              ← Layout base (Jinja) compartilhado
│   ├── login.html             ← Tela de login (senha única)
│   ├── index.html             ← Formulário do paciente
│   └── resultado.html         ← Tela de recomendações
├── static/
│   └── style.css              ← Estilos compartilhados
├── docs/
│   └── cronograma_tcc.pdf     ← Cronograma de 14 semanas
└── latex/
    └── tcc_guilherme_final.tex ← Artigo LaTeX (versão final)
```

## Arquitetura do sistema

```
Paciente → Interface Flask → Classificador de Estágio (TFG→G1-G5)
                                    ↓
                            Ontologia OntoDRC (OWL 2)
                                    ↓
                            Motor de Inferência (owlready2)
                              ↓                ↓
                    Recomendações          Alertas Clínicos
                    (Permitido/             (hipercalemia,
                     Restrito/              hiperfosfatemia,
                     Proibido)              hipernatremia)
                              ↓
                    Avaliação do Nutricionista
```

## Ontologia OntoDRC

### 7 Classes principais
- **Alimento** (subclasses: Fruta, Verdura, Leguminosa, Cereal, Proteina, Laticinio, Bebida, Industrializado, Tuberculo, Ovo + AlimentoPermitido/Restrito/Proibido)
- **Nutriente** (Macronutriente, Micronutriente, Eletrólito)
- **Paciente**
- **EstagioDRC** (G1, G2, G3a, G3b, G4, G5)
- **RestricaoNutricional** (Potássio, Sódio, Fósforo, Proteína, Líquido)
- **RecomendacaoDietetica**
- **RiscoClinico** (Hipercalemia, Hiperfosfatemia, Hipernatremia, SobrecargaHidrica, DesnutricaoProteicoEnergetica)

### 8 Object Properties
- `contemNutriente`: Alimento → Nutriente
- `possuiEstagio`: Paciente → EstagioDRC
- `temRestricao`: EstagioDRC → RestricaoNutricional
- `recomendaAlimento`: Recomendação → Alimento
- `restringeAlimento`: Restrição → Alimento
- `provocaRisco`: Nutriente → RiscoClinico
- `geradaPara`: Recomendação → Paciente
- `comBaseEm`: Recomendação → RestricaoNutricional

### Data Properties dos alimentos (por 100g)
`potassioPor100g`, `sodioPor100g`, `fosforoPor100g`, `proteinaPor100g`, `caloriasPor100g`

### Restrições por estágio (KDIGO/KDOQI)
| Estágio | Potássio | Sódio | Fósforo | Proteína |
|---------|----------|-------|---------|----------|
| G1-G2   | sem      | sem   | sem     | sem      |
| G3a     | sem      | ≤2000mg/dia | sem | sem    |
| G3b     | ≤2000mg/dia | ≤2000mg/dia | ≤800mg/dia | ≤0.6g/kg/dia |
| G4      | ≤1500mg/dia | ≤2000mg/dia | ≤800mg/dia | ≤0.6g/kg/dia |
| G5      | ≤1500mg/dia | ≤2000mg/dia | ≤800mg/dia | ≤1.2g/kg/dia + líq ≤1000mL |

## Função principal: recommend(perfil)

Entrada:
```python
perfil = {
    "nome": "Paciente X",
    "idade": 62,
    "peso": 75.0,
    "tfg": 35.0,          # mL/min/1.73m²
    "em_dialise": False,
    "diabetes": True,
    "hipertensao": True
}
```

Saída: dict com `estagio`, `restricoes`, `permitidos`, `restritos`, `proibidos` (cada um com justificativa semântica), `alertas`.

## Métricas de avaliação (Semana 8)

- **TRAN** (Taxa de Rejeição de Alimentos Nocivos): 100% (14/14)
- **Acurácia**: 100% (20/20 casos de teste)
- **Falsos negativos**: 0 (nenhum alimento nocivo classificado como seguro)
- **Especificidade**: 100% (6/6 seguros corretos)

## Cronograma e estado atual

| Semana | Entrega | Status |
|--------|---------|--------|
| 1 | Correções textuais + plano técnico | ✅ |
| 2 | Trabalhos relacionados + ONS/CKDO | ✅ |
| 3 | Diagrama de arquitetura + Seção 5 | ✅ |
| 4 | Ontologia OWL + Python (owlready2) | ✅ |
| 5 | Motor de inferência + recommend() | ✅ |
| 6 | Interface Flask + alertas | ✅ |
| 7 | 52 alimentos TACO + Metodologia | ✅ |
| 8 | TRAN + 20 testes formais | ✅ |
| 9 | Resultados e Discussão (dados reais) | ⬜ |
| 10 | Formato artigo IMRAD + citações | ⬜ |
| 11 | Feedback do orientador + GitHub | ⬜ |
| 12 | Revisão final | ⬜ |
| 13 | Buffer para ajustes | ⬜ |
| 14 | Slides + ensaio | ⬜ |

Prazo final: 18 de julho de 2026.

## Correções do professor já aplicadas

1. Palavras-chave fora do abstract, separadas por ponto
2. Referências do orientador como "manuscrito não publicado"
3. Apps com anos (MyFitnessPal 2005, FatSecret 2007, Lifesum 2013, Yazio 2015)
4. Ontologias com ref. Gruber (1993)
5. Vulnerabilidade alimentar explicada com IBGE (2023)
6. LGPD contextualizada (art. 5º, art. 11) com refs lei + Botelho (2021)
7. Chen et al. (2019) adicionado junto a Mendes
8. "individualizado" com nota de rodapé
9. "Como destaca" removido (coloquialismo)
10. ONS/CKDO: acesso aberto e gratuito
11. "emergentes" → "disruptivas"
12. Métricas justificadas (TRAN, falso negativo vs falso positivo)
13. TFG explicada na Seção 5.1
14. 7 propriedades semânticas explicadas individualmente
15. Tabela corrigida para twocolumn
16. 6 novas referências bibliográficas

## Referências bibliográficas do artigo

22 referências totais. Principais:
- Gottschalg-Duque (2024) — proposta de pós-doc (manuscrito)
- Aggarwal (2016) — Recommender Systems
- Mendes et al. (2021) — food recommender for older adults
- Zhang et al. (2023) — ontology-driven nutrition
- Mckensy-Sambola et al. (2022) — OWL + SWRL nutrition system
- Göğebakan et al. (2024) — DIAKID ontology for CKD
- Vitali et al. (2025) — systematic review ontologies + XAI
- Gruber (1993) — definição de ontologia
- KDIGO (2024) — guideline para DRC
- Brasil (2018) — LGPD

## Como rodar

```bash
cd tcc-sistema-recomendacao-nutricional-drc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Acesse http://localhost:5000
# Acesso protegido por senha única (padrão: ontodrc2026).
# Configurável via env: ONTODRC_SENHA e ONTODRC_SECRET_KEY.
```

## Comandos úteis

```bash
# Rodar testes formais (TRAN + 20 casos)
python testes_formais.py

# Rodar testes unitários (pytest)
pytest -v

# Expandir ontologia (v2 → v3)
python expandir_ontologia.py

# Rodar motor no terminal
python -c "from motor_recomendacao import recommend; print(recommend({'nome':'Teste','idade':62,'peso':75,'tfg':35,'em_dialise':False,'diabetes':True,'hipertensao':True}))"
```
