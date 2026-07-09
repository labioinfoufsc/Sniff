import streamlit as st
import pandas as pd
import os
import base64
from src.ingestor import QualisIngestor
from src.matchers import ACMMatcher, IEEEMatcher, ElsevierMatcher, SpringerMatcher, WileyMatcher

# --- VIEW HELPER FUNCTIONS (The "V" in MVC) ---
def local_css(file_path: str):
    """Engineering Note: Reads an external CSS file and injects it globally into the Streamlit DOM."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_image_base64(path: str) -> str:
    """Converts a local image to base64 so it can be rendered safely inside local HTML."""
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def render_navbar(template_path: str, logo_path: str):
    """Reads an external HTML file and renders it into the Streamlit view layer."""
    if os.path.exists(template_path) and os.path.exists(logo_path):
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        logo_base64 = f"data:image/png;base64,{get_image_base64(logo_path)}"
        final_html = html_content.replace("{{LOGO_PATH}}", logo_base64)
        st.markdown(final_html, unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='color: #4F8BF9;'>sniff</h1>", unsafe_allow_html=True)


# --- CONTROLLER SETUP (The "C" in MVC) ---
favicon_path = "assets/tamandua.png"
page_icon = favicon_path if os.path.exists(favicon_path) else "S"

st.set_page_config(
    page_title="sniff - Farejador de Periódicos do Acordo CAPES", 
    page_icon=page_icon, 
    layout="wide"
)

# Injetando o CSS Global (Nova Linha de Engenharia)
local_css("assets/style.css")

# Render Navbar View Component
render_navbar(template_path="assets/navbar.html", logo_path=favicon_path)
st.markdown("---")

st.header("Passo 1: Carregar Base Sucupira (.xlsx)")

# Bloco HTML informativo inserido logo abaixo do título
st.markdown("""
<div style="background-color: #FFFFFF; border-left: 4px solid #4F8BF9; padding: 15px; margin-top: 10px; margin-bottom: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin: 0 0 10px 0; font-weight: 600; color: #1E1E1E; font-family: sans-serif; font-size: 16px;">Como buscar e obter esse arquivo:</p>
    <ol style="margin: 0; padding-left: 20px; color: #555555; font-family: sans-serif; font-size: 14px; line-height: 1.6;">
        <li style="margin-bottom: 6px;">Acesse a consulta pública na <a href="https://sucupira-legado.capes.gov.br/sucupira/public/consultas/coleta/veiculoPublicacaoQualis/listaConsultaGeralPeriodicos.jsf" target="_blank" style="color: #4F8BF9; text-decoration: none; font-weight: bold;">Plataforma Sucupira</a>.</li>
        <li style="margin-bottom: 6px;">Selecione o <strong>Evento de Classificação</strong> mais recente (ou o desejado).</li>
        <li style="margin-bottom: 6px;">Filtre os resultados selecionando a sua <strong>Área de Avaliação</strong> específica.</li>
        <li style="margin-bottom: 0;">Clique no botão <strong>Pesquisar</strong> e, em seguida, clique no ícone para baixar a planilha no formato <strong>Excel (.xlsx)</strong> gerada pelo sistema.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

uploaded_qualis = st.file_uploader("Arraste ou selecione o arquivo Excel da Sucupira", type=["xlsx"])

if uploaded_qualis:
    temp_xlsx_path = "data/raw_uploaded_qualis.xlsx"
    os.makedirs("data", exist_ok=True)
    with open(temp_xlsx_path, "wb") as f:
        f.write(uploaded_qualis.getbuffer())
    
    try:
        ingestor = QualisIngestor()
        processed_csv_path = ingestor.convert_xlsx_to_csv(temp_xlsx_path)
        st.success("Base do Qualis carregada e padronizada com sucesso.")
        st.session_state['sucupira_df'] = pd.read_csv(processed_csv_path, dtype=str)
    except Exception as e:
        st.error(f"Erro ao processar arquivo Excel: {e}")

if 'sucupira_df' in st.session_state:
    st.markdown("---")
    st.header("Passo 2: Selecionar Editora e Fornecer Catálogo")
    
    publisher_options = {
        "ACM": {"matcher": ACMMatcher, "file": "data/raw/ACM.csv"},
        "Elsevier": {"matcher": ElsevierMatcher, "file": "data/raw/Elsevier.csv"},
        "IEEE": {"matcher": IEEEMatcher, "file": "data/raw/IEEE.csv"},
        "Springer Nature": {"matcher": SpringerMatcher, "file": "data/raw/Springer.csv"},
        "Wiley": {"matcher": WileyMatcher, "file": "data/raw/Wiley.csv"}
    }
    
    selected_publisher = st.selectbox("Escolha a editora para realizar o cruzamento:", list(publisher_options.keys()))
    
    if selected_publisher:
        config = publisher_options[selected_publisher]
        
        if os.path.exists(config["file"]):
            st.info(f"Catálogo de referência de '{selected_publisher}' localizado.")
            
            if st.button(f"Processar cruzamentos com {selected_publisher}"):
                try:
                    matcher_instance = config["matcher"](sucupira_df=st.session_state['sucupira_df'])
                    result_df = matcher_instance.match(config["file"])
                    
                    if not result_df.empty:
                        st.success(f"Processamento concluído. Encontradas {len(result_df)} correspondências.")
                        st.dataframe(result_df, use_container_width=True)
                        
                        csv_download = result_df.to_csv(index=False, encoding="utf-8-sig")
                        st.download_button(
                            label="Baixar Planilha de Cruzamento (CSV)",
                            data=csv_download,
                            file_name=f"sniff_resultado_{selected_publisher.lower().replace(' ', '_')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("Nenhum cruzamento encontrado para esta Área de Avaliação.")
                except Exception as e:
                    st.error(f"Erro operacional durante o cruzamento: {e}")
        else:
            st.error(f"Arquivo ausente: Certifique-se de que o arquivo '{config['file']}' está na pasta do projeto.")