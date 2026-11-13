from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="API Sistema de Gestão de Gastos Fantasmas")

# Banco de dados simulado em memória (armazena o histórico limpo para o front-end)
banco_historico_despesas = []

# Modelo da Transação Bruta (conforme Diagrama de Classes)
class TransacaoBancaria(BaseModel):
    id_transacao: str
    descricao_original: str
    valor: float
    data: date

# Modelo da Despesa Processada / Limpa
class DespesaProcessada(BaseModel):
    id_despesa: str
    nome_traduzido: str
    valor: float
    data: date
    categoria: str
    alerta_gasto_fantasma: bool

@app.get("/")
def ler_raiz():
    return {"mensagem": "API do Sistema de Gestão de Gastos Fantasmas rodando com sucesso!"}

# 1. Rota do Motor de Processamento e Tradução
@app.post("/traduzir-gasto", response_model=DespesaProcessada)
def traduzir_gasto(transacao: TransacaoBancaria):
    texto = transacao.descricao_original.upper()
    
    # Lógica do motor (Pipes and Filters)
    if "MCD" in texto or "MC DONALDS" in texto or "BK" in texto:
        nome_limpo = "Fast Food / Lanchonete"
        categoria = "Alimentação"
    elif "UBER" in texto or "99APP" in texto:
        nome_limpo = "Aplicativo de Transporte"
        categoria = "Transporte"
    elif "NETFLIX" in texto or "SPOTIFY" in texto or "AMAZON PRIME" in texto:
        nome_limpo = "Assinatura Digital"
        categoria = "Gastos Fantasmas / Fixos"
    else:
        nome_limpo = transacao.descricao_original
        categoria = "Outros"

    # Verificação de gasto fantasma
    e_gasto_fantasma = categoria == "Gastos Fantasmas / Fixos"

    # Cria o objeto processado
    despesa_processada = DespesaProcessada(
        id_despesa=transacao.id_transacao,
        nome_traduzido=nome_limpo,
        valor=transacao.valor,
        data=transacao.data,
        categoria=categoria,
        alerta_gasto_fantasma=e_gasto_fantasma
    )

    # Salva no histórico (Persistência)
    banco_historico_despesas.append(despesa_processada)

    return despesa_processada

# 2. Rota para o Dashboard consultar todas as despesas limpas
@app.get("/historico", response_model=list[DespesaProcessada])
def obter_historico():
    """Retorna o histórico completo de transações traduzidas para exibição no painel."""
    return banco_historico_despesas