from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash BLOB NOT NULL,
                salt BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                celular TEXT NOT NULL,
                idade INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS procedure_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS client_procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                procedure_type_id INTEGER NOT NULL,
                data_procedimento TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
                FOREIGN KEY (procedure_type_id) REFERENCES procedure_types(id) ON DELETE RESTRICT
            )
            """
        )
        conn.commit()


def seed_demo_data() -> None:
    with get_connection() as conn:
        total_clients = conn.execute(
            "SELECT COUNT(*) AS total FROM clients"
        ).fetchone()["total"]

        if total_clients > 0:
            return

        procedimentos = [
            "Botox",
            "Preenchimento labial",
            "Limpeza de pele",
            "Microagulhamento",
            "Peeling",
            "Harmonização facial",
            "Skinbooster",
            "Bioestimulador de colágeno",
        ]

        for nome_procedimento in procedimentos:
            conn.execute(
                """
                INSERT OR IGNORE INTO procedure_types (nome)
                VALUES (?)
                """,
                (nome_procedimento,),
            )

        clientes = [
            ("Ana Silva", "ana.silva@email.com", "21990000001", 24),
            ("Bruna Costa", "bruna.costa@email.com", "21990000002", 27),
            ("Carla Mendes", "carla.mendes@email.com", "21990000003", 31),
            ("Daniela Rocha", "daniela.rocha@email.com", "21990000004", 35),
            ("Eduarda Lima", "eduarda.lima@email.com", "21990000005", 22),
            ("Fernanda Alves", "fernanda.alves@email.com", "21990000006", 29),
            ("Gabriela Nunes", "gabriela.nunes@email.com", "21990000007", 33),
            ("Helena Martins", "helena.martins@email.com", "21990000008", 38),
            ("Isabela Gomes", "isabela.gomes@email.com", "21990000009", 41),
            ("Juliana Barros", "juliana.barros@email.com", "21990000010", 45),
            ("Karina Souza", "karina.souza@email.com", "21990000011", 26),
            ("Larissa Pires", "larissa.pires@email.com", "21990000012", 30),
            ("Mariana Teixeira", "mariana.teixeira@email.com", "21990000013", 34),
            ("Natália Araujo", "natalia.araujo@email.com", "21990000014", 37),
            ("Patricia Melo", "patricia.melo@email.com", "21990000015", 42),
            ("Renata Gomes", "renata.gomes@email.com", "21990000016", 48),
            ("Simone Freitas", "simone.freitas@email.com", "21990000017", 52),
            ("Tatiane Ribeiro", "tatiane.ribeiro@email.com", "21990000018", 39),
            ("Vanessa Duarte", "vanessa.duarte@email.com", "21990000019", 28),
            ("Viviane Castro", "viviane.castro@email.com", "21990000020", 46),
            ("Aline Moreira", "aline.moreira@email.com", "21990000021", 25),
            ("Beatriz Lopes", "beatriz.lopes@email.com", "21990000022", 32),
            ("Camila Farias", "camila.farias@email.com", "21990000023", 36),
            ("Débora Cardoso", "debora.cardoso@email.com", "21990000024", 43),
            ("Eliane Moraes", "eliane.moraes@email.com", "21990000025", 50),
            ("Fabiana Reis", "fabiana.reis@email.com", "21990000026", 55),
            ("Giovana Torres", "giovana.torres@email.com", "21990000027", 23),
            ("Heloisa Batista", "heloisa.batista@email.com", "21990000028", 40),
            ("Iris Campos", "iris.campos@email.com", "21990000029", 47),
            ("Josiane Cunha", "josiane.cunha@email.com", "21990000030", 58),
        ]

        for cliente in clientes:
            conn.execute(
                """
                INSERT INTO clients (nome, email, celular, idade)
                VALUES (?, ?, ?, ?)
                """,
                cliente,
            )

        clientes_db = conn.execute(
            "SELECT id FROM clients ORDER BY id"
        ).fetchall()

        procedimentos_db = conn.execute(
            "SELECT id, nome FROM procedure_types ORDER BY id"
        ).fetchall()

        proc_por_nome = {item["nome"]: item["id"] for item in procedimentos_db}

        atendimentos = [
            ("2025-01-05", "Limpeza de pele"),
            ("2025-01-08", "Botox"),
            ("2025-01-10", "Peeling"),
            ("2025-01-12", "Preenchimento labial"),
            ("2025-01-15", "Limpeza de pele"),
            ("2025-01-18", "Botox"),
            ("2025-01-20", "Microagulhamento"),
            ("2025-01-22", "Skinbooster"),
            ("2025-01-25", "Botox"),
            ("2025-01-28", "Harmonização facial"),
            ("2025-02-02", "Peeling"),
            ("2025-02-05", "Botox"),
            ("2025-02-07", "Preenchimento labial"),
            ("2025-02-10", "Microagulhamento"),
            ("2025-02-14", "Bioestimulador de colágeno"),
            ("2025-02-18", "Botox"),
            ("2025-02-20", "Skinbooster"),
            ("2025-02-24", "Limpeza de pele"),
            ("2025-03-01", "Botox"),
            ("2025-03-03", "Harmonização facial"),
            ("2025-03-06", "Peeling"),
            ("2025-03-09", "Preenchimento labial"),
            ("2025-03-12", "Microagulhamento"),
            ("2025-03-15", "Botox"),
            ("2025-03-18", "Skinbooster"),
            ("2025-03-20", "Bioestimulador de colágeno"),
            ("2025-03-22", "Limpeza de pele"),
            ("2025-03-25", "Botox"),
            ("2025-03-27", "Peeling"),
            ("2025-03-30", "Harmonização facial"),
        ]

        for cliente_row, atendimento in zip(clientes_db, atendimentos):
            data_procedimento, nome_procedimento = atendimento
            conn.execute(
                """
                INSERT INTO client_procedures (client_id, procedure_type_id, data_procedimento)
                VALUES (?, ?, ?)
                """,
                (
                    cliente_row["id"],
                    proc_por_nome[nome_procedimento],
                    data_procedimento,
                ),
            )

        conn.commit()


def add_client(nome: str, email: str, celular: str, idade: int) -> tuple[bool, str]:
    nome = nome.strip()
    email = email.strip().lower()
    celular = celular.strip()

    if not nome:
        return False, "Informe o nome."
    if not email or "@" not in email:
        return False, "Informe um e-mail válido."
    if not celular:
        return False, "Informe o celular."
    if idade < 0:
        return False, "Informe uma idade válida."

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO clients (nome, email, celular, idade)
                VALUES (?, ?, ?, ?)
                """,
                (nome, email, celular, idade),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "Já existe cliente com esse e-mail."

    return True, "Cliente cadastrado com sucesso."


def update_client(client_id: int, nome: str, email: str, celular: str, idade: int) -> tuple[bool, str]:
    nome = nome.strip()
    email = email.strip().lower()
    celular = celular.strip()

    if not nome:
        return False, "Informe o nome."
    if not email or "@" not in email:
        return False, "Informe um e-mail válido."
    if not celular:
        return False, "Informe o celular."
    if idade < 0:
        return False, "Informe uma idade válida."

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE clients
                SET nome = ?, email = ?, celular = ?, idade = ?
                WHERE id = ?
                """,
                (nome, email, celular, idade, client_id),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "Já existe outro cliente com esse e-mail."

    if cursor.rowcount == 0:
        return False, "Cliente não encontrado."

    return True, "Cliente atualizado com sucesso."


def delete_client(client_id: int) -> tuple[bool, str]:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM clients WHERE id = ?",
            (client_id,),
        )
        conn.commit()

    if cursor.rowcount == 0:
        return False, "Cliente não encontrado."

    return True, "Cliente excluído com sucesso."


def get_client_by_id(client_id: int):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, nome, email, celular, idade
            FROM clients
            WHERE id = ?
            """,
            (client_id,),
        ).fetchone()
    return row


def add_procedure_type(nome: str) -> tuple[bool, str]:
    nome = nome.strip()

    if not nome:
        return False, "Informe o nome do procedimento."

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO procedure_types (nome) VALUES (?)",
                (nome,),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "Esse procedimento já existe."

    return True, "Procedimento cadastrado com sucesso."


def delete_procedure_type(procedure_type_id: int) -> tuple[bool, str]:
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM procedure_types WHERE id = ?",
                (procedure_type_id,),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "Não é possível excluir esse procedimento porque ele já possui atendimentos vinculados."

    if cursor.rowcount == 0:
        return False, "Procedimento não encontrado."

    return True, "Procedimento excluído com sucesso."


def add_client_procedure(
    client_id: int,
    procedure_type_id: int,
    data_procedimento: str,
) -> tuple[bool, str]:
    if not data_procedimento:
        return False, "Informe a data do procedimento."

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO client_procedures (client_id, procedure_type_id, data_procedimento)
            VALUES (?, ?, ?)
            """,
            (client_id, procedure_type_id, data_procedimento),
        )
        conn.commit()

    return True, "Atendimento cadastrado com sucesso."


def delete_client_procedure(attendance_id: int) -> tuple[bool, str]:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM client_procedures WHERE id = ?",
            (attendance_id,),
        )
        conn.commit()

    if cursor.rowcount == 0:
        return False, "Atendimento não encontrado."

    return True, "Atendimento excluído com sucesso."


def list_clients():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, nome, email, celular, idade
            FROM clients
            ORDER BY nome
            """
        ).fetchall()
    return rows


def list_procedure_types():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, nome
            FROM procedure_types
            ORDER BY nome
            """
        ).fetchall()
    return rows


def list_attendances():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                cp.id,
                c.nome AS cliente_nome,
                c.email AS cliente_email,
                c.idade AS cliente_idade,
                pt.nome AS procedimento_nome,
                cp.data_procedimento
            FROM client_procedures cp
            INNER JOIN clients c ON c.id = cp.client_id
            INNER JOIN procedure_types pt ON pt.id = cp.procedure_type_id
            ORDER BY cp.data_procedimento DESC, c.nome
            """
        ).fetchall()
    return rows


def list_analysis_data():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.nome,
                c.email,
                c.celular,
                c.idade,
                cp.data_procedimento,
                pt.nome AS procedimento
            FROM client_procedures cp
            INNER JOIN clients c ON c.id = cp.client_id
            INNER JOIN procedure_types pt ON pt.id = cp.procedure_type_id
            ORDER BY cp.data_procedimento DESC, c.nome
            """
        ).fetchall()
    return rows