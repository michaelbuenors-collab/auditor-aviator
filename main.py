import sqlite3
import pandas as pd
import requests
import time
from datetime import datetime

# ==========================================================
# CONFIGURAÇÕES DO TELEGRAM
# ==========================================================
TELEGRAM_TOKEN = "8936856843:AAE2xzKqgwpFqSORNzdIJAFvVk-8WhZbzSc"
CHAT_ID = "1030274897"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar no Telegram: {e}")

# ==========================================================
# INICIALIZAÇÃO DO BANCO DE DADOS
# ==========================================================
def init_db():
    conn = sqlite3.connect('auditoria_aviator.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rodadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            multiplicador REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ==========================================================
# AUDITORIA DE CONFORMIDADE E DETECÇÃO DE ERROS DA CASA
# ==========================================================
def auditar_e_gerar_relatorio():
    conn = sqlite3.connect('auditoria_aviator.db')
    df = pd.read_sql_query("SELECT multiplicador, timestamp FROM rodadas WHERE timestamp >= datetime('now', '-1 hour')", conn)
    conn.close()

    total_rodadas = len(df)
    if total_rodadas < 10:
        enviar_telegram("📊 *IA Auditora:* Coletando dados para formar a amostra de análise...")
        return

    # Frequências reais observadas
    crashes_1_00 = len(df[df['multiplicador'] == 1.00])
    velas_baixas = len(df[df['multiplicador'] < 1.50])
    velas_2x = len(df[df['multiplicador'] >= 2.00])
    velas_10x = len(df[df['multiplicador'] >= 10.00])

    pct_1_00 = (crashes_1_00 / total_rodadas) * 100
    pct_baixas = (velas_baixas / total_rodadas) * 100
    pct_2x = (velas_2x / total_rodadas) * 100
    pct_10x = (velas_10x / total_rodadas) * 100

    # Valores teóricos esperados pelo algoritmo Spribe (RTP 97%)
    desvio_1_00 = pct_1_00 - 3.0
    desvio_2x = pct_2x - 48.5

    # Diagnóstico da IA
    if pct_1_00 > 6.0:
        status_plataforma = "🚨 *ANOMALIA DETECTADA:* Taxa de Crash (1.00x) anormalmente alta. Forte indício de retenção abusiva."
    elif desvio_2x < -10.0:
        status_plataforma = "⚠️ *DESVIO DE RTP:* A casa está entregando 10% a menos de velas verdes que o modelo padrão."
    else:
        status_plataforma = "🟢 *DENTRO DOS PARÂMETROS:* Plataforma operando dentro da distribuição estatística teórica."

    relatorio = (
        f"🤖 *RELATÓRIO DE AUDITORIA DE IA (ÚLTIMA HORA)*\n"
        f"Amostra analisada: *{total_rodadas} jogos*\n\n"
        f"• Status: {status_plataforma}\n\n"
        f"📈 *Métricas Observadas vs. Teóricas:*\n"
        f"• Crash (1.00x): *{pct_1_00:.1f}%* (Teórico: ~3.0%)\n"
        f"• Velas < 1.50x: *{pct_baixas:.1f}%*\n"
        f"• Velas ≥ 2.00x: *{pct_2x:.1f}%* (Teórico: 48.5%)\n"
        f"• Velas Rosas (≥ 10.0x): *{pct_10x:.1f}%*\n"
    )

    enviar_telegram(relatorio)

# ==========================================================
# LOOP CONTINUO NA NUVEM
# ==========================================================
if __name__ == "__main__":
    init_db()
    enviar_telegram("🚀 *SISTEMA DE IA AUDITORA INICIADO NA NUVEM!* Monitoramento 24/7 ativo.")
    
    contador_segundos = 0
    while True:
        time.sleep(60)
        contador_segundos += 60
        
        # A cada 1 hora (3600s), gera o relatório de auditoria
        if contador_segundos >= 3600:
            auditar_e_gerar_relatorio()
            contador_segundos = 0
