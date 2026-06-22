"""
OntoDRC — Aplicação Web Flask
TCC Guilherme Bessa — UnB/FCTE

Interface web para o Sistema de Recomendação Nutricional
baseado em ontologias para pacientes com DRC.

Acesso protegido por senha única (sessão). Como o sistema lida com dados
de saúde (sensíveis pela LGPD), o acesso exige autenticação.

Para executar:
    source venv/bin/activate
    pip install -r requirements.txt
    python app.py

Configuração (opcional, via variáveis de ambiente):
    ONTODRC_SENHA      senha de acesso (padrão: ontodrc2026)
    ONTODRC_SECRET_KEY chave de assinatura da sessão (padrão: chave de desenvolvimento)

Acesse: http://localhost:5000
"""

import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)
from motor_recomendacao import recommend

app = Flask(__name__)
app.secret_key = os.environ.get("ONTODRC_SECRET_KEY", "dev-secret-key-trocar-em-producao")

# Senha de acesso compartilhada. Em produção, defina ONTODRC_SENHA no ambiente.
SENHA_ACESSO = os.environ.get("ONTODRC_SENHA", "ontodrc2026")


def requer_login(view):
    """Decorator que bloqueia o acesso a rotas para usuários não autenticados."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("autenticado"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    """Tela de login por senha única."""
    if session.get("autenticado"):
        return redirect(url_for("index"))

    if request.method == "POST":
        senha = request.form.get("senha", "")
        if senha == SENHA_ACESSO:
            session["autenticado"] = True
            destino = request.args.get("next") or url_for("index")
            return redirect(destino)
        flash("Senha incorreta. Tente novamente.")
        return render_template("login.html"), 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Encerra a sessão do usuário."""
    session.clear()
    flash("Sessão encerrada com sucesso.")
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@requer_login
def index():
    """Página inicial com formulário do paciente."""
    return render_template("index.html")


@app.route("/recomendar", methods=["POST"])
@requer_login
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
    except (TypeError, ValueError):
        return render_template(
            "index.html",
            erro="Verifique os campos numéricos (idade, peso e TFG devem ser números válidos).",
        ), 400

    try:
        resultado = recommend(perfil)
    except ValueError as e:
        return render_template("index.html", erro=str(e)), 400

    return render_template("resultado.html", r=resultado)


if __name__ == "__main__":
    print("=" * 50)
    print("OntoDRC — Sistema de Recomendação Nutricional")
    print("Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
