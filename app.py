import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

@st.cache_data
def carregar_dados():
    return pd.read_csv("sales_data.csv", parse_dates=["Date_Sold"])

dados = carregar_dados()

st.title("Dashboard Interativo de Vendas 📈")

categorias = sorted(dados["Category"].unique().tolist())
produtos = sorted(dados["Product_Name"].unique().tolist())

col1, col2, col3 = st.sidebar.columns(3)
categoria_sel = col1.multiselect("Categorias", categorias, default=categorias)
produto_sel = col2.multiselect("Produtos", produtos, default=produtos)
data_sel = col3.date_input("Período", [dados.Date_Sold.min(), dados.Date_Sold.max()])

filtro = (
    dados["Category"].isin(categoria_sel) &
    dados["Product_Name"].isin(produto_sel) &
    (dados["Date_Sold"] >= pd.to_datetime(data_sel[0])) &
    (dados["Date_Sold"] <= pd.to_datetime(data_sel[1]))
)
dados = dados[filtro]

aba1, aba2, aba3, aba4 = st.tabs(["Vendas ao Longo do Tempo", "Top Produtos", "Categorias", "Matriz de Correlação"])

with aba1:
    st.subheader("Total de Vendas ao Longo do Tempo")
    mostrar_media = st.checkbox("Mostrar média móvel (7 dias)")
    mostrar_rotulos = st.checkbox("Mostrar rótulos dos pontos")
    
    df_temp = dados.groupby("Date_Sold")["Total_Sales"].sum().reset_index()
    if mostrar_media:
        df_temp["Media_Movel"] = df_temp["Total_Sales"].rolling(7).mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_temp["Date_Sold"], df_temp["Total_Sales"], marker='o', label="Total de Vendas")
    if mostrar_media:
        ax.plot(df_temp["Date_Sold"], df_temp["Media_Movel"], linestyle="--", label="Média Móvel")
    if mostrar_rotulos:
        for i in range(len(df_temp)):
            ax.text(df_temp["Date_Sold"][i], df_temp["Total_Sales"][i], f'{df_temp["Total_Sales"][i]:.0f}', fontsize=8)
    ax.set_title("Evolução das Vendas")
    ax.set_xlabel("Data")
    ax.set_ylabel("Total R$")
    ax.legend()
    st.pyplot(fig)

with aba2:
    st.subheader("Top 10 Produtos por Receita")
    vertical = st.checkbox("Orientar verticalmente os rótulos")
    top_n = st.slider("Quantidade de Produtos", 5, 20, 10)
    df_prod = dados.groupby("Product_Name")["Total_Sales"].sum().sort_values(ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(x=df_prod.index, y=df_prod.values, ax=ax)
    ax.set_xlabel("Produto")
    ax.set_ylabel("Receita Total")
    if vertical:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_title("Produtos com Maior Receita")
    st.pyplot(fig)

with aba3:
    st.subheader("Distribuição de Receita por Categoria")
    explodir = st.checkbox("Explodir setores")
    df_cat = dados.groupby("Category")["Total_Sales"].sum()
    explode = [0.1 if explodir else 0 for _ in df_cat]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(df_cat, labels=df_cat.index, autopct="%1.1f%%", explode=explode, startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

with aba4:
    st.subheader("Matriz de Correlação entre Variáveis Numéricas")
    corr = dados[["Price", "Quantity_Sold", "Total_Sales"]].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)