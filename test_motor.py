"""
OntoDRC — Testes unitários do motor de recomendação (pytest)
TCC Guilherme Bessa — UnB/FCTE

Cobre:
- Fronteiras de classificar_estagio (G1–G5 + diálise)
- Tabela de limiares por estágio + agravamento por hipertensão
- Validação de entrada de recommend()
- Formatação de nome (camelCase -> legível)
- Regressão da distribuição por estágio (deve bater com o baseline do artigo)

Rodar:  pytest -v
"""

import pytest

from motor_recomendacao import (
    classificar_estagio,
    recommend,
    buscar_alimentos,
    _calcular_limiares,
    _formatar_nome,
    _validar_perfil,
    LIMIARES_POR_ESTAGIO,
)


# ============================================================
# classificar_estagio — fronteiras KDIGO
# ============================================================
@pytest.mark.parametrize("tfg,esperado", [
    (120, "G1"),   # função elevada
    (90, "G1"),    # limite inferior G1
    (89, "G2"),    # limite superior G2
    (60, "G2"),    # limite inferior G2
    (59, "G3a"),
    (45, "G3a"),
    (44, "G3b"),
    (30, "G3b"),
    (29, "G4"),
    (15, "G4"),
    (14, "G5"),
    (5, "G5"),
    (0, "G5"),
])
def test_classificar_estagio_fronteiras(tfg, esperado):
    assert classificar_estagio(tfg)["estagio"] == esperado


def test_dialise_forca_g5_mesmo_com_tfg_alta():
    # Paciente em diálise é sempre G5, independentemente da TFG informada
    assert classificar_estagio(95, em_dialise=True)["estagio"] == "G5"


def test_classificar_estagio_retorna_campos():
    res = classificar_estagio(35)
    assert set(res.keys()) == {"estagio", "classe", "descricao"}
    assert res["classe"] == "EstagioG3b"


# ============================================================
# Tabela de limiares
# ============================================================
def test_limiares_g1_sem_restricao_potassio():
    lim = _calcular_limiares("G1", {})
    assert lim["potassio_restrito"] is None
    assert lim["potassio_proibido"] is None
    assert lim["sodio_proibido"] == 1000


def test_limiares_g5_mais_rigorosos_que_g3b():
    g3b = _calcular_limiares("G3b", {})
    g5 = _calcular_limiares("G5", {})
    assert g5["potassio_proibido"] < g3b["potassio_proibido"]
    assert g5["fosforo_proibido"] < g3b["fosforo_proibido"]


def test_hipertensao_intensifica_sodio():
    base = _calcular_limiares("G3b", {})
    com_hipertensao = _calcular_limiares("G3b", {"hipertensao": True})
    assert com_hipertensao["sodio_restrito"] == int(base["sodio_restrito"] * 0.8)
    assert com_hipertensao["sodio_proibido"] == int(base["sodio_proibido"] * 0.8)


def test_hipertensao_nao_afeta_estagio_sem_sodio():
    # G1/G2 têm sódio, então hipertensão afeta; mas potássio segue None
    lim = _calcular_limiares("G1", {"hipertensao": True})
    assert lim["potassio_restrito"] is None


def test_tabela_limiares_cobre_todos_estagios():
    for estagio in ["G1", "G2", "G3a", "G3b", "G4", "G5"]:
        assert estagio in LIMIARES_POR_ESTAGIO


# ============================================================
# Validação de entrada
# ============================================================
def test_validar_perfil_sem_tfg_levanta_erro():
    with pytest.raises(ValueError, match="tfg"):
        _validar_perfil({"nome": "X"})


def test_validar_perfil_tfg_nao_numerica():
    with pytest.raises(ValueError, match="TFG inválida"):
        _validar_perfil({"tfg": "abc"})


def test_validar_perfil_tfg_negativa():
    with pytest.raises(ValueError, match="negativa"):
        _validar_perfil({"tfg": -5})


def test_validar_perfil_converte_tfg_para_float():
    assert _validar_perfil({"tfg": "35"})["tfg"] == 35.0


def test_recommend_sem_tfg_levanta_value_error():
    with pytest.raises(ValueError):
        recommend({"nome": "Sem TFG"})


# ============================================================
# Formatação de nome
# ============================================================
@pytest.mark.parametrize("entrada,esperado", [
    ("BananaPrata", "Banana Prata"),
    ("FeijãoCarioca", "Feijão Carioca"),
    ("EspinafreCozido", "Espinafre Cozido"),
    ("Tomate", "Tomate"),
    ("RefrigeranteCola", "Refrigerante Cola"),
])
def test_formatar_nome(entrada, esperado):
    assert _formatar_nome(entrada) == esperado


# ============================================================
# Estrutura do retorno de recommend
# ============================================================
def test_recommend_estrutura_basica():
    r = recommend({"nome": "Teste", "idade": 60, "peso": 70, "tfg": 35,
                   "em_dialise": False, "diabetes": False, "hipertensao": False})
    for chave in ("paciente", "estagio", "restricoes", "permitidos",
                  "restritos", "proibidos", "alertas", "aviso_legal"):
        assert chave in r
    # cada alimento classificado tem nome_exibicao legível
    assert all("nome_exibicao" in a for a in r["permitidos"])


def test_recommend_alertas_comorbidades():
    r = recommend({"nome": "T", "idade": 60, "peso": 70, "tfg": 35,
                   "em_dialise": False, "diabetes": True, "hipertensao": True})
    texto = " ".join(r["alertas"]).lower()
    assert "diab" in texto
    assert "sódio" in texto or "sodio" in texto


# ============================================================
# Regressão: distribuição por estágio (baseline do artigo)
# ============================================================
# (permitidos, restritos, proibidos) sem comorbidades
BASELINE_DISTRIBUICAO = {
    "G1": (46, 2, 4),
    "G2": (46, 2, 4),
    "G3a": (39, 8, 5),
    "G3b": (18, 17, 17),
    "G4": (12, 13, 27),
    "G5": (6, 13, 33),
}

PERFIS_REGRESSAO = {
    "G1": (95, False), "G2": (72, False), "G3a": (50, False),
    "G3b": (35, False), "G4": (22, False), "G5": (10, True),
}


@pytest.mark.parametrize("estagio", list(BASELINE_DISTRIBUICAO.keys()))
def test_distribuicao_por_estagio_nao_regride(estagio):
    tfg, dialise = PERFIS_REGRESSAO[estagio]
    r = recommend({"nome": "Reg", "idade": 50, "peso": 70, "tfg": tfg,
                   "em_dialise": dialise, "diabetes": False, "hipertensao": False})
    obtido = (len(r["permitidos"]), len(r["restritos"]), len(r["proibidos"]))
    assert obtido == BASELINE_DISTRIBUICAO[estagio]


def test_total_alimentos_constante():
    # A base tem 52 alimentos; a soma das 3 listas deve ser sempre 52
    r = recommend({"nome": "T", "idade": 50, "peso": 70, "tfg": 35,
                   "em_dialise": False, "diabetes": False, "hipertensao": False})
    total = len(r["permitidos"]) + len(r["restritos"]) + len(r["proibidos"])
    assert total == len(buscar_alimentos()) == 52
