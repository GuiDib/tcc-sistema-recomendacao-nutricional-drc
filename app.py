"""
OntoDRC — Aplicação Web Flask
TCC Guilherme Bessa — UnB/FCTE — Semana 6

Interface web para o Sistema de Recomendação Nutricional
baseado em ontologias para pacientes com DRC.

Para executar:
    source venv/bin/activate
    pip install flask owlready2
    python app.py

Acesse: http://localhost:5000
"""

from flask import Flask, render_template, request
from motor_recomendacao import recommend

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """Página inicial com formulário do paciente."""
    return render_template("index.html")


@app.route("/recomendar", methods=["POST"])
def recomendar():
    """Processa o formulário e gera recomendações."""
    try:
        perfil = {
            "nome": request.form.get("nome", "Paciente"),
            "idade": int(request.form.get("idade", 0)),
            "peso": float(request.form.get("peso", 0)),
            "tfg": float(request.form.get("tfg", 0)),
            "em_dialise": request.form.get("em_dialise") == "sim",
            "diabetes": request.form.get("diabetes") == "sim",
            "hipertensao": request.form.get("hipertensao") == "sim",
        }

        resultado = recommend(perfil)
        return render_template("resultado.html", r=resultado)

    except Exception as e:
        return render_template("index.html", erro=str(e))


if __name__ == "__main__":
    print("=" * 50)
    print("OntoDRC — Sistema de Recomendação Nutricional")
    print("Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
