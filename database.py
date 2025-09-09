import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "chamados.db"

# Inicializa banco e tabelas
def inicializar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de chamados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regional TEXT,
            loja TEXT,
            lider TEXT,
            motivo TEXT,
            abertura TEXT,
            fechamento TEXT,
            duracao TEXT,
            status TEXT
        )
    """)

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT,
            papel TEXT
        )
    """)

    conn.commit()
    conn.close()


# Ler todos os chamados
def ler_chamados():
    inicializar_banco()
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM chamados", conn)
    return df

# Cadastrar chamado
def cadastrar_chamado(regional, loja, lider, motivo):
    abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chamados (regional, loja, lider, motivo, abertura, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (regional, loja, lider, motivo, abertura, "Aberto"))
        conn.commit()

# Finalizar chamado pelo ID
def finalizar_chamado(chamado_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT abertura FROM chamados WHERE id = ?", (chamado_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        abertura = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        fechamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duracao = str(datetime.now() - abertura).split('.')[0]
        cursor.execute("""
            UPDATE chamados
            SET fechamento=?, duracao=?, status=?
            WHERE id=?
        """, (fechamento, duracao, "Finalizado", chamado_id))
        conn.commit()
    return True

# Cadastrar usuário
def cadastrar_usuario(usuario, senha, papel="user"):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (usuario, senha, papel)
            VALUES (?, ?, ?)
        """, (usuario, senha, papel))
        conn.commit()

# Verificar login
def verificar_usuario(usuario, senha):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT papel FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
        row = cursor.fetchone()
    return row[0] if row else None

# Zerar banco de dados
def zerar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS chamados")
    cursor.execute("DROP TABLE IF EXISTS usuarios")
    conn.commit()
    conn.close()
