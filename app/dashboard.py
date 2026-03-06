from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import authenticate_user, create_user, update_password, user_exists
from database import (
    add_client,
    add_client_procedure,
    add_procedure_type,
    delete_client,
    delete_client_procedure,
    delete_procedure_type,
    get_client_by_id,
    init_database,
    list_analysis_data,
    list_attendances,
    list_clients,
    list_procedure_types,
    seed_demo_data,
    update_client,
)


st.set_page_config(
    page_title="Dashboard Estética",
    page_icon="📊",
    layout="wide",
)


def init_session() -> None:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""

    if "cliente_edicao_id" not in st.session_state:
        st.session_state.cliente_edicao_id = None
    if "cliente_nome" not in st.session_state:
        st.session_state.cliente_nome = ""
    if "cliente_email" not in st.session_state:
        st.session_state.cliente_email = ""
    if "cliente_celular" not in st.session_state:
        st.session_state.cliente_celular = ""
    if "cliente_idade" not in st.session_state:
        st.session_state.cliente_idade = 0
    if "limpar_cliente_form" not in st.session_state:
        st.session_state.limpar_cliente_form = False


def aplicar_limpeza_pendente_cliente() -> None:
    if st.session_state.limpar_cliente_form:
        st.session_state.cliente_edicao_id = None
        st.session_state.cliente_nome = ""
        st.session_state.cliente_email = ""
        st.session_state.cliente_celular = ""
        st.session_state.cliente_idade = 0
        st.session_state.limpar_cliente_form = False


def solicitar_limpeza_form_cliente() -> None:
    st.session_state.limpar_cliente_form = True


def carregar_cliente_para_edicao(client_id: int) -> None:
    cliente = get_client_by_id(client_id)
    if cliente is not None:
        st.session_state.cliente_edicao_id = cliente["id"]
        st.session_state.cliente_nome = cliente["nome"]
        st.session_state.cliente_email = cliente["email"]
        st.session_state.cliente_celular = cliente["celular"]
        st.session_state.cliente_idade = int(cliente["idade"])


def show_first_access_screen() -> None:
    st.title("🔐 Primeiro acesso")
    st.write("Crie o usuário inicial do sistema.")

    with st.form("first_access_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirmar senha", type="password")
        submitted = st.form_submit_button("Criar conta")

    if submitted:
        if password != confirm_password:
            st.error("A confirmação da senha não confere.")
            return

        ok, message = create_user(email, password)
        if ok:
            st.success(message)
            st.info("Conta criada. Faça login com o e-mail e a senha cadastrados.")
            st.rerun()
        else:
            st.error(message)


def show_login_screen() -> None:
    st.title("🔑 Login")

    with st.form("login_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        ok, message = authenticate_user(email, password)
        if ok:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.rerun()
        else:
            st.error(message)


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.rerun()


def show_change_password_panel() -> None:
    with st.sidebar.expander("Alterar senha"):
        with st.form("change_password_form"):
            current_password = st.text_input("Senha atual", type="password")
            new_password = st.text_input("Nova senha", type="password")
            confirm_new_password = st.text_input("Confirmar nova senha", type="password")
            submitted = st.form_submit_button("Salvar nova senha")

        if submitted:
            if new_password != confirm_new_password:
                st.sidebar.error("A confirmação da nova senha não confere.")
                return

            ok, message = update_password(
                st.session_state.user_email,
                current_password,
                new_password,
            )
            if ok:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)


def load_dataframe() -> pd.DataFrame:
    rows = list_analysis_data()

    if not rows:
        return pd.DataFrame(
            columns=[
                "nome",
                "email",
                "celular",
                "idade",
                "data_procedimento",
                "procedimento",
            ]
        )

    df = pd.DataFrame([dict(row) for row in rows])

    colunas_esperadas = [
        "nome",
        "email",
        "celular",
        "idade",
        "data_procedimento",
        "procedimento",
    ]

    for coluna in colunas_esperadas:
        if coluna not in df.columns:
            raise ValueError(f"A coluna esperada '{coluna}' não foi encontrada nos dados carregados.")

    df["idade"] = pd.to_numeric(df["idade"], errors="coerce")
    df["data_procedimento"] = pd.to_datetime(df["data_procedimento"], errors="coerce")
    df = df[df["idade"].notna()]
    df = df[df["idade"] >= 0]

    bins = [0, 25, 35, 45, 60, 200]
    labels = ["0-25", "26-35", "36-45", "46-60", "60+"]

    df["faixa_etaria"] = pd.cut(
        df["idade"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True,
    )

    return df[df["faixa_etaria"].notna()].copy()


def render_clientes() -> None:
    aplicar_limpeza_pendente_cliente()

    st.subheader("Clientes")

    if st.session_state.cliente_edicao_id is None:
        st.info("Modo atual: cadastro de novo cliente.")
    else:
        st.warning(f"Modo atual: edição do cliente ID {st.session_state.cliente_edicao_id}.")

    with st.form("form_cliente"):
        nome = st.text_input("Nome", key="cliente_nome")
        email = st.text_input("E-mail", key="cliente_email")
        celular = st.text_input("Celular", key="cliente_celular")
        idade = st.number_input(
            "Idade",
            min_value=0,
            max_value=120,
            step=1,
            key="cliente_idade",
        )

        col_btn_1, col_btn_2 = st.columns(2)
        salvar_novo = col_btn_1.form_submit_button("Salvar novo cliente")
        salvar_edicao = col_btn_2.form_submit_button("Atualizar cliente")

    if salvar_novo:
        ok, message = add_client(nome, email, celular, int(idade))
        if ok:
            st.session_state.cliente_edicao_id = None
            solicitar_limpeza_form_cliente()
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    if salvar_edicao:
        if st.session_state.cliente_edicao_id is None:
            st.error("Selecione um cliente da lista para editar.")
        else:
            ok, message = update_client(
                st.session_state.cliente_edicao_id,
                nome,
                email,
                celular,
                int(idade),
            )
            if ok:
                st.session_state.cliente_edicao_id = None
                solicitar_limpeza_form_cliente()
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    clientes = list_clients()
    st.markdown("### Clientes cadastrados")

    if not clientes:
        st.info("Nenhum cliente cadastrado.")
    else:
        for cliente in clientes:
            with st.container(border=True):
                col1, col2, col3 = st.columns([6, 1, 1])

                col1.write(
                    f"**{cliente['nome']}**  \n"
                    f"E-mail: {cliente['email']}  \n"
                    f"Celular: {cliente['celular']}  \n"
                    f"Idade: {cliente['idade']}"
                )

                if col2.button("Editar", key=f"editar_cliente_{cliente['id']}"):
                    carregar_cliente_para_edicao(cliente["id"])
                    st.rerun()

                if col3.button("Excluir", key=f"excluir_cliente_{cliente['id']}"):
                    ok, message = delete_client(cliente["id"])
                    if ok:
                        if st.session_state.cliente_edicao_id == cliente["id"]:
                            st.session_state.cliente_edicao_id = None
                            solicitar_limpeza_form_cliente()
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    if st.button("Limpar formulário de cliente"):
        st.session_state.cliente_edicao_id = None
        solicitar_limpeza_form_cliente()
        st.rerun()


def render_procedimentos() -> None:
    st.subheader("Procedimentos")

    with st.form("form_procedimento"):
        nome_procedimento = st.text_input("Nome do procedimento")
        submitted = st.form_submit_button("Salvar procedimento")

    if submitted:
        ok, message = add_procedure_type(nome_procedimento)
        if ok:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    procedimentos = list_procedure_types()
    st.markdown("### Procedimentos cadastrados")

    if not procedimentos:
        st.info("Nenhum procedimento cadastrado.")
    else:
        for item in procedimentos:
            col1, col2 = st.columns([6, 1])
            col1.write(f"- {item['nome']}")
            if col2.button("Excluir", key=f"excluir_procedimento_{item['id']}"):
                ok, message = delete_procedure_type(item["id"])
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def render_atendimentos() -> None:
    st.subheader("Atendimentos")

    clientes = list_clients()
    procedimentos = list_procedure_types()

    if not clientes:
        st.warning("Cadastre pelo menos um cliente primeiro.")
    elif not procedimentos:
        st.warning("Cadastre pelo menos um procedimento primeiro.")
    else:
        clientes_dict = {
            f'{item["nome"]} | {item["email"]} | {item["idade"]} anos': item["id"]
            for item in clientes
        }
        procedimentos_dict = {
            item["nome"]: item["id"]
            for item in procedimentos
        }

        with st.form("form_lancamento"):
            cliente_label = st.selectbox("Cliente", list(clientes_dict.keys()))
            procedimento_label = st.selectbox("Procedimento", list(procedimentos_dict.keys()))
            data_procedimento = st.date_input("Data do procedimento")
            submitted = st.form_submit_button("Salvar atendimento")

        if submitted:
            ok, message = add_client_procedure(
                client_id=clientes_dict[cliente_label],
                procedure_type_id=procedimentos_dict[procedimento_label],
                data_procedimento=str(data_procedimento),
            )
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.markdown("### Atendimentos cadastrados")
    atendimentos = list_attendances()

    if not atendimentos:
        st.info("Nenhum atendimento cadastrado.")
    else:
        for item in atendimentos:
            with st.container(border=True):
                col1, col2 = st.columns([7, 1])
                col1.write(
                    f"**Cliente:** {item['cliente_nome']}  \n"
                    f"**E-mail:** {item['cliente_email']}  \n"
                    f"**Idade:** {item['cliente_idade']}  \n"
                    f"**Procedimento:** {item['procedimento_nome']}  \n"
                    f"**Data:** {item['data_procedimento']}"
                )
                if col2.button("Excluir", key=f"excluir_atendimento_{item['id']}"):
                    ok, message = delete_client_procedure(item["id"])
                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)


def render_dashboard() -> None:
    st.title("📊 Dashboard - Análise de Procedimentos Estéticos")
    st.markdown("Cadastro, edição, exclusão, lançamentos e análise por faixa etária.")

    st.sidebar.success(f"Usuário logado: {st.session_state.user_email}")
    if st.sidebar.button("Sair"):
        logout()

    show_change_password_panel()

    aba1, aba2, aba3, aba4 = st.tabs(
        ["Clientes", "Procedimentos", "Atendimentos", "Dashboard"]
    )

    with aba1:
        render_clientes()

    with aba2:
        render_procedimentos()

    with aba3:
        render_atendimentos()

    with aba4:
        st.subheader("Análise dos dados")

        df = load_dataframe()

        if df.empty:
            st.info("Ainda não há atendimentos lançados para gerar o dashboard.")
            return

        procedimentos_disponiveis = sorted(df["procedimento"].dropna().unique().tolist())
        faixas_disponiveis = df["faixa_etaria"].dropna().astype(str).unique().tolist()

        st.sidebar.header("Filtros do dashboard")
        procedimentos_selecionados = st.sidebar.multiselect(
            "Procedimento",
            options=procedimentos_disponiveis,
            default=procedimentos_disponiveis,
        )
        faixas_selecionadas = st.sidebar.multiselect(
            "Faixa etária",
            options=faixas_disponiveis,
            default=faixas_disponiveis,
        )

        df_filtrado = df[
            df["procedimento"].isin(procedimentos_selecionados)
            & df["faixa_etaria"].astype(str).isin(faixas_selecionadas)
        ].copy()

        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado com os filtros selecionados.")
            return

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de atendimentos", len(df_filtrado))
        col2.metric("Clientes únicos", df_filtrado["email"].nunique())
        col3.metric("Procedimentos distintos", df_filtrado["procedimento"].nunique())

        st.subheader("Procedimentos mais realizados")
        proc = (
            df_filtrado["procedimento"]
            .value_counts()
            .rename_axis("procedimento")
            .reset_index(name="quantidade")
        )
        fig1 = px.bar(
            proc,
            x="procedimento",
            y="quantidade",
            text="quantidade",
            title="Quantidade por procedimento",
        )
        st.plotly_chart(fig1, width="stretch")

        st.subheader("Procedimentos por faixa etária")
        faixa = (
            df_filtrado.groupby(["faixa_etaria", "procedimento"], observed=False)
            .size()
            .reset_index(name="quantidade")
        )
        fig2 = px.bar(
            faixa,
            x="faixa_etaria",
            y="quantidade",
            color="procedimento",
            barmode="group",
            text="quantidade",
            title="Distribuição por faixa etária",
        )
        st.plotly_chart(fig2, width="stretch")

        st.subheader("Procedimentos por mês")
        df_datas_validas = df_filtrado[df_filtrado["data_procedimento"].notna()].copy()

        if not df_datas_validas.empty:
            df_datas_validas["mes_periodo"] = df_datas_validas["data_procedimento"].dt.to_period("M")
            mes = (
                df_datas_validas.groupby(["mes_periodo", "procedimento"])
                .size()
                .reset_index(name="quantidade")
                .sort_values("mes_periodo")
            )
            mes["mes"] = mes["mes_periodo"].astype(str)

            fig3 = px.line(
                mes,
                x="mes",
                y="quantidade",
                color="procedimento",
                markers=True,
                title="Evolução mensal",
            )
            st.plotly_chart(fig3, width="stretch")

        st.subheader("Base analítica")
        tabela = df_filtrado[
            ["nome", "email", "celular", "idade", "faixa_etaria", "data_procedimento", "procedimento"]
        ].copy()
        tabela["data_procedimento"] = tabela["data_procedimento"].dt.strftime("%Y-%m-%d")
        st.dataframe(tabela, width="stretch")


def main() -> None:
    init_database()
    seed_demo_data()
    init_session()

    if not user_exists():
        show_first_access_screen()
        return

    if not st.session_state.logged_in:
        show_login_screen()
        return

    render_dashboard()


if __name__ == "__main__":
    main()