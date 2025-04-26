import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(layout="wide")

@st.cache_data
def carregar_dados():
    return pd.read_csv("sales_data.csv", parse_dates=["Date_Sold"])

dados = carregar_dados()

st.title("Dashboard Interativo de Vendas 📈")

categorias = sorted(dados["Category"].unique().tolist())
data_min = dados["Date_Sold"].min().date()
data_max = dados["Date_Sold"].max().date()

periodo = st.sidebar.slider("Período de Venda", min_value=data_min, max_value=data_max,
                            value=(data_min, data_max), format="%d/%m/%Y")
categoria_sel = st.sidebar.multiselect("Categorias", categorias, default=categorias)

filtro = (
    dados["Category"].isin(categoria_sel) &
    (dados["Date_Sold"] >= pd.to_datetime(periodo[0])) &
    (dados["Date_Sold"] <= pd.to_datetime(periodo[1]))
)
dados = dados[filtro]

aba1, aba2, aba3, aba4 = st.tabs(["Vendas ao Longo do Tempo", "Top Produtos", "Categorias", "Matriz de Correlação"])

with aba1:
    st.subheader("Total de Vendas ao Longo do Tempo")
    col1, col2, col3 = st.columns(3)
    mostrar_media = col1.checkbox("Média móvel (7 dias)", value=True)
    mostrar_rotulos = col2.checkbox("Rótulos nos pontos")
    mostrar_grade = col3.checkbox("Exibir grade no fundo", value=True)

    df_temp = dados.groupby("Date_Sold")["Total_Sales"].sum().reset_index()
    if mostrar_media:
        df_temp["Media_Movel"] = df_temp["Total_Sales"].rolling(7).mean()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df_temp["Date_Sold"], df_temp["Total_Sales"], marker='o', label="Total de Vendas")
    if mostrar_media:
        ax.plot(df_temp["Date_Sold"], df_temp["Media_Movel"], linestyle="--", label="Média Móvel")
    if mostrar_rotulos:
        for i in range(len(df_temp)):
            valor = f"R$ {df_temp['Total_Sales'][i]:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
            ax.text(df_temp["Date_Sold"][i], df_temp["Total_Sales"][i], valor, fontsize=8)
    ax.set_title("Evolução das Vendas")
    ax.set_xlabel("Data")
    ax.set_ylabel("Total R$")
    if mostrar_grade:
        ax.grid(True)
    ax.legend()
    st.pyplot(fig)

with aba2:
    st.subheader("Top Produtos por Receita")
    col1, col2, col3 = st.columns(3)
    top_n = col1.slider("Quantidade de Produtos", 5, 20, 10)
    vertical = col2.checkbox("Rótulos verticais", value=True)
    mostrar_valores = col3.checkbox("Mostrar valores sobre as barras", value=True)

    df_prod = dados.groupby("Product_Name")["Total_Sales"].sum().sort_values(ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(14, 5))
    barras = sns.barplot(x=df_prod.index, y=df_prod.values, ax=ax)
    ax.set_xlabel("Produto")
    ax.set_ylabel("Receita Total")
    if vertical:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    if mostrar_valores:
        for i, valor in enumerate(df_prod.values):
            label = f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
            ax.text(i, valor, label, ha='center', va='bottom', fontsize=8)
    ax.set_title("Produtos com Maior Receita")
    st.pyplot(fig)

with aba3:
    st.subheader("Distribuição de Receita por Categoria")
    col1, col2 = st.columns(2)
    explodir = col1.checkbox("Explodir setores")
    mostrar_legenda = col2.checkbox("Exibir legenda", value=True)

    df_cat = dados.groupby("Category")["Total_Sales"].sum()
    explode = [0.1 if explodir else 0 for _ in df_cat]
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(df_cat, labels=df_cat.index if mostrar_legenda else None,
                                      autopct=lambda p: f"R$ {(p/100)*df_cat.sum():,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
                                      explode=explode, startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

with aba4:
    st.subheader("Matriz de Correlação entre Variáveis Numéricas")
    col1, col2 = st.columns(2)
    mapa_anotado = col1.checkbox("Exibir valores numéricos", value=True)
    cmap_escolhido = col2.selectbox("Escolher paleta de cores", ["coolwarm", "viridis", "plasma", "magma", "Blues"])

    corr = dados[["Price", "Quantity_Sold", "Total_Sales"]].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=mapa_anotado, cmap=cmap_escolhido, ax=ax)
    st.pyplot(fig)
