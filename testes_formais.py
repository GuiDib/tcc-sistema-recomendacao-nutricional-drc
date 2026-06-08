"""
OntoDRC — Testes Formais e Métricas de Avaliação
TCC Guilherme Bessa — UnB/FCTE — Semana 8

Implementa:
1. Taxa de Rejeição de Alimentos Nocivos (TRAN)
2. 20 casos de teste com resultado esperado validado por KDIGO/KDOQI
3. Tabulação de acertos, erros e casos limítrofes
4. Métricas complementares: acurácia, sensibilidade, especificidade

Referências clínicas para os resultados esperados:
- KDIGO 2024 Clinical Practice Guideline for CKD
- KDOQI Clinical Practice Guideline for Nutrition in CKD (2020)
- Vasconcelos et al. (2021) - Nutrição e DRC
- Tabela TACO 4a edição (NEPA/Unicamp)
"""

from motor_recomendacao import recommend, buscar_alimentos
import os

# ============================================================
# DEFINIÇÃO DOS 20 CASOS DE TESTE
# ============================================================
# Cada caso: (alimento, estágio_tfg, dialise, esperado, justificativa_clinica)
# esperado: "PERMITIDO", "RESTRITO" ou "PROIBIDO"
#
# A justificativa clínica é baseada em:
# - Limites de K, Na, P por 100g para cada estágio (KDIGO/KDOQI)
# - Valores nutricionais da tabela TACO

CASOS_DE_TESTE = [
    # === ESTÁGIO G1 (TFG=95) — Sem restrições rigorosas ===
    {
        "id": 1,
        "alimento": "BananaPrata",
        "perfil": {"nome": "Teste01", "idade": 35, "peso": 70, "tfg": 95.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PERMITIDO",
        "justificativa": "G1: sem restrições de potássio. Banana (K=358mg) é segura neste estágio."
    },
    {
        "id": 2,
        "alimento": "ArrozBranco",
        "perfil": {"nome": "Teste02", "idade": 40, "peso": 75, "tfg": 95.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PERMITIDO",
        "justificativa": "G1: arroz branco (K=62, Na=1, P=18) é seguro em todos os estágios."
    },
    {
        "id": 3,
        "alimento": "Salsicha",
        "perfil": {"nome": "Teste03", "idade": 45, "peso": 80, "tfg": 95.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PROIBIDO",
        "justificativa": "G1: mesmo sem restrições rigorosas, salsicha (Na=1077mg) excede limiar de ultraprocessados."
    },

    # === ESTÁGIO G3a (TFG=50) — Restrição de sódio ativa ===
    {
        "id": 4,
        "alimento": "MacaFuji",
        "perfil": {"nome": "Teste04", "idade": 55, "peso": 72, "tfg": 50.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PERMITIDO",
        "justificativa": "G3a: maçã (K=75, Na=1, P=9) é segura — baixo teor em todos os nutrientes críticos."
    },
    {
        "id": 5,
        "alimento": "PaoFrances",
        "perfil": {"nome": "Teste05", "idade": 58, "peso": 78, "tfg": 50.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "RESTRITO",
        "justificativa": "G3a: pão francês (Na=648mg) excede limiar de sódio restrito (400mg) para este estágio."
    },
    {
        "id": 6,
        "alimento": "Mortadela",
        "perfil": {"nome": "Teste06", "idade": 60, "peso": 85, "tfg": 50.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": True},
        "esperado": "PROIBIDO",
        "justificativa": "G3a + hipertensão: mortadela (Na=1180mg) excede limiar proibido. Hipertensão agrava restrição de sódio."
    },

    # === ESTÁGIO G3b (TFG=35) — Restrições múltiplas ===
    {
        "id": 7,
        "alimento": "BananaPrata",
        "perfil": {"nome": "Teste07", "idade": 62, "peso": 75, "tfg": 35.0,
                   "em_dialise": False, "diabetes": True, "hipertensao": True},
        "esperado": "PROIBIDO",
        "justificativa": "G3b: banana (K=358mg) excede limiar proibido de potássio (350mg). Risco de hipercalemia."
    },
    {
        "id": 8,
        "alimento": "Abacaxi",
        "perfil": {"nome": "Teste08", "idade": 62, "peso": 75, "tfg": 35.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PERMITIDO",
        "justificativa": "G3b: abacaxi (K=131, Na=1, P=8) está dentro de todos os limites para este estágio."
    },
    {
        "id": 9,
        "alimento": "FeijãoCarioca",
        "perfil": {"nome": "Teste09", "idade": 65, "peso": 70, "tfg": 35.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "RESTRITO",
        "justificativa": "G3b: feijão carioca (K=256mg) excede limiar restrito de potássio (200mg) mas não o proibido (350mg)."
    },
    {
        "id": 10,
        "alimento": "QueijoMinas",
        "perfil": {"nome": "Teste10", "idade": 60, "peso": 73, "tfg": 35.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": True},
        "esperado": "PROIBIDO",
        "justificativa": "G3b + hipertensão: queijo minas (Na=370mg, P=355mg) excede limiar de fósforo proibido (300mg)."
    },
    {
        "id": 11,
        "alimento": "PeitoFrango",
        "perfil": {"nome": "Teste11", "idade": 55, "peso": 68, "tfg": 35.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "RESTRITO",
        "justificativa": "G3b: frango (K=245mg, P=195mg) excede limiares de potássio restrito (200mg) e fósforo restrito (150mg)."
    },

    # === ESTÁGIO G4 (TFG=22) — Restrições severas ===
    {
        "id": 12,
        "alimento": "EspinafreCozido",
        "perfil": {"nome": "Teste12", "idade": 70, "peso": 72, "tfg": 22.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": True},
        "esperado": "PROIBIDO",
        "justificativa": "G4: espinafre (K=466mg) excede amplamente o limiar proibido de potássio (250mg). Risco grave de hipercalemia."
    },
    {
        "id": 13,
        "alimento": "MacarraoCozido",
        "perfil": {"nome": "Teste13", "idade": 68, "peso": 70, "tfg": 22.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PERMITIDO",
        "justificativa": "G4: macarrão (K=15, Na=1, P=42) está dentro de todos os limites, mesmo os mais rigorosos."
    },
    {
        "id": 14,
        "alimento": "PatinhoGrelhado",
        "perfil": {"nome": "Teste14", "idade": 72, "peso": 75, "tfg": 22.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "PROIBIDO",
        "justificativa": "G4: patinho (K=370mg, P=228mg) excede limiar proibido de potássio (250mg) e fósforo proibido (200mg)."
    },
    {
        "id": 15,
        "alimento": "LaranjaPera",
        "perfil": {"nome": "Teste15", "idade": 66, "peso": 69, "tfg": 22.0,
                   "em_dialise": False, "diabetes": False, "hipertensao": False},
        "esperado": "RESTRITO",
        "justificativa": "G4: laranja (K=163mg) excede limiar restrito de potássio (150mg) mas não o proibido (250mg)."
    },

    # === ESTÁGIO G5 / DIÁLISE (TFG=10) — Restrições máximas ===
    {
        "id": 16,
        "alimento": "BananaPrata",
        "perfil": {"nome": "Teste16", "idade": 48, "peso": 68, "tfg": 10.0,
                   "em_dialise": True, "diabetes": False, "hipertensao": True},
        "esperado": "PROIBIDO",
        "justificativa": "G5/diálise: banana (K=358mg) excede amplamente o limiar proibido (200mg). Risco imediato de hipercalemia."
    },
    {
        "id": 17,
        "alimento": "RefrigeranteCola",
        "perfil": {"nome": "Teste17", "idade": 50, "peso": 70, "tfg": 10.0,
                   "em_dialise": True, "diabetes": False, "hipertensao": False},
        "esperado": "PERMITIDO",
        "justificativa": "G5: refrigerante cola (K=2, Na=4, P=17) tem valores baixos em todos os nutrientes críticos, apesar de não ter valor nutricional."
    },
    {
        "id": 18,
        "alimento": "Tomate",
        "perfil": {"nome": "Teste18", "idade": 55, "peso": 65, "tfg": 10.0,
                   "em_dialise": True, "diabetes": False, "hipertensao": True},
        "esperado": "PROIBIDO",
        "justificativa": "G5/diálise + hipertensão: tomate (K=222mg) excede limiar proibido de potássio (200mg)."
    },
    {
        "id": 19,
        "alimento": "OvoCozido",
        "perfil": {"nome": "Teste19", "idade": 52, "peso": 72, "tfg": 10.0,
                   "em_dialise": True, "diabetes": False, "hipertensao": False},
        "esperado": "PROIBIDO",
        "justificativa": "G5/diálise: ovo (P=186mg, Na=142mg) excede limiar proibido de fósforo (150mg)."
    },
    {
        "id": 20,
        "alimento": "Abacaxi",
        "perfil": {"nome": "Teste20", "idade": 45, "peso": 60, "tfg": 10.0,
                   "em_dialise": True, "diabetes": False, "hipertensao": False},
        "esperado": "RESTRITO",
        "justificativa": "G5/diálise: abacaxi (K=131mg) excede limiar restrito (100mg) mas não o proibido (200mg)."
    },
]


# ============================================================
# FUNÇÕES DE AVALIAÇÃO
# ============================================================

def executar_testes():
    """Executa todos os 20 casos de teste e retorna resultados."""
    resultados = []

    for caso in CASOS_DE_TESTE:
        rec = recommend(caso["perfil"])

        # Encontrar o alimento nos resultados
        alimento_nome = caso["alimento"]
        obtido = None

        for lista, status in [(rec["permitidos"], "PERMITIDO"),
                              (rec["restritos"], "RESTRITO"),
                              (rec["proibidos"], "PROIBIDO")]:
            for a in lista:
                if a["nome"] == alimento_nome:
                    obtido = status
                    break
            if obtido:
                break

        esperado = caso["esperado"]
        acertou = obtido == esperado

        # Classificar tipo de erro
        tipo_erro = None
        if not acertou:
            if esperado in ["RESTRITO", "PROIBIDO"] and obtido == "PERMITIDO":
                tipo_erro = "FALSO_NEGATIVO"  # CRÍTICO: alimento nocivo classificado como seguro
            elif esperado == "PERMITIDO" and obtido in ["RESTRITO", "PROIBIDO"]:
                tipo_erro = "FALSO_POSITIVO"  # Menos grave: alimento seguro classificado como restrito
            elif esperado == "PROIBIDO" and obtido == "RESTRITO":
                tipo_erro = "SUBCLASSIFICACAO"  # Detectou risco mas subestimou gravidade
            elif esperado == "RESTRITO" and obtido == "PROIBIDO":
                tipo_erro = "SUPERCLASSIFICACAO"  # Detectou risco e superestimou gravidade
            else:
                tipo_erro = "OUTRO"

        resultados.append({
            "id": caso["id"],
            "alimento": alimento_nome,
            "estagio": rec["estagio"]["estagio"],
            "esperado": esperado,
            "obtido": obtido or "NAO_ENCONTRADO",
            "acertou": acertou,
            "tipo_erro": tipo_erro,
            "justificativa": caso["justificativa"]
        })

    return resultados


def calcular_metricas(resultados):
    """Calcula TRAN e métricas complementares."""

    total = len(resultados)
    acertos = sum(1 for r in resultados if r["acertou"])

    # TRAN: proporção de alimentos nocivos corretamente rejeitados
    # Nocivo = esperado RESTRITO ou PROIBIDO
    nocivos_esperados = [r for r in resultados if r["esperado"] in ["RESTRITO", "PROIBIDO"]]
    nocivos_detectados = [r for r in nocivos_esperados
                          if r["obtido"] in ["RESTRITO", "PROIBIDO"]]
    tran = len(nocivos_detectados) / len(nocivos_esperados) if nocivos_esperados else 0

    # Sensibilidade (recall para nocivos)
    sensibilidade = tran  # Mesmo cálculo

    # Especificidade: proporção de seguros corretamente permitidos
    seguros_esperados = [r for r in resultados if r["esperado"] == "PERMITIDO"]
    seguros_corretos = [r for r in seguros_esperados if r["obtido"] == "PERMITIDO"]
    especificidade = len(seguros_corretos) / len(seguros_esperados) if seguros_esperados else 0

    # Acurácia geral
    acuracia = acertos / total if total else 0

    # Classificação exata (3 classes)
    acuracia_exata = acertos / total if total else 0

    # Falsos negativos (CRÍTICO)
    falsos_negativos = [r for r in resultados if r["tipo_erro"] == "FALSO_NEGATIVO"]

    # Falsos positivos
    falsos_positivos = [r for r in resultados if r["tipo_erro"] == "FALSO_POSITIVO"]

    # Sub/super classificações
    sub = [r for r in resultados if r["tipo_erro"] == "SUBCLASSIFICACAO"]
    super_ = [r for r in resultados if r["tipo_erro"] == "SUPERCLASSIFICACAO"]

    return {
        "total_testes": total,
        "acertos": acertos,
        "erros": total - acertos,
        "tran": tran,
        "sensibilidade": sensibilidade,
        "especificidade": especificidade,
        "acuracia": acuracia,
        "falsos_negativos": len(falsos_negativos),
        "falsos_positivos": len(falsos_positivos),
        "subclassificacoes": len(sub),
        "superclassificacoes": len(super_),
        "detalhes_fn": falsos_negativos,
        "detalhes_fp": falsos_positivos,
        "nocivos_esperados": len(nocivos_esperados),
        "nocivos_detectados": len(nocivos_detectados),
        "seguros_esperados": len(seguros_esperados),
        "seguros_corretos": len(seguros_corretos),
    }


# ============================================================
# EXECUÇÃO E SAÍDA
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print("OntoDRC — TESTES FORMAIS E MÉTRICAS DE AVALIAÇÃO")
    print("=" * 80)
    print(f"Total de casos de teste: {len(CASOS_DE_TESTE)}")
    print(f"Ontologia: 52 alimentos (TACO) | 6 estágios | 5 tipos de restrição\n")

    resultados = executar_testes()
    metricas = calcular_metricas(resultados)

    # --- TABELA DE RESULTADOS ---
    print("-" * 80)
    print(f"  {'ID':<4} {'Alimento':<22} {'Estágio':<8} {'Esperado':<11} {'Obtido':<11} {'Resultado':<10}")
    print("-" * 80)

    for r in resultados:
        marca = "✅" if r["acertou"] else "❌"
        detalhe = ""
        if r["tipo_erro"]:
            detalhe = f" ({r['tipo_erro']})"
        print(f"  {r['id']:<4} {r['alimento']:<22} {r['estagio']:<8} "
              f"{r['esperado']:<11} {r['obtido']:<11} {marca}{detalhe}")

    print("-" * 80)

    # --- MÉTRICAS ---
    print(f"\n{'=' * 80}")
    print("MÉTRICAS DE AVALIAÇÃO")
    print(f"{'=' * 80}")

    print(f"\n  TAXA DE REJEIÇÃO DE ALIMENTOS NOCIVOS (TRAN)")
    print(f"  Definição: proporção de alimentos clinicamente contraindicados")
    print(f"  que o sistema identifica corretamente como Restritos ou Proibidos.")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Alimentos nocivos esperados:   {metricas['nocivos_esperados']}")
    print(f"  Alimentos nocivos detectados:  {metricas['nocivos_detectados']}")
    print(f"  TRAN = {metricas['nocivos_detectados']}/{metricas['nocivos_esperados']}"
          f" = {metricas['tran']:.1%}")
    print(f"  ─────────────────────────────────────────────────────")

    print(f"\n  MÉTRICAS COMPLEMENTARES")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Acurácia geral (3 classes):    {metricas['acertos']}/{metricas['total_testes']}"
          f" = {metricas['acuracia']:.1%}")
    print(f"  Sensibilidade (nocivos):       {metricas['tran']:.1%}")
    print(f"  Especificidade (seguros):      {metricas['seguros_corretos']}/{metricas['seguros_esperados']}"
          f" = {metricas['especificidade']:.1%}")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Falsos negativos (CRÍTICO):    {metricas['falsos_negativos']}")
    print(f"  Falsos positivos:              {metricas['falsos_positivos']}")
    print(f"  Subclassificações:             {metricas['subclassificacoes']}")
    print(f"  Superclassificações:           {metricas['superclassificacoes']}")

    if metricas["falsos_negativos"] > 0:
        print(f"\n  ⚠️  ATENÇÃO — FALSOS NEGATIVOS DETECTADOS:")
        for fn in metricas["detalhes_fn"]:
            print(f"     Caso {fn['id']}: {fn['alimento']} ({fn['estagio']}) — "
                  f"esperado {fn['esperado']}, obtido {fn['obtido']}")
            print(f"              {fn['justificativa']}")
    else:
        print(f"\n  ✅ NENHUM FALSO NEGATIVO — Todos os alimentos nocivos foram detectados.")

    if metricas["falsos_positivos"] > 0:
        print(f"\n  ℹ️  FALSOS POSITIVOS (menos graves):")
        for fp in metricas["detalhes_fp"]:
            print(f"     Caso {fp['id']}: {fp['alimento']} ({fp['estagio']}) — "
                  f"esperado {fp['esperado']}, obtido {fp['obtido']}")

    # --- RESUMO PARA O ARTIGO ---
    print(f"\n{'=' * 80}")
    print("RESUMO PARA INCLUSÃO NO ARTIGO")
    print(f"{'=' * 80}")
    print(f"""
  O protótipo foi avaliado com um conjunto de {metricas['total_testes']} casos de teste,
  cada um definindo um alimento específico, um estágio da DRC (G1 a G5)
  e a classificação esperada (Permitido, Restrito ou Proibido) conforme
  as diretrizes KDIGO/KDOQI.

  A Taxa de Rejeição de Alimentos Nocivos (TRAN) obtida foi de
  {metricas['tran']:.1%}, indicando que {metricas['nocivos_detectados']} dos
  {metricas['nocivos_esperados']} alimentos clinicamente contraindicados foram
  corretamente identificados pelo sistema.

  A acurácia geral (classificação exata em 3 classes) foi de
  {metricas['acuracia']:.1%} ({metricas['acertos']}/{metricas['total_testes']}).
  A especificidade (alimentos seguros corretamente permitidos) foi de
  {metricas['especificidade']:.1%} ({metricas['seguros_corretos']}/{metricas['seguros_esperados']}).

  Foram registrados {metricas['falsos_negativos']} falso(s) negativo(s) —
  situação em que um alimento nocivo seria classificado como permitido,
  representando risco clínico direto ao paciente.
""")
    print("=" * 80)
