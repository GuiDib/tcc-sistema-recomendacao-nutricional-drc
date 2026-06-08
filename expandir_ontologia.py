"""
OntoDRC — Expansão da Ontologia para 50+ Alimentos
TCC Guilherme Bessa — UnB/FCTE — Semana 7

Adiciona 27 novos alimentos brasileiros (TACO) à ontologia existente,
totalizando 52 alimentos. Salva como v3.
"""

from owlready2 import get_ontology
import os

OWL_IN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontologia_nutricional_renal_v2.owl")
OWL_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontologia_nutricional_renal_v3.owl")

print("Carregando ontologia v2...")
onto = get_ontology(f"file://{OWL_IN}").load()

# Dados dos 27 novos alimentos (TACO 4a ed.)
# Formato: (nome, classe, K, Na, P, Prot, Cal, nutrientes_risco)
novos_alimentos = [
    # FRUTAS
    ("Melancia", "Fruta", 104, 1, 10, 0.9, 33, []),
    ("Manga", "Fruta", 148, 1, 11, 0.4, 64, []),
    ("Goiaba", "Fruta", 220, 1, 15, 1.1, 54, ["Potassio"]),
    ("Uva", "Fruta", 162, 1, 15, 0.7, 53, []),
    ("Pera", "Fruta", 75, 1, 10, 0.6, 53, []),
    ("Morango", "Fruta", 184, 1, 22, 0.9, 30, []),

    # VERDURAS E LEGUMES
    ("Chuchu", "Verdura", 133, 1, 12, 0.4, 17, []),
    ("Abobrinha", "Verdura", 165, 1, 25, 1.1, 15, []),
    ("Repolho", "Verdura", 170, 18, 22, 1.3, 17, []),
    ("Pepino", "Verdura", 136, 1, 20, 0.7, 10, []),
    ("Beterraba", "Verdura", 375, 60, 35, 1.9, 49, ["Potassio"]),
    ("Couve", "Verdura", 403, 12, 49, 2.9, 27, ["Potassio"]),
    ("Brócolis", "Verdura", 290, 12, 52, 3.6, 25, ["Potassio"]),

    # CEREAIS E TUBÉRCULOS
    ("Aveia", "Cereal", 336, 5, 153, 14.0, 394, ["Potassio", "Fosforo"]),
    ("Farofa", "Cereal", 113, 380, 40, 1.6, 365, ["Sodio"]),
    ("Tapioca", "Tuberculo", 15, 1, 7, 0.0, 340, []),
    ("BatataDoce", "Tuberculo", 340, 12, 36, 1.3, 118, ["Potassio"]),
    ("Inhame", "Tuberculo", 520, 7, 49, 2.0, 97, ["Potassio"]),

    # PROTEÍNAS
    ("Sardinha", "Proteina", 310, 560, 380, 21.0, 164, ["Potassio", "Sodio", "Fosforo"]),
    ("Carne de porco (lombo)", "Proteina", 360, 49, 200, 28.0, 210, ["Potassio", "Fosforo"]),
    ("Fígado bovino", "Proteina", 330, 70, 380, 29.1, 225, ["Potassio", "Fosforo"]),

    # LATICÍNIOS
    ("Iogurte natural", "Laticinio", 186, 52, 119, 4.1, 51, ["Fosforo"]),
    ("Requeijão", "Laticinio", 90, 490, 290, 10.0, 257, ["Sodio", "Fosforo"]),

    # INDUSTRIALIZADOS
    ("Macarrão instantâneo", "Industrializado", 85, 1580, 72, 7.0, 436, ["Sodio"]),
    ("Presunto", "Industrializado", 210, 1120, 130, 18.0, 117, ["Sodio", "Fosforo"]),
    ("Biscoito cream cracker", "Industrializado", 100, 854, 86, 8.3, 432, ["Sodio"]),
    ("Molho de tomate", "Industrializado", 290, 550, 25, 1.2, 30, ["Potassio", "Sodio"]),
]

with onto:
    count = 0
    for nome, classe, k, na, p, prot, cal, riscos in novos_alimentos:
        # Buscar a classe pelo nome
        cls = getattr(onto, classe, None)
        if cls is None:
            print(f"  AVISO: classe '{classe}' não encontrada, pulando {nome}")
            continue

        # Criar indivíduo
        nome_limpo = nome.replace(" ", "").replace("(", "").replace(")", "").replace("í", "i").replace("ã", "a").replace("é", "e").replace("ó", "o")
        ind = cls(nome_limpo)

        # Atribuir valores nutricionais
        ind.potassioPor100g = [float(k)]
        ind.sodioPor100g = [float(na)]
        ind.fosforoPor100g = [float(p)]
        ind.proteinaPor100g = [float(prot)]
        ind.caloriasPor100g = [float(cal)]

        # Associar nutrientes de risco
        for nutriente_nome in riscos:
            nutriente_ind = getattr(onto, nutriente_nome, None)
            if nutriente_ind:
                ind.contemNutriente.append(nutriente_ind)

        count += 1
        print(f"  + {nome:<30} [{classe}] K={k} Na={na} P={p}")

print(f"\nTotal de alimentos adicionados: {count}")

# Contar total de alimentos
categorias = ['Fruta', 'Verdura', 'Leguminosa', 'Cereal', 'Proteina',
              'Laticinio', 'Bebida', 'Industrializado', 'Tuberculo', 'Ovo']
total = sum(1 for ind in onto.individuals()
            if any(c.name in categorias for c in ind.is_a))
print(f"Total de alimentos na ontologia: {total}")

# Salvar
onto.save(file=OWL_OUT, format="rdfxml")
print(f"\nOntologia v3 salva em: {OWL_OUT}")
