# ==============================================================================
# 4. INTERFACE DO USUÁRIO (MODERN LIGHT FOOTBALL THEME)
# ==============================================================================
init_db()
st.set_page_config(page_title="Base Craque AI | Escola de Futebol", layout="wide", page_icon="⚽")

# CSS para Tema Claro Profissional
st.markdown("""
    <style>
    /* Fundo do Aplicativo e Cores Gerais */
    .stApp { 
        background-color: #F8FAF8; 
        color: #2C3E50; 
    }
    
    /* Sidebar (Menu Lateral) - Agora Branco com Borda */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        color: #1B5E20 !important; 
        border-right: 1px solid #E0E0E0; 
    }
    
    /* Estilização dos Cards de Questões */
    .q-card { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #D1D5DB; 
        margin-bottom: 20px; 
        color: #333333; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-left: 6px solid #4CAF50; 
    }
    
    /* Botões - Amarelo Ouro com Texto Escuro */
    .stButton>button { 
        background-color: #FFD700 !important; 
        color: #1B5E20 !important; 
        font-weight: 700 !important; 
        border-radius: 10px !important; 
        border: 1px solid #C5B358 !important; 
        transition: 0.3s; 
    }
    .stButton>button:hover { 
        background-color: #FDCB00 !important; 
        transform: translateY(-2px); 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
    }
    
    /* Títulos e Textos */
    h1, h2, h3 { 
        color: #1B5E20 !important; 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important; 
    }
    
    /* Inputs e Selectboxes - Fundo Branco */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input { 
        background-color: #FFFFFF !important; 
        color: #2C3E50 !important; 
        border: 1px solid #CED4DA !important; 
    }

    /* Badges e Infos */
    .stat-box { 
        background-color: #E8F5E9; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: bold; 
        border: 1px solid #C8E6C9; 
        color: #2E7D32; 
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("⚽ Base Craque AI")
st.sidebar.markdown("---")
# Ajustando as cores do rádio da sidebar para combinar com tema claro
menu = st.sidebar.radio("Menu do Atleta", ["🏠 Vestiário (Home)", "🎮 Iniciar Desafio", "🏆 Meus Troféus (Histórico)"])

if menu == "🏠 Vestiário (Home)":
    st.title("🏟️ Bem-vindo ao Vestiário, Craque!")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E0E0E0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h3 style="margin-top:0;">Transforme seu jogo com inteligência! 🧠⚽</h3>
            <p>Aqui você não treina apenas as pernas, treina a <b>mente</b>. 
            Aprenda tática, nutrição e regras para subir de nível e chegar ao profissional.</p>
            <br>
            <b>O que você encontra aqui:</b><br>
            🎯 <b>Desafios de QI de Jogo:</b> Teste sua visão de campo.<br>
            🍎 <b>Dicas de Nutrição:</b> Coma como um atleta.<br>
            📜 <b>Regras da Bola:</b> Saiba tudo para não levar cartão bobo.<br>
            🛡️ <b>Mentalidade:</b> Aprenda a lidar com a pressão.
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("💡 **Dica do Prof:** 'O talento ganha jogos, mas a inteligência ganha campeonatos!'")
    with col2:
        st.image("https://img.freepik.com/free-vector/soccer-player-concept-illustration_114360-11761.jpg", use_container_width=True)

# ... (O resto do código de lógica permanece igual)
