import streamlit as st
from groq import Groq
import json
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import base64

# ==============================================================================
# 1. CONFIGURAÇÃO DE SEGURANÇA E IA (GROQ)
# ==============================================================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Ops! O Professor esqueceu a chave da API. Configure nos Secrets!")

# ==============================================================================
# 2. SISTEMA de BANCO de DADOS (Base Craque DB)
# ==============================================================================
DB_NAME = 'base_craque_kids.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS desafios (id INTEGER PRIMARY KEY, categoria TEXT, posicao TEXT, tema TEXT, data TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS questoes 
                 (id INTEGER PRIMARY KEY, desafio_id INTEGER, area TEXT, pergunta TEXT, 
                 opcoes TEXT, correta TEXT, justificativa TEXT)''')
    conn.commit()
    conn.close()

def save_desafio(categoria, posicao, tema):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute('INSERT INTO desafios (categoria, posicao, tema, data) VALUES (?, ?, ?, ?)', (categoria, posicao, tema, data_atual))
    id_desafio = c.lastrowid
    conn.commit()
    conn.close()
    return id_desafio

def save_questoes(desafio_id, questoes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for q in questoes:
        c.execute('INSERT INTO questoes (desafio_id, area, pergunta, opcoes, correta, justificativa) VALUES (?, ?, ?, ?, ?, ?)',
                  (desafio_id, q.get('area', 'Geral'), q['pergunta'], json.dumps(q['opcoes']), q['correta'], q['justificativa']))
    conn.commit()
    conn.close()

def get_desafios():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM desafios ORDER BY id DESC", conn)
    conn.close()
    return df

def get_questoes(desafio_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM questoes WHERE desafio_id = ?', (desafio_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "area": r[2], "pergunta": r[3], "opcoes": json.loads(r[4]), "correta": r[5], "justificativa": r[6]} for r in rows]

# ==============================================================================
# 3. MOTOR DE GERAÇÃO DE DESAFIOS (IA GROQ)
# ==============================================================================
def ai_generate_football_quiz(categoria, posicao, tema, qtd):
    prompt = f"""
    Você é o 'Professor Craque', um treinador super legal e animado de categorias de base.
    Crie um "Desafio de QI de Jogo" para garotos da categoria {categoria}.
    POSIÇÃO: {posicao} | TEMA: {tema} | QUANTIDADE: {qtd} questões.
    
    Linguagem: Use gírias leves de futebol ("Bora pro jogo!", "Na gaveta!", "Visão de jogo!"), 
    seja muito motivador e use emojis. 
    Crie cenários onde o garoto é o protagonista da jogada.
    
    Retorne EXCLUSIVAMENTE um JSON:
    {{
      "questoes": [
        {{
          "area": "Tática/Nutrição/Regra/Mental",
          "pergunta": "Cenário divertido e pergunta",
          "opcoes": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
          "correta": "A",
          "justificativa": "Explicação curta, animada e educativa."
        }}
      ]
    }}
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile", 
        response_format={"type": "json_object"} 
    )
    res = json.loads(chat_completion.choices[0].message.content)
    return res.get("questoes", [])

# ==============================================================================
# 4. SISTEMA VISUAL "CYBER ARENA" (Dark Glass + Neon)
# ==============================================================================

def get_video_base64(video_path):
    try:
        with open(video_path, "rb") as video_file:
            encoded_string = base64.b64encode(video_file.read()).decode('utf-8')
        return f"data:video/mp4;base64,{encoded_string}"
    except Exception:
        return "https://videos.pexels.com/video-files/16651367/pexels-video-16651367.mp4"

VIDEO_B64 = get_video_base64("arena.mp4")

style_css = """
    <style>
    .video-background {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -1; 
        object-fit: cover;
    }

    .stApp { 
        background: transparent !important; 
        background-color: transparent !important;
    }
    
    /* CAIXAS: Vidro Fosco Dark (Glassmorphism) */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.7) !important; 
        backdrop-filter: blur(20px); 
        border-radius: 30px;
        padding: 35px;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #FFFFFF !important;
    }

    /* MENU: Azul Escuro Profundo */
    [data-testid="stSidebar"] { 
        background-color: #001A33 !important; 
        border-right: 6px solid #FFD700; 
    }
    
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stText {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* CARTÕES: Vidro Dark com borda branca transparente */
    .q-card { 
        background-color: rgba(255, 255, 255, 0.1); 
        padding: 25px; 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.3); 
        margin-bottom: 25px; 
        color: #FFFFFF; 
        box-shadow: 0 8px 15px rgba(0,0,0,0.3); 
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }

    /* BOTÕES: Azul Neon com Glow */
    .stButton>button { 
        background-color: #00D1FF !important; 
        color: #000000 !important; 
        font-weight: 900 !important; 
        font-size: 18px !important;
        border-radius: 50px !important; 
        border: 2px solid #FFFFFF !important; 
        padding: 10px 30px !important;
        transition: 0.3s; 
        text-transform: uppercase;
        box-shadow: 0 0 15px #00D1FF;
    }
    
    .stButton>button:hover { 
        background-color: #FFFFFF !important; 
        color: #00D1FF !important; 
        transform: scale(1.05); 
        box-shadow: 0 0 25px #FFFFFF;
    }

    /* TÍTULOS: Branco Puro */
    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-family: 'Comic Sans MS', cursive, sans-serif !important; 
        font-weight: 900 !important;
    }

    /* Inputs: Dark com bordas branco transparente */
    .stTextInput>div>div>input, .stSelectbox>div>div>div { 
        border-radius: 15px !important; 
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    </style>
"""

video_html = f"""
    <video autoplay muted loop playsinline class="video-background">
        <source src="{VIDEO_B64}" type="video/mp4">
    </video>
"""

# ==============================================================================
# 5. LÓGICA DO APP
# ==============================================================================

init_db()
st.set_page_config(page_title="Base Craque AI ⚽", layout="wide", page_icon="⚽")
st.markdown(style_css + video_html, unsafe_allow_html=True)

st.sidebar.title("⚽ Base Craque AI")
st.sidebar.markdown("### MENU DO JOGO")
menu = st.sidebar.radio("Escolha sua fase:", ["🏠 Vestiário", "🎮 Jogar Desafio", "🏆 Sala de Troféus"])

if menu == "🏠 Vestiário":
    st.markdown("<h1 style='text-align: center; font-size: 3.2em; color: #FFFFFF;'>🏟️ Bem-vindo ao Vestiário, Craque!</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div style="background-color: rgba(255,255,255,0.1); padding: 35px; border-radius: 30px; border: 2px solid rgba(255,255,255,0.3); color: #FFFFFF; box-shadow: 0 10px 20px rgba(0,0,0,0.4);">
            <h2 style="margin-top:0; color:#FFD700; border-bottom: 3px solid #FFD700; display: inline-block;">Bora subir de nível? 🚀⚽</h2>
            <p style="font-size: 1.4em; line-height: 1.6; color: #FFFFFF;">Aqui você treina a <b style="color:#FFD700; font-size: 1.5em;">MENTE</b> para se tornar o melhor do campo! 
            Aprenda as manhas da tática, as dicas de saúde e as regras para não levar cartão!</p>
            <br>
            <div style="font-size: 1.2em; background-color: rgba(0,0,0,0.5); padding: 20px; border-radius: 20px; border: 1px solid #FFD700;">
                🎯 <b style="color:#FFD700;">QI DE JOGO:</b> Teste sua visão de craque.<br>
                🍎 <b style="color:#FFD700;">COMIDA de CAMPEÃO:</b> Nutrição para ter energia.<br>
                📜 <b style="color:#FFD700;">REGRA DA BOLA:</b> Para dominar o juiz!<br>
                🛡️ <b style="color:#FFD700;">MENTALIDADE:</b> Foco total no gol!
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # SUCESSO NEON GREEN
        st.markdown(f"""
            <div style="background-color: rgba(57, 255, 20, 0.2); border-left: 8px solid #39FF14; padding: 15px; border-radius: 10px; color: #39FF14; font-weight: bold; box-shadow: 0 0 10px #39FF14;">
                💡 Dica do Prof: 'Quem estuda o jogo, joga com a bola no pé!' ⚽
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        try:
            st.image("jogador.jpg.png", use_container_width=True)
        except:
            st.write("🚀 *Prepare-se para o jogo!*")

elif menu == "🎮 Jogar Desafio":
    st.title("🎮 Desafio de QI de Jogo")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Qual sua categoria? 👦", ["Sub-11", "Sub-13", "Sub-15", "Sub-17", "Várzea Adulto"])
            posicao = st.selectbox("Onde você joga? 🛡️", ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"])
        with col2:
            tema = st.selectbox("O que quer aprender hoje? 📚", ["Tática e Posicionamento", "Regras do Futebol", "Nutrição e Saúde", "Mentalidade e Foco"])
            qtd_total = st.slider("Quantas perguntas? ⚡", 5, 20, 10)
    
    if st.button("🚀 DAR O START NO JOGO!"):
        with st.spinner("🏃 Professor preparando o campo..."):
            try:
                questoes = ai_generate_football_quiz(categoria, posicao, tema, qtd_total)
                if questoes and len(questoes) > 0:
                    id_desafio = save_desafio(categoria, posicao, tema)
                    save_questoes(id_desafio, questoes)
                    st.session_state.desafio_atual_id = id_desafio
                    st.session_state.respostas_usuario = {}
                    st.session_state.desafio_concluido = False
                    st.rerun()
                else:
                    st.error("❌ O Professor não conseguiu preparar as questões agora. Tente novamente!")
            except Exception as e:
                st.error(f"Erro no treino: {e}")

    if 'desafio_atual_id' in st.session_state:
        des_id = st.session_state.desafio_atual_id
        questoes = get_questoes(des_id)
        
        if not st.session_state.get('desafio_concluido', False):
            st.markdown("### 📝 Mostre que você tem visão de jogo!")
            with st.form("quiz_form"):
                for i, q in enumerate(questoes):
                    st.markdown(f"""<div class="q-card">
                        <small style="color: #00D1FF;"><b>🌟 ÁREA: {q['area']}</b></small><br>
                        <strong style="font-size:1.3em; color: #FFFFFF;">Questão {i+1}</strong><br>{q['pergunta']}
                    </div>""", unsafe_allow_html=True)
                    opcoes_formatadas = [f"{k}) {v}" for k, v in q['opcoes'].items()]
                    resp = st.radio(f"Qual a jogada certa?", options=opcoes_formatadas, key=f"q_{i}")
                    st.session_state.respostas_usuario[i] = resp[0]
                    st.write("")
                if st.form_submit_button("APITO FINAL! 🏁"):
                    st.session_state.desafio_concluido = True
                    st.rerun()
        else:
            st.header("📊 Seu Level de Craque")
            acertos = 0
            stats = {}
            for i, q in enumerate(questoes):
                area = q['area']
                if area not in stats: stats[area] = {"corretas": 0, "total": 0}
                stats[area]["total"] += 1
                if st.session_state.respostas_usuario.get(i) == q['correta']:
                    acertos += 1
                    stats[area]["corretas"] += 1
            
            score_percent = (acertos / len(questoes)) * 100 if len(questoes) > 0 else 0

            if score_percent >= 90: nivel = "🌟 LENDA DA VÁRZEA"
            elif score_percent >= 70: nivel = "🔥 PROMESSA DA BASE"
            elif score_percent >= 50: nivel = "⚽ JOGADOR REGULAR"
            else: nivel = "👟 PRECISA DE MAIS TREINO"

            col_a, col_b = st.columns(2)
            with col_a: st.metric("Aproveitamento", f"{score_percent:.1f}%")
            with col_b: st.markdown(f"**Seu Nível:** <span style='font-size:20px; color:#FFD700; font-weight:bold;'>{nivel}</span>", unsafe_allow_html=True)

            if len(stats) > 0:
                df_stats = pd.DataFrame([{"Área": k, "Perc": (v["corretas"]/v["total"])*100} for k, v in stats.items()])
                fig = go.Figure(data=go.Bar(x=df_stats['Área'], y=df_stats['Perc'], marker_color='#00D1FF', text=df_stats['Perc'].apply(lambda x: f"{x:.0f}%"), textposition='auto'))
                fig.update_layout(title="Tua Evolução no Campo!", yaxis_range=[0, 100], template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("🔍 O que o Professor achou?")
            for i, q in enumerate(questoes):
                user_ans = st.session_state.respostas_usuario.get(i, "N/A")
                correct = q['correta']
                color = "#39FF14" if user_ans == correct else "#FF3131"
                st.markdown(f"""<div class="q-card" style="border-left: 10px solid {color}">
                    <strong style="color:#FFFFFF;">{q['area']} | Pergunta {i+1}</strong><br>{q['pergunta']}<br><br>
                    Tua jogada: <span style="color:{color}; font-weight:bold;">{user_ans}</span> | 
                    Jogada de Craque: <span style="color:#39FF14; font-weight:bold;">{correct}</span><br>
                    <small><b style="color:#FFD700;">⚽ Dica do Prof:</b> {q['justificativa']}</small>
                </div>""", unsafe_allow_html=True)
            
            if st.button("Voltar para o Vestiário 🏠"):
                st.session_state.desafio_atual_id = None
                st.session_state.desafio_concluido = False
                st.rerun()

elif menu == "🏆 Sala de Troféus":
    st.title("🏆 Galeria de Conquistas")
    df = get_desafios()
    if df.empty:
        st.info("Você ainda não jogou! Bora pro campo! ⚽")
    else:
        opcoes = df['id'].tolist()
        nomes = [f"ID {id} - {row['tema']} ({row['categoria']}) - {row['data']}" for id, row in zip(df['id'], df.to_dict('records'))]
        escolha = st.selectbox("Qual treino quer rever?", opcoes, format_func=lambda x: nomes[df[df['id']==x].index[0]])
        if st.button("Ver Jogadas"):
            questoes = get_questoes(escolha)
            for i, q in enumerate(questoes):
                st.markdown(f"""<div class="q-card">
                    <strong style="color:#FFFFFF;">{q['area']} | Questão {i+1}</strong><br>{q['pergunta']}<br><br>
                    <span style="color:#39FF14"><b>Resposta de Craque: {q['correta']}</b></span><br>
                    <small><b style="color:#FFD700;">✅ Dica:</b> {q['justificativa']}</small>
                </div>""", unsafe_allow_html=True)
