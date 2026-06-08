# Sistema de Recomendação Nutricional Baseado em Ontologias para Pacientes com Doença Renal Crônica

**OntoDRC** — Sistema de Recomendação Nutricional baseado em Ontologias e Inteligência Artificial para orientação alimentar personalizada a pacientes com Doença Renal Crônica (DRC).

**Trabalho de Conclusão de Curso — Guilherme França Dib de Oliveira Bessa**
Orientador: Prof. Dr. Cláudio Gottschalg-Duque
UnB / FCTE — 2026

## Sobre

O sistema recebe dados clínicos do paciente (idade, peso, TFG, comorbidades), classifica automaticamente o estágio da DRC (G1–G5 conforme KDIGO), consulta uma ontologia OWL com 52 alimentos brasileiros da tabela TACO e gera recomendações alimentares categorizadas como **Permitido**, **Restrito** ou **Proibido**, acompanhadas de justificativas semânticas e alertas clínicos.

## Instalação

```bash
git clone https://github.com/SEU_USUARIO/tcc-sistema-recomendacao-nutricional-drc.git
cd tcc-sistema-recomendacao-nutricional-drc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Interface web
```bash
python app.py
# Acesse http://localhost:5000
```

### Testes formais
```bash
python testes_formais.py
```

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Ontologia | OWL 2 / Protégé 5.6 |
| Raciocinador | HermiT |
| Manipulação OWL | owlready2 |
| Interface | Flask |
| Base alimentar | TACO 4ª ed. (NEPA/Unicamp) |
| Diretrizes clínicas | KDIGO / KDOQI |

## Métricas

| Métrica | Resultado |
|---|---|
| TRAN (Taxa de Rejeição de Alimentos Nocivos) | 100% |
| Acurácia (20 casos de teste) | 100% |
| Falsos negativos | 0 |

## Licença

Este projeto é parte de um Trabalho de Conclusão de Curso e está disponível para fins acadêmicos.
