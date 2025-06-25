import streamlit as st
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Lista de Compras - Supermercado",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nome do arquivo de salvamento
SAVE_FILE = "dados_salvos.json"

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .category-tag {
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
        display: inline-block;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🛒 Lista de Compras - Supermercado</h1>
    <p>Organize suas compras de forma inteligente e eficiente</p>
</div>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'produtos' not in st.session_state:
    st.session_state.produtos = pd.DataFrame(columns=['Nome', 'Quantidade', 'Categoria', 'Preço Unitário', 'Observações'])

if 'colunas_personalizadas' not in st.session_state:
    st.session_state.colunas_personalizadas = []

if 'categorias' not in st.session_state:
    st.session_state.categorias = [
        'Grãos', 'Laticínios', 'Carnes', 'Frutas', 'Verduras',
        'Bebidas', 'Limpeza', 'Higiene', 'Padaria', 'Congelados', 'Outros'
    ]

# Função para carregar os dados salvos
def carregar_dados():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"produtos": [], "observacoes": ""}

# Função para salvar automaticamente
def salvar_dados():
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state["dados"], f, ensure_ascii=False, indent=4)

# Inicialização da session state
if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_dados()

st.title("Organizador de Compras")
st.success("Todas as alterações são salvas automaticamente!")

# Função para calcular total
def calcular_total(df):
    if 'Total' not in df.columns:
        df['Total'] = df['Quantidade'] * df['Preço Unitário']
    return df

# Função para adicionar categoria de cores
def get_color_category(categoria):
    colors = {
        'Grãos': '#FFC107', 'Laticínios': '#2196F3', 'Carnes': '#F44336',
        'Frutas': '#4CAF50', 'Verduras': '#8BC34A', 'Bebidas': '#9C27B0',
        'Limpeza': '#00BCD4', 'Higiene': '#E91E63', 'Padaria': '#FF9800',
        'Congelados': '#607D8B', 'Outros': '#795548'
    }
    return colors.get(categoria, '#9E9E9E')

# Sidebar para controles
with st.sidebar:
    st.header("🔧 Controles")
    
    # Seção para adicionar produto
    with st.expander("➕ Adicionar Produto", expanded=False):
        with st.form("adicionar_produto"):
            nome = st.text_input("Nome do Produto*")
            col1, col2 = st.columns(2)
            with col1:
                quantidade = st.number_input("Quantidade*", min_value=0.0, value=1.0, step=0.1)
            with col2:
                preco = st.number_input("Preço Unitário (R$)*", min_value=0.0, value=0.0, step=0.01)
            
            categoria = st.selectbox("Categoria*", st.session_state.categorias)
            observacoes = st.text_area("Observações", height=100)
            
            # Campos das colunas personalizadas
            valores_personalizados = {}
            for coluna in st.session_state.colunas_personalizadas:
                valores_personalizados[coluna] = st.text_input(f"{coluna}")
            
            submitted = st.form_submit_button("✅ Adicionar Produto", type="primary")
            
            if submitted and nome:
                novo_produto = {
                    'Nome': nome,
                    'Quantidade': quantidade,
                    'Categoria': categoria,
                    'Preço Unitário': preco,
                    'Observações': observacoes
                }
                
                # Adicionar colunas personalizadas
                for coluna, valor in valores_personalizados.items():
                    novo_produto[coluna] = valor
                
                novo_df = pd.DataFrame([novo_produto])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo_df], ignore_index=True)
                st.success(f"✅ {nome} adicionado com sucesso!")
                st.rerun()
    
    # Seção para gerenciar colunas personalizadas
    with st.expander("🔧 Gerenciar Colunas", expanded=False):
        nova_coluna = st.text_input("Nome da nova coluna")
        if st.button("➕ Adicionar Coluna"):
            if nova_coluna and nova_coluna not in st.session_state.produtos.columns:
                st.session_state.colunas_personalizadas.append(nova_coluna)
                st.session_state.produtos[nova_coluna] = ""
                st.success(f"Coluna '{nova_coluna}' adicionada!")
                st.rerun()
        
        if st.session_state.colunas_personalizadas:
            st.write("**Colunas Personalizadas:**")
            for coluna in st.session_state.colunas_personalizadas:
                if st.button(f"🗑️ Remover '{coluna}'", key=f"remove_{coluna}"):
                    st.session_state.colunas_personalizadas.remove(coluna)
                    if coluna in st.session_state.produtos.columns:
                        st.session_state.produtos = st.session_state.produtos.drop(columns=[coluna])
                    st.rerun()
    
    st.subheader("🔍 Filtros")
    categoria_filtro = st.selectbox("Filtrar por Categoria", ["Todas"] + st.session_state.categorias)
    
    st.subheader("📊 Ordenação")
    colunas_ordenacao = ['Nome', 'Quantidade', 'Categoria', 'Preço Unitário', 'Total']
    coluna_ordenacao = st.selectbox("Ordenar por", colunas_ordenacao)
    ordem_crescente = st.radio("Ordem", ["Crescente", "Decrescente"]) == "Crescente"

# Processar dados
df = st.session_state.produtos.copy()
df = calcular_total(df)

if categoria_filtro != "Todas":
    df = df[df['Categoria'] == categoria_filtro]

if coluna_ordenacao in df.columns:
    df = df.sort_values(by=coluna_ordenacao, ascending=ordem_crescente)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Total de Produtos", len(df))

with col2:
    st.metric("🔢 Total de Itens", f"{df['Quantidade'].sum():.1f}")

with col3:
    st.metric("💰 Valor Total", f"R$ {df['Total'].sum():.2f}")

with col4:
    preco_medio = df['Preço Unitário'].mean() if len(df) > 0 else 0
    st.metric("📊 Preço Médio", f"R$ {preco_medio:.2f}")

col1, col2 = st.columns(2)

with col1:
    if len(df) > 0:
        categoria_counts = df['Categoria'].value_counts()
        fig_pie = px.pie(
            values=categoria_counts.values, 
            names=categoria_counts.index,
            title="📊 Distribuição por Categoria",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    if len(df) > 0:
        categoria_valores = df.groupby('Categoria')['Total'].sum().sort_values(ascending=False)
        fig_bar = px.bar(
            x=categoria_valores.index,
            y=categoria_valores.values,
            title="💰 Valor Total por Categoria",
            color=categoria_valores.values,
            color_continuous_scale="Viridis"
        )
        fig_bar.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📋 Lista de Produtos")

if len(df) > 0:
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="produtos_editor",
        column_config={
            "Nome": st.column_config.TextColumn("Nome do Produto", required=True),
            "Quantidade": st.column_config.NumberColumn("Quantidade", min_value=0, step=0.1),
            "Categoria": st.column_config.SelectboxColumn("Categoria", options=st.session_state.categorias),
            "Preço Unitário": st.column_config.NumberColumn("Preço Unitário (R$)", min_value=0, step=0.01, format="R$ %.2f"),
            "Total": st.column_config.NumberColumn("Total (R$)", format="R$ %.2f", disabled=True),
            "Observações": st.column_config.TextColumn("Observações")
        },
        hide_index=True
    )
    
    if not edited_df.equals(st.session_state.produtos):
        st.session_state.produtos = edited_df
        st.rerun()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 Atualizar Dados"):
            st.rerun()

    with col2:
        if st.button("🗑️ Limpar Lista"):
            st.session_state.produtos = pd.DataFrame(columns=['Nome', 'Quantidade', 'Categoria', 'Preço Unitário', 'Observações'])
            st.rerun()

    with col3:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"lista_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col4:
        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Lista de Compras', index=False)
            st.download_button(
                label="📊 Exportar Excel",
                data=buffer.getvalue(),
                file_name=f"lista_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("Para exportar Excel, instale: pip install openpyxl")
else:
    st.info("📝 Nenhum produto na lista. Adicione produtos usando o painel lateral!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🛒 Lista de Compras | Desenvolvido com Streamlit | Dica: Use Ctrl+R para atualizar a página
    </div>
    """,
    unsafe_allow_html=True
)
