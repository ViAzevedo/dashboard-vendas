
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def carregar_dados():
    return pd.read_csv("sales_data.csv", parse_dates=["Date_Sold"])

dados = carregar_dados()

categorias = dados["Category"].unique().tolist()
categoria_selecionada = st.sidebar.selectbox("Selecione uma Categoria", ["Todas"] + categorias)

if categoria_selecionada != "Todas":
    dados = dados[dados["Category"] == categoria_selecionada]

st.title("Dashboard de Vendas 📊")

vendas_diarias = dados.groupby("Date_Sold")["Total_Sales"].sum().reset_index()

st.subheader("Vendas ao Longo do Tempo")
fig1, ax1 = plt.subplots()
ax1.plot(vendas_diarias["Date_Sold"], vendas_diarias["Total_Sales"], marker='o')
ax1.set_xlabel("Data")
ax1.set_ylabel("Total de Vendas")
ax1.set_title("Total de Vendas por Dia")
st.pyplot(fig1)

produtos_top = dados.groupby("Product_Name")["Total_Sales"].sum().sort_values(ascending=False).head(10)

st.subheader("Top 10 Produtos por Receita")
fig2, ax2 = plt.subplots()
produtos_top.plot(kind='bar', ax=ax2)
ax2.set_ylabel("Receita Total")
ax2.set_xlabel("Produto")
ax2.set_title("Produtos com Maior Receita")
st.pyplot(fig2)

st.subheader("Participação das Categorias na Receita")
receita_categoria = dados.groupby("Category")["Total_Sales"].sum()
fig3, ax3 = plt.subplots()
ax3.pie(receita_categoria, labels=receita_categoria.index, autopct="%1.1f%%", startangle=90)
ax3.axis("equal")
st.pyplot(fig3)
