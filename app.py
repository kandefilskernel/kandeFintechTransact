import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(layout="wide")
@st.cache_data
def load_data():
    return pd.read_csv("Transactions_data_complet.csv")

df = load_data()

st.title("Dashboard Interactif - Analyse des Transactions")

# 2. Sidebar - Filtres dynamiques
st.sidebar.header("Filtres")

if 'TransactionStartTime' in df.columns:
    df['TransactionStartTime'] = pd.to_datetime(df['TransactionStartTime'])
    date_min = df['TransactionStartTime'].min()
    date_max = df['TransactionStartTime'].max()
    date_range = st.sidebar.date_input("Filtrer par Date", [date_min, date_max])

    # Filtrage des données par date
    if len(date_range) == 2:
        df = df[(df['TransactionStartTime'] >= pd.to_datetime(date_range[0])) &
                 (df['TransactionStartTime'] <= pd.to_datetime(date_range[1]))]

# Filtres catégoriels multiples
colonnes_categorique = df.select_dtypes(include=['object', 'category']).columns.tolist()
for col in colonnes_categorique:
    valeurs = df[col].unique().tolist()
    selection = st.sidebar.multiselect(f"{col}", valeurs, default=valeurs)
    df = df[df[col].isin(selection)]

# 3. Sélection pour Graphiques
colonnes_numerique = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

col_x = st.sidebar.selectbox("Variable X (catégorique)", colonnes_categorique)
col_y = st.sidebar.selectbox("Variable Y (numérique)", colonnes_numerique)
col_color = st.sidebar.selectbox("Variable couleur (optionnel)", [None] + colonnes_categorique)

if 'TransactionStartTime' in df.columns:
    st.subheader("Évolution temporelle")
    line_data = df.groupby('TransactionStartTime')[col_y].mean().reset_index()
    fig_line = px.line(line_data, x='TransactionStartTime', y=col_y, title=f"{col_y} moyen au fil du temps")
    st.plotly_chart(fig_line, use_container_width=True)

# Histogramme
st.subheader("Histogramme interactif")
fig_hist = px.histogram(df, x=col_y, color=col_color, nbins=30)
st.plotly_chart(fig_hist, use_container_width=True)

# Barplot (moyenne par catégorie)
st.subheader("Moyenne par catégorie")
agg_data = df.groupby(col_x)[col_y].mean().reset_index()
fig_bar = px.bar(agg_data, x=col_x, y=col_y, color=col_x, title=f"Moyenne de {col_y} par {col_x}")
st.plotly_chart(fig_bar, use_container_width=True)

# Heatmap de corrélation
st.subheader("Heatmap de Corrélation")
corr = df[colonnes_numerique].corr()
fig_corr, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig_corr)

# Pie chart
if col_x:
    st.subheader("Répartition des catégories")
    fig_pie = px.pie(df, names=col_x, title=f"Répartition de {col_x}")
    st.plotly_chart(fig_pie, use_container_width=True)

if 'CountryCode' in df.columns:
    st.subheader("Analyse des Montants par Pays")
    country_data = df.groupby('CountryCode')['Amount'].sum().reset_index()
    fig_country = px.bar(country_data, x='CountryCode', y='Amount', title="Montant total par Pays")
    st.plotly_chart(fig_country, use_container_width=True)

if 'ProviderId' in df.columns:
    st.subheader("Analyse des Transactions par Fournisseur")
    provider_data = df['ProviderId'].value_counts().reset_index()
    provider_data.columns = ['ProviderId', 'Nombre de Transactions']
    fig_provider = px.bar(provider_data, x='ProviderId', y='Nombre de Transactions', title="Nombre de Transactions par Fournisseur")
    st.plotly_chart(fig_provider, use_container_width=True)

# 7. Distribution des Catégories de Produits
if 'ProductCategory' in df.columns:
    st.subheader("Distribution des Catégories de Produits")
    product_data = df['ProductCategory'].value_counts().reset_index()
    product_data.columns = ['ProductCategory', 'Nombre de Transactions']
    fig_product = px.bar(product_data, x='ProductCategory', y='Nombre de Transactions', title="Nombre de Transactions par Catégorie de Produit")
    st.plotly_chart(fig_product, use_container_width=True)

# 8. Analyse des Fraudes
if 'FraudResult' in df.columns:
    st.subheader("Analyse des Fraudes")
    fraud_data = df['FraudResult'].value_counts().reset_index()
    fraud_data.columns = ['FraudResult', 'Nombre de Transactions']
    fig_fraud = px.pie(fraud_data, names='FraudResult', values='Nombre de Transactions', title="Répartition des Résultats de Fraude")
    st.plotly_chart(fig_fraud, use_container_width=True)

# 9. Statistiques Descriptives
st.subheader("Statistiques Descriptives")
st.write(df.describe())

# 10. Analyse Tabulaire
st.subheader("Analyse Tabulaire")
groupby_col = st.selectbox("Grouper par", colonnes_categorique)
agg_col = st.multiselect("Colonnes à agréger", colonnes_numerique, default=colonnes_numerique[:1])
if groupby_col and agg_col:
    st.dataframe(df.groupby(groupby_col)[agg_col].agg(['mean', 'sum', 'count']).round(2))

with st.expander("Aperçu des données"):
    st.dataframe(df)

# 12. Téléchargement des données filtrées
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Télécharger les données filtrées", csv, "transactions_filtrées.csv", "text/csv")
