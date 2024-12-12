import sqlite3

def conectar_banco():
    conn = sqlite3.connect("baseDeDados.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas (
        numero_conta TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        saldo REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_conta TEXT NOT NULL,
        operacao TEXT NOT NULL,
        valor REAL NOT NULL,
        FOREIGN KEY(numero_conta) REFERENCES contas(numero_conta)
    )
    """)
    conn.commit()
    return conn

def criar_conta(conn):
    cursor = conn.cursor()
    numero_conta = input("Digite o número da conta (único): ").strip()
    nome = input("Digite o nome do titular da conta: ").strip()
    try:
        saldo_inicial = float(input("Digite o saldo inicial (positivo): "))
        if saldo_inicial < 0:
            raise ValueError("O saldo inicial deve ser positivo.")
    except ValueError as e:
        print(f"Erro: {e}")
        return
    try:
        cursor.execute("INSERT INTO contas (numero_conta, nome, saldo) VALUES (?, ?, ?)",
                       (numero_conta, nome, saldo_inicial))
        conn.commit()
        print(f"Conta criada com sucesso para {nome}!")
    except sqlite3.IntegrityError:
        print("Erro: O número da conta já existe.")

def consultar_saldo(conn):
    cursor = conn.cursor()
    numero_conta = input("Digite o número da conta: ").strip()
    cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (numero_conta,))
    conta = cursor.fetchone()
    if conta:
        print(f"Saldo atual da conta {numero_conta}: R$ {conta[0]:.2f}")
    else:
        print("Erro: Conta não encontrada.")

def depositar(conn):
    cursor = conn.cursor()
    numero_conta = input("Digite o número da conta: ").strip()
    try:
        valor = float(input("Digite o valor a ser depositado: "))
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser positivo.")
    except ValueError as e:
        print(f"Erro: {e}")
        return
    cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (numero_conta,))
    conta = cursor.fetchone()
    if conta:
        novo_saldo = conta[0] + valor
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", (novo_saldo, numero_conta))
        cursor.execute("INSERT INTO historico (numero_conta, operacao, valor) VALUES (?, 'Depósito', ?)",
                       (numero_conta, valor))
        conn.commit()
        print(f"Depósito realizado! Novo saldo: R$ {novo_saldo:.2f}")
    else:
        print("Erro: Conta não encontrada.")

def sacar(conn):
    cursor = conn.cursor()
    numero_conta = input("Digite o número da conta: ").strip()
    try:
        valor = float(input("Digite o valor a ser sacado: "))
        if valor <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
    except ValueError as e:
        print(f"Erro: {e}")
        return
    cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (numero_conta,))
    conta = cursor.fetchone()
    if conta:
        if conta[0] >= valor:
            novo_saldo = conta[0] - valor
            cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", (novo_saldo, numero_conta))
            cursor.execute("INSERT INTO historico (numero_conta, operacao, valor) VALUES (?, 'Saque', ?)",
                           (numero_conta, valor))
            conn.commit()
            print(f"Saque realizado! Novo saldo: R$ {novo_saldo:.2f}")
        else:
            print("Erro: Saldo insuficiente.")
    else:
        print("Erro: Conta não encontrada.")

def encerrar_conta(conn):
    cursor = conn.cursor()
    numero_conta = input("Digite o número da conta: ").strip()
    cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (numero_conta,))
    conta = cursor.fetchone()
    if conta:
        if conta[0] == 0:
            cursor.execute("DELETE FROM contas WHERE numero_conta = ?", (numero_conta,))
            conn.commit()
            print(f"Conta {numero_conta} encerrada com sucesso.")
        else:
            print("Erro: O saldo precisa ser zero para encerrar a conta.")
    else:
        print("Erro: Conta não encontrada.")

def menu():
    conn = conectar_banco()
    while True:
        print("\nMenu do Sistema Bancário")
        print("1. Criar Conta")
        print("2. Consultar Saldo")
        print("3. Depositar")
        print("4. Sacar")
        print("5. Encerrar Conta")
        print("6. Sair")
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            criar_conta(conn)
        elif escolha == "2":
            consultar_saldo(conn)
        elif escolha == "3":
            depositar(conn)
        elif escolha == "4":
            sacar(conn)
        elif escolha == "5":
            encerrar_conta(conn)
        elif escolha == "6":
            print("Saindo do sistema...")
            conn.close()
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
