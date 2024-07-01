# modelo treinado
import numpy as np
from spacy import load
import streamlit as st
import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
from dash import Output
from dash import Input


def mudarCol(new_column_name=None):
    columns = []
    if 'column_input_counter' not in st.session_state:
        st.session_state.column_input_counter = 0

    while True:
        new_column_name = st.text_input(
            "Digite novos nomes para as colunas (separados por vírgula): ",
            key=f'column_input_{st.session_state.column_input_counter}'
        )
        st.write("Digite 'sair' para parar")
        if new_column_name.lower() == 'sair':
            break
        new_column_names = [name.strip() for name in new_column_name.split(",")]
        columns.extend(new_column_names)
        st.session_state.column_input_counter += 1

    if columns:
        df = pd.DataFrame(columns=columns)
        st.write("Colunas criadas com sucesso!")
        st.write(df)
        return df

def mudarDados(df):
    while True:
        coluna_escolhida = input("Qual coluna você deseja mudar os dados (ou 'sair' para parar): ")

        if coluna_escolhida.lower() == 'sair':

            return df  # Retorna o DataFrame df quando o usuário escolhe sair

        if coluna_escolhida not in df.columns:
            print(f"Erro: Coluna '{coluna_escolhida}' não existe no DataFrame.")
            continue

        while True:
            indice_escolhido = input(f"Digite o índice da linha que você deseja mudar (ou 'sair' para parar): ")

            if indice_escolhido.lower() == 'sair':

                return df  # Retorna o DataFrame df quando o usuário escolhe sair

            try:
                indice_escolhido = int(indice_escolhido)
                novo_valor = input(
                    f"Digite o novo valor para a coluna '{coluna_escolhida}' na linha {indice_escolhido}: ")
                df.loc[indice_escolhido, coluna_escolhida] = novo_valor
                print(f"Valor adicionado com sucesso!")
                print(df)  # Imprime o DataFrame atualizado
            except (ValueError, KeyError):
                print(f"Erro: Índice {indice_escolhido} não existe no DataFrame.")

    return df  # Retorna o DataFrame df no final da função

def criarPlanilha(df):
    nome_planilha = input("Digite o nome da planilha: ")
    df.to_excel(f"{nome_planilha}.xlsx", index=False)
    print(f"Planilha '{nome_planilha}.xlsx' criada com sucesso!")


def criarDashBoard():

    # Crie uma área de transferência para carregar as planilhas
    st.header("Carregue as planilhas")
    uploaded_files = st.file_uploader("Selecione as planilhas", type=["csv"], accept_multiple_files=True)

    # Crie um dicionário para armazenar as planilhas carregadas
    planilhas = {}

    # Carregue as planilhas carregadas
    if uploaded_files:
        for file in uploaded_files:
            df = pd.read_csv(file.read(), sep=";", decimal=",")
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            planilhas[file.name] = df

    # Adicione uma seleção de planilha no sidebar
    st.sidebar.header("Selecione a planilha")
    selected_planilha = st.sidebar.selectbox("Planilha", list(planilhas.keys()))

    # Carregue o DataFrame selecionado
    df = planilhas[selected_planilha]

    # Adicione as colunas necessárias
    df["Month"] = df["Date"].apply(lambda x: str(x.year) + "-" + str(x.month))

    # Adicione a seleção de mês
    month = st.sidebar.selectbox("Mês", df["Month"].unique())

    # Filtrar os dados pelo mês selecionado
    df_filtered = df[df["Month"] == month]

    # Crie as figuras
    col1, col2 = st.columns(2)
    col3, col4, col5 = st.columns(3)

    fig_date = px.bar(df_filtered, x="Date", y="Total", color="City", title="Faturamento por dia")
    col1.plotly_chart(fig_date, use_container_width=True)

    fig_prod = px.bar(df_filtered, x="Date", y="Product line",
                      color="City", title="Faturamento por tipo de produto",
                      orientation="h")
    col2.plotly_chart(fig_prod, use_container_width=True)

    city_total = df_filtered.groupby("City")[["Total"]].sum().reset_index()
    fig_city = px.bar(city_total, x="City", y="Total",
                      title="Faturamento por filial")
    col3.plotly_chart(fig_city, use_container_width=True)

    fig_kind = px.pie(df_filtered, values="Total", names="Payment",
                      title="Faturamento por tipo de pagamento")
    col4.plotly_chart(fig_kind, use_container_width=True)

    city_total = df_filtered.groupby("City")[["Rating"]].mean().reset_index()
    fig_rating = px.bar(df_filtered, y="Rating", x="City",
                        title="Avaliação")
    col5.plotly_chart(fig_rating, use_container_width=True)

criarDashBoard()



