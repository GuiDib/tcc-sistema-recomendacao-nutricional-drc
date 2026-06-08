"""
OntoDRC — Motor de Inferência e Recomendação Nutricional
TCC Guilherme Bessa — UnB/FCTE — Semana 5

Módulo principal do sistema de recomendação. Contém:
- classificar_estagio(): classifica o estágio da DRC com base na TFG (KDIGO)
- recommend(): gera recomendações personalizadas para um perfil de paciente
- Testes com perfis sintéticos cobrindo os 5 estágios da DRC
"""

from owlready2 import get_ontology
import os

# ============================================================
# CARREGAR ONTOLOGIA
# ============================================================
OWL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontologia_nutricional_renal_v3.owl")
onto = get_ontology(f"file://{OWL_PATH}").load()


# ============================================================
# FUNÇÃO: CLASSIFICAR ESTÁGIO DA DRC
# ============================================================
def classificar_estagio(tfg, em_dialise=False):
    """
    Classifica o estágio da DRC com base na TFG (mL/min/1.73m²)
    conforme os critérios KDIGO.

    Parâmetros:
        tfg (float): Taxa de Filtração Glomerular
        em_dialise (bool): Se o paciente está em diálise

    Retorna:
        dict com 'estagio' (str), 'classe' (str), 'descricao' (str)
    """
    if em_dialise or tfg < 15:
        return {
            "estagio": "G5",
            "classe": "EstagioG5",
            "descricao": "Falência renal (TFG < 15 mL/min ou em diálise)"
        }
    elif tfg < 30:
        return {
            "estagio": "G4",
            "classe": "EstagioG4",
            "descricao": "Redução severa (TFG 15–29 mL/min)"
        }
    elif tfg < 45:
        return {
            "estagio": "G3b",
            "classe": "EstagioG3b",
            "descricao": "Redução moderada a severa (TFG 30–44 mL/min)"
        }
    elif tfg < 60:
        return {
            "estagio": "G3a",
            "classe": "EstagioG3a",
            "descricao": "Redução leve a moderada (TFG 45–59 mL/min)"
        }
    elif tfg < 90:
        return {
            "estagio": "G2",
            "classe": "EstagioG2",
            "descricao": "Redução leve (TFG 60–89 mL/min)"
        }
    else:
        return {
            "estagio": "G1",
            "classe": "EstagioG1",
            "descricao": "Função normal ou elevada (TFG ≥ 90 mL/min)"
        }


# ============================================================
# FUNÇÃO: BUSCAR RESTRIÇÕES DO ESTÁGIO NA ONTOLOGIA
# ============================================================
def buscar_restricoes(estagio_id):
    """
    Consulta a ontologia para obter as restrições nutricionais
    associadas a um estágio da DRC.

    Parâmetros:
        estagio_id (str): ID do estágio na ontologia (ex: "G3b")

    Retorna:
        dict com limites por nutriente (mg/dia ou g/kg/dia)
    """
    estagio_ind = getattr(onto, estagio_id, None)
    restricoes = {
        "potassio_mg": None,
        "sodio_mg": None,
        "fosforo_mg": None,
        "proteina_gkg": None,
        "liquido_ml": None
    }

    if estagio_ind and hasattr(estagio_ind, 'temRestricao'):
        for r in estagio_ind.temRestricao:
            tipos = [c.name for c in r.is_a]
            limite_mg = r.limiteDiarioMg[0] if r.limiteDiarioMg else None
            limite_gkg = r.limiteDiarioGkg[0] if r.limiteDiarioGkg else None

            if "RestricaoPotassio" in tipos and limite_mg:
                restricoes["potassio_mg"] = limite_mg
            elif "RestricaoSodio" in tipos and limite_mg:
                restricoes["sodio_mg"] = limite_mg
            elif "RestricaoFosforo" in tipos and limite_mg:
                restricoes["fosforo_mg"] = limite_mg
            elif "RestricaoProteina" in tipos and limite_gkg:
                restricoes["proteina_gkg"] = limite_gkg
            elif "RestricaoLiquido" in tipos and limite_mg:
                restricoes["liquido_ml"] = limite_mg

    return restricoes


# ============================================================
# FUNÇÃO: BUSCAR ALIMENTOS NA ONTOLOGIA
# ============================================================
def buscar_alimentos():
    """
    Consulta a ontologia e retorna todos os alimentos cadastrados
    com seus dados nutricionais.

    Retorna:
        list de dicts com dados de cada alimento
    """
    categorias = ['Fruta', 'Verdura', 'Leguminosa', 'Cereal', 'Proteina',
                  'Laticinio', 'Bebida', 'Industrializado', 'Tuberculo', 'Ovo']
    alimentos = []

    for ind in onto.individuals():
        classes_nomes = [c.name for c in ind.is_a]
        if any(c in categorias for c in classes_nomes):
            alimentos.append({
                "nome": ind.name,
                "categoria": next((c for c in classes_nomes if c in categorias), "?"),
                "potassio": ind.potassioPor100g[0] if ind.potassioPor100g else 0,
                "sodio": ind.sodioPor100g[0] if ind.sodioPor100g else 0,
                "fosforo": ind.fosforoPor100g[0] if ind.fosforoPor100g else 0,
                "proteina": ind.proteinaPor100g[0] if ind.proteinaPor100g else 0,
                "calorias": ind.caloriasPor100g[0] if ind.caloriasPor100g else 0,
                "nutrientes_risco": [n.name for n in ind.contemNutriente] if ind.contemNutriente else []
            })

    return alimentos


# ============================================================
# FUNÇÃO: BUSCAR RISCOS CLÍNICOS NA ONTOLOGIA
# ============================================================
def buscar_riscos_nutriente(nutriente_nome):
    """
    Consulta a ontologia para identificar o risco clínico
    associado a um nutriente.

    Retorna:
        str com o nome do risco ou None
    """
    mapa_riscos = {
        "Potassio": "hipercalemia",
        "Sodio": "hipernatremia",
        "Fosforo": "hiperfosfatemia"
    }
    return mapa_riscos.get(nutriente_nome, None)


# ============================================================
# FUNÇÃO PRINCIPAL: RECOMMEND
# ============================================================
def recommend(perfil):
    """
    Gera recomendações nutricionais personalizadas para um paciente
    com Doença Renal Crônica.

    Parâmetros:
        perfil (dict): Perfil do paciente contendo:
            - nome (str): Nome ou identificador
            - idade (int): Idade em anos
            - peso (float): Peso em kg
            - tfg (float): Taxa de Filtração Glomerular (mL/min/1.73m²)
            - em_dialise (bool): Se está em diálise
            - diabetes (bool): Se tem diabetes
            - hipertensao (bool): Se tem hipertensão

    Retorna:
        dict com:
            - paciente: dados do paciente
            - estagio: classificação do estágio
            - restricoes: limites nutricionais aplicáveis
            - permitidos: lista de alimentos permitidos
            - restritos: lista de alimentos restritos (com justificativa)
            - proibidos: lista de alimentos proibidos (com justificativa)
            - alertas: alertas clínicos adicionais
    """

    # 1. Classificar estágio
    estagio = classificar_estagio(perfil["tfg"], perfil.get("em_dialise", False))

    # 2. Buscar restrições na ontologia
    restricoes = buscar_restricoes(estagio["estagio"])

    # 3. Definir limiares de classificação por 100g
    #    Baseados nas restrições do estágio + diretrizes KDIGO/KDOQI
    #    Proibido = risco imediato | Restrito = consumo limitado
    limiares = _calcular_limiares(estagio["estagio"], restricoes, perfil)

    # 4. Buscar alimentos da ontologia
    alimentos = buscar_alimentos()

    # 5. Classificar cada alimento
    permitidos = []
    restritos = []
    proibidos = []
    alertas = []

    for a in alimentos:
        status = "PERMITIDO"
        motivos = []

        # Avaliar potássio
        if limiares["potassio_proibido"] and a["potassio"] > limiares["potassio_proibido"]:
            status = "PROIBIDO"
            motivos.append({
                "nutriente": "Potássio",
                "valor": a["potassio"],
                "limite": limiares["potassio_proibido"],
                "risco": "hipercalemia (arritmia cardíaca)"
            })
        elif limiares["potassio_restrito"] and a["potassio"] > limiares["potassio_restrito"]:
            if status != "PROIBIDO":
                status = "RESTRITO"
            motivos.append({
                "nutriente": "Potássio",
                "valor": a["potassio"],
                "limite": limiares["potassio_restrito"],
                "risco": "hipercalemia"
            })

        # Avaliar sódio
        if limiares["sodio_proibido"] and a["sodio"] > limiares["sodio_proibido"]:
            status = "PROIBIDO"
            motivos.append({
                "nutriente": "Sódio",
                "valor": a["sodio"],
                "limite": limiares["sodio_proibido"],
                "risco": "hipernatremia / sobrecarga hídrica"
            })
        elif limiares["sodio_restrito"] and a["sodio"] > limiares["sodio_restrito"]:
            if status != "PROIBIDO":
                status = "RESTRITO"
            motivos.append({
                "nutriente": "Sódio",
                "valor": a["sodio"],
                "limite": limiares["sodio_restrito"],
                "risco": "hipernatremia"
            })

        # Avaliar fósforo
        if limiares["fosforo_proibido"] and a["fosforo"] > limiares["fosforo_proibido"]:
            status = "PROIBIDO"
            motivos.append({
                "nutriente": "Fósforo",
                "valor": a["fosforo"],
                "limite": limiares["fosforo_proibido"],
                "risco": "hiperfosfatemia (calcificação vascular)"
            })
        elif limiares["fosforo_restrito"] and a["fosforo"] > limiares["fosforo_restrito"]:
            if status != "PROIBIDO":
                status = "RESTRITO"
            motivos.append({
                "nutriente": "Fósforo",
                "valor": a["fosforo"],
                "limite": limiares["fosforo_restrito"],
                "risco": "hiperfosfatemia"
            })

        resultado = {
            "nome": a["nome"],
            "categoria": a["categoria"],
            "status": status,
            "motivos": motivos,
            "justificativa": _gerar_justificativa(a["nome"], status, motivos, estagio["estagio"])
        }

        if status == "PERMITIDO":
            permitidos.append(resultado)
        elif status == "RESTRITO":
            restritos.append(resultado)
        else:
            proibidos.append(resultado)

    # 6. Gerar alertas clínicos adicionais
    if perfil.get("diabetes", False):
        alertas.append("Paciente diabético: atenção redobrada ao controle glicêmico e ao consumo de carboidratos simples.")
    if perfil.get("hipertensao", False):
        alertas.append("Paciente hipertenso: priorizar alimentos com baixo teor de sódio (< 100mg/100g).")
    if perfil.get("em_dialise", False):
        alertas.append("Paciente em diálise: necessidade proteica aumentada (1.0–1.2 g/kg/dia). Controlar líquidos.")
    if estagio["estagio"] in ["G4", "G5"]:
        alertas.append(f"Estágio {estagio['estagio']}: risco elevado. Acompanhamento nutricional frequente é essencial.")

    return {
        "paciente": perfil,
        "estagio": estagio,
        "restricoes": restricoes,
        "limiares_por_100g": limiares,
        "permitidos": permitidos,
        "restritos": restritos,
        "proibidos": proibidos,
        "alertas": alertas,
        "aviso_legal": "Sistema de apoio à decisão. A avaliação final cabe ao nutricionista responsável."
    }


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def _calcular_limiares(estagio, restricoes, perfil):
    """
    Calcula os limiares de classificação (restrito/proibido) por 100g
    de alimento, conforme o estágio da DRC e diretrizes KDIGO/KDOQI.

    Estágios mais avançados = limiares mais rigorosos.
    """
    # Valores padrão: sem restrição (None = não avaliado)
    limiares = {
        "potassio_restrito": None,
        "potassio_proibido": None,
        "sodio_restrito": None,
        "sodio_proibido": None,
        "fosforo_restrito": None,
        "fosforo_proibido": None,
    }

    if estagio in ["G1", "G2"]:
        # Estágios iniciais: sem restrições rigorosas
        # Apenas sinalizar ultraprocessados muito ricos em sódio
        limiares["sodio_restrito"] = 600
        limiares["sodio_proibido"] = 1000

    elif estagio == "G3a":
        # Restrição de sódio ativa
        limiares["sodio_restrito"] = 400
        limiares["sodio_proibido"] = 800
        limiares["fosforo_restrito"] = 200
        limiares["fosforo_proibido"] = 400

    elif estagio == "G3b":
        # Restrições de potássio, sódio e fósforo
        limiares["potassio_restrito"] = 200
        limiares["potassio_proibido"] = 350
        limiares["sodio_restrito"] = 300
        limiares["sodio_proibido"] = 600
        limiares["fosforo_restrito"] = 150
        limiares["fosforo_proibido"] = 300

    elif estagio == "G4":
        # Restrições mais rigorosas
        limiares["potassio_restrito"] = 150
        limiares["potassio_proibido"] = 250
        limiares["sodio_restrito"] = 200
        limiares["sodio_proibido"] = 500
        limiares["fosforo_restrito"] = 100
        limiares["fosforo_proibido"] = 200

    elif estagio == "G5":
        # Restrições máximas (diálise)
        limiares["potassio_restrito"] = 100
        limiares["potassio_proibido"] = 200
        limiares["sodio_restrito"] = 150
        limiares["sodio_proibido"] = 400
        limiares["fosforo_restrito"] = 80
        limiares["fosforo_proibido"] = 150

    # Comorbidades intensificam restrições
    if perfil.get("hipertensao", False) and limiares["sodio_restrito"]:
        limiares["sodio_restrito"] = int(limiares["sodio_restrito"] * 0.8)
        limiares["sodio_proibido"] = int(limiares["sodio_proibido"] * 0.8)

    return limiares


def _gerar_justificativa(nome, status, motivos, estagio):
    """
    Gera uma justificativa semântica legível para a classificação
    de um alimento.
    """
    if status == "PERMITIDO":
        return f"{nome}: valores nutricionais dentro dos limites para estágio {estagio}."

    partes = []
    for m in motivos:
        partes.append(
            f"{m['nutriente']} de {m['valor']:.0f}mg/100g excede o limite "
            f"de {m['limite']:.0f}mg/100g; risco: {m['risco']}"
        )
    classificacao = "restrito" if status == "RESTRITO" else "proibido"
    return f"{nome} classificado como {classificacao} para estágio {estagio}: {'; '.join(partes)}."


def imprimir_resultado(resultado):
    """
    Imprime o resultado da recomendação de forma formatada no terminal.
    """
    p = resultado["paciente"]
    e = resultado["estagio"]
    r = resultado["restricoes"]

    print("\n" + "=" * 70)
    print(f"RECOMENDAÇÃO NUTRICIONAL — {p.get('nome', 'Paciente')}")
    print("=" * 70)

    print(f"\n  Perfil: {p.get('idade', '?')} anos, {p.get('peso', '?')} kg, "
          f"TFG = {p.get('tfg', '?')} mL/min")
    print(f"  Estágio: {e['estagio']} — {e['descricao']}")
    print(f"  Diálise: {'Sim' if p.get('em_dialise') else 'Não'} | "
          f"Diabetes: {'Sim' if p.get('diabetes') else 'Não'} | "
          f"Hipertensão: {'Sim' if p.get('hipertensao') else 'Não'}")

    print(f"\n  Restrições do estágio {e['estagio']}:")
    if r["potassio_mg"]:
        print(f"    Potássio: ≤ {r['potassio_mg']:.0f} mg/dia")
    if r["sodio_mg"]:
        print(f"    Sódio: ≤ {r['sodio_mg']:.0f} mg/dia")
    if r["fosforo_mg"]:
        print(f"    Fósforo: ≤ {r['fosforo_mg']:.0f} mg/dia")
    if r["proteina_gkg"]:
        print(f"    Proteína: ≤ {r['proteina_gkg']:.1f} g/kg/dia")
    if r["liquido_ml"]:
        print(f"    Líquidos: ≤ {r['liquido_ml']:.0f} mL/dia")
    if not any(r.values()):
        print(f"    (sem restrições específicas para este estágio)")

    lim = resultado["limiares_por_100g"]
    print(f"\n  Limiares de classificação (por 100g de alimento):")
    for nutriente in ["potassio", "sodio", "fosforo"]:
        rest = lim.get(f"{nutriente}_restrito")
        proib = lim.get(f"{nutriente}_proibido")
        if rest or proib:
            nome_n = {"potassio": "Potássio", "sodio": "Sódio", "fosforo": "Fósforo"}[nutriente]
            print(f"    {nome_n}: Restrito > {rest}mg | Proibido > {proib}mg")

    print(f"\n  ✅ PERMITIDOS ({len(resultado['permitidos'])}):")
    for a in resultado["permitidos"]:
        print(f"     {a['nome']:<25} [{a['categoria']}]")

    print(f"\n  ⚠️  RESTRITOS ({len(resultado['restritos'])}):")
    for a in resultado["restritos"]:
        motivos_str = "; ".join(
            f"{m['nutriente']}={m['valor']:.0f}mg" for m in a["motivos"]
        )
        print(f"     {a['nome']:<25} [{a['categoria']}] — {motivos_str}")

    print(f"\n  🚫 PROIBIDOS ({len(resultado['proibidos'])}):")
    for a in resultado["proibidos"]:
        motivos_str = "; ".join(
            f"{m['nutriente']}={m['valor']:.0f}mg → {m['risco']}" for m in a["motivos"]
        )
        print(f"     {a['nome']:<25} [{a['categoria']}] — {motivos_str}")

    if resultado["alertas"]:
        print(f"\n  🔔 ALERTAS CLÍNICOS:")
        for alerta in resultado["alertas"]:
            print(f"     • {alerta}")

    total = len(resultado['permitidos']) + len(resultado['restritos']) + len(resultado['proibidos'])
    print(f"\n  RESUMO: {len(resultado['permitidos'])} permitidos | "
          f"{len(resultado['restritos'])} restritos | "
          f"{len(resultado['proibidos'])} proibidos (de {total} alimentos)")
    print(f"\n  ⚕️  {resultado['aviso_legal']}")
    print("=" * 70)


# ============================================================
# TESTES COM PERFIS SINTÉTICOS — 5 ESTÁGIOS DA DRC
# ============================================================
if __name__ == "__main__":

    perfis_teste = [
        {
            "nome": "Maria (G1 — estágio inicial)",
            "idade": 35,
            "peso": 65.0,
            "tfg": 95.0,
            "em_dialise": False,
            "diabetes": False,
            "hipertensao": False
        },
        {
            "nome": "João (G2 — redução leve)",
            "idade": 52,
            "peso": 80.0,
            "tfg": 72.0,
            "em_dialise": False,
            "diabetes": True,
            "hipertensao": False
        },
        {
            "nome": "Ana (G3b — moderado a severo)",
            "idade": 62,
            "peso": 75.0,
            "tfg": 35.0,
            "em_dialise": False,
            "diabetes": True,
            "hipertensao": True
        },
        {
            "nome": "Carlos (G4 — severo)",
            "idade": 70,
            "peso": 72.0,
            "tfg": 22.0,
            "em_dialise": False,
            "diabetes": False,
            "hipertensao": True
        },
        {
            "nome": "Rosa (G5 — diálise)",
            "idade": 48,
            "peso": 68.0,
            "tfg": 10.0,
            "em_dialise": True,
            "diabetes": False,
            "hipertensao": True
        },
    ]

    print("=" * 70)
    print("OntoDRC — TESTES DE RECOMENDAÇÃO (5 Estágios da DRC)")
    print("=" * 70)
    print(f"Ontologia: {onto.base_iri}")
    print(f"Alimentos cadastrados: {len(buscar_alimentos())}")
    print(f"Perfis de teste: {len(perfis_teste)}")

    # Tabela resumo
    print("\n" + "-" * 70)
    print(f"  {'Paciente':<35} {'Estágio':<8} {'Perm.':<6} {'Rest.':<6} {'Proib.':<6}")
    print("-" * 70)

    resultados = []
    for perfil in perfis_teste:
        resultado = recommend(perfil)
        resultados.append(resultado)
        e = resultado["estagio"]["estagio"]
        print(f"  {perfil['nome']:<35} {e:<8} "
              f"{len(resultado['permitidos']):<6} "
              f"{len(resultado['restritos']):<6} "
              f"{len(resultado['proibidos']):<6}")

    print("-" * 70)

    # Imprimir detalhes de cada perfil
    for resultado in resultados:
        imprimir_resultado(resultado)

    # Verificação: estágios mais avançados devem ter mais restrições
    print("\n" + "=" * 70)
    print("VALIDAÇÃO: Progressão das restrições por estágio")
    print("=" * 70)
    for i, resultado in enumerate(resultados):
        e = resultado["estagio"]["estagio"]
        n_proib = len(resultado["proibidos"])
        n_rest = len(resultado["restritos"])
        n_perm = len(resultado["permitidos"])
        barra_proib = "█" * n_proib
        barra_rest = "▓" * n_rest
        barra_perm = "░" * n_perm
        print(f"  {e}  {barra_perm}{barra_rest}{barra_proib}  ({n_perm}P/{n_rest}R/{n_proib}X)")

    print("\n  Esperado: conforme o estágio avança (G1→G5), o número de")
    print("  alimentos proibidos deve aumentar e os permitidos diminuir.")
    print("=" * 70)
