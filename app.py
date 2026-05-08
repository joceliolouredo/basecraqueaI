import base64 # Adicione isso no topo do seu arquivo, junto com os outros imports

# ==============================================================================
# FUNÇÃO PARA CARREGAR O VÍDEO DO REPOSITÓRIO (SISTEMA ANTI-ERRO)
# ==============================================================================
def get_video_base64(video_path):
    try:
        with open(video_path, "rb") as video_file:
            encoded_string = base64.b64encode(video_file.read()).decode('utf-8')
        return f"data:video/mp4;base64,{encoded_string}"
    except FileNotFoundError:
        # Caso o arquivo arena.mp4 não seja encontrado, ele usa um link de backup
        return "https://videos.pexels.com/video-files/16651367/pexels-video-16651367.mp4"

# Aqui chamamos a função para pegar o seu vídeo arena.mp4
VIDEO_B64 = get_video_base64("arena.mp4")

# ==============================================================================
# 4. INTERFACE GAMIFICADA - FUNDO de VÍDEO LOCAL (ARENA MODE)
# ==============================================================================

st.markdown(f"""
    <style>
    /* 1. O VÍDEO DE FUNDO - Agora carregado do seu próprio repositório! */
    .video-background {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -1; 
        object-fit: cover;
    }}

    /* 2. TRANSPARÊNCIA TOTAL DO APP */
    .stApp {{ 
        background: transparent !important; 
        background-color: transparent !important;
    }}
    
    /* 3. EFEITO GLASSMORPHISM (Vidro Escuro Gamer) 
       Isso cria a camada onde o conteúdo fica para não sumir no vídeo */
    .main .block-container {{
        background-color: rgba(0, 0, 0, 0.75) !important; 
        backdrop-filter: blur(12px); 
        border-radius: 30px;
        padding: 30px;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white !important;
    }}

    /* 4. SIDEBAR (Menu Lateral Profissional) */
    [data-testid="stSidebar"] {{ 
        background-color: rgba(0, 0, 0, 0.85) !important; 
        border-right: 6px solid #FFD700; 
    }}
    
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stText {{
        color: #FFFFFF !important;
    }}

    /* 5. CARTÕES DE QUESTÕES (Brancos para leitura máxima) */
    .q-card {{ 
        background-color: rgba(255, 255, 255, 0.98); 
        padding: 25px; 
        border-radius: 25px; 
        border: 4px solid #FFD700; 
        margin-bottom: 25px; 
        color: #1B5E20; 
        box-shadow: 8px 8px 0px #C8E6C9; 
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }}

    /* 6. BOTÕES NEON (Estilo FIFA/E-Sports) */
    .stButton>button {{ 
        background-color: #FFD700 !important; 
        color: #000 !important; 
        font-weight: 900 !important; 
        font-size: 18px !important;
        border-radius: 50px !important; 
        border: 3px solid #FFFFFF !important; 
        padding: 10px 20px !important;
        transition: 0.3s; 
        text-transform: uppercase;
        box-shadow: 0 0 15px #FFD700;
    }}
    
    .stButton>button:hover {{ 
        background-color: #FFFFFF !important; 
        transform: scale(1.1); 
        box-shadow: 0 0 25px #FFFFFF;
    }}

    h1, h2, h3 {{ 
        color: #FFD700 !important; 
        font-family: 'Comic Sans MS', cursive, sans-serif !important; 
        text-shadow: 2px 2px #000;
    }}

    /* Inputs visíveis no fundo escuro */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{ 
        border-radius: 20px !important; 
        border: 2px solid #FFD700 !important;
        background-color: white !important;
        color: black !important;
    }}
    </style>
    
    <video autoplay muted loop playsinline class="video-background">
        <source src="{VIDEO_B64}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)
