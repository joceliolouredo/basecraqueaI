import streamlit as st
from groq import Groq
import json
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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
# 3. MOTOR DE GERAÇÃO de DESAFIOS (IA GROQ)
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
# 4. INTERFACE PREMIUM - ESTILO PLAYER CARD (GAMER MODE)
# ==============================================================================

init_db()

st.set_page_config(page_title="Base Craque AI ⚽", layout="wide", page_icon="⚽")

# BACKGROUND ESTILO "PLAYER STUDIO" (Sombreado com luzes)
# Usei uma imagem de estádio moderno com luzes dramáticas
PLAYER_BG_URL = "https://images.unsplash.com/photo-1522770179538-7140a50434d1?q=80&w=2000&auto=format&fit=crop"

st.markdown(f"""
    <style>
    /* Fundo do App: Estúdio de Jogador / Estádio Moderno */
    .stApp {{ 
        background-image: url('{PLAYER_BG_URL}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Overlay Escuro para dar contraste de "Game" */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.7) 100%);
        z-index: -1;
    }}

    /* Sidebar: Estilo Carbono / Dark Premium */
    [data-testid="stSidebar"] {{ 
        background-color: rgba(20, 20, 20, 0.9) !important; 
        backdrop-filter: blur(15px);
        border-right: 6px solid #FFD700; 
    }}
    
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stText {{
        color: #FFD700 !important;
    }}

    /* Cards: Efeito de Carta de Jogador (Semi-transparente com brilho) */
    .q-card {{ 
        background-color: rgba(255, 255, 255, 0.85); 
        padding: 25px; 
        border-radius: 20px; 
        border: 3px solid #FFD700; 
        margin-bottom: 25px; 
        color: #1B5E20; 
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5); 
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-align: center;
    }}
    
    /* Botões: Gold Neon */
    .stButton>button {{ 
        background-color: #FFD700 !important; 
        color: #000 !important; 
        font-weight: 900 !important; 
        font-size: 18px !important;
        border-radius: 50px !important; 
        border: 2px solid #FFF !important; 
        padding: 10px 20px !important;
        transition: 0.3s; 
        text-transform: uppercase;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
    }}
    .stButton>button:hover {{ 
        background-color: #FFF !important; 
        color: #000 !important;
        transform: scale(1.1); 
        box-shadow: 0 0 25px #FFD700;
    }}
    
    h1, h2, h3 {{ 
        color: #FFD700 !important; 
        font-family: 'Comic Sans MS', cursive, sans-serif !important; 
        text-shadow: 2px 2px 4px #000;
    }}
    
    /* Inputs: Dark Mode com borda dourada */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{ 
        border-radius: 15px !important; 
        border: 2px solid #FFD700 !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("⚽ Base Craque AI")
st.sidebar.markdown("### MENU DO JOGO")
menu = st.sidebar.radio("Escolha sua fase:", ["🏠 Vestiário", "🎮 Jogar Desafio", "🏆 Sala de Troféus"])

if menu == "🏠 Vestiário":
    st.title("🏟️ Central do Craque")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 30px; border: 4px solid #FFD700; box-shadow: 0px 15px 30px rgba(0,0,0,0.5);">
            <h2 style="margin-top:0; color: #1B5E20;">Suba para o Nível Pro! 🚀⚽</h2>
            <p style="font-size: 1.2em; color: #333;">Você entrou na elite. Aqui, a gente não treina só o pé, treina a <b>visão de jogo</b>!</p>
            <br>
            <div style="font-size: 1.1em; color: #1B5E20;">
                ⚡ <b style="color:#000;">SISTEMA DE RANKING:</b> Acerte e vire Lenda.<br>
                🧠 <b style="color:#000;">TÁTICA AVANÇADA:</b> Aprenda a ler o jogo.<br>
                🍎 <b style="color:#000;">PERFORMANCE:</b> Nutrição de atleta profissional.<br>
                🛡️ <b style="color:#000;">MENTALIDADE:</b> Foco de campeão.
            </div
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("💡 **Dica do Prof:** 'O talento ganha jogos, mas a inteligência ganha campeonatos!' ⚽")
    with col2:
        st.image("jogador.jpg.png", use_container_width=True)

elif menu == "🎮 Jogar Desafio":
    st.title("🎮 Desafio de QI de Jogo")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Sua Categoria 👦", ["Sub-11", "Sub-13", "Sub-15", "Sub-17", "Várzea Adulto"])
            posicao = st.selectbox("Sua Posição 🛡️", ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"])
        with col2:
            tema = st.selectbox("Treino do Dia 📚", ["Tática e Posicionamento", "Regras do Futebol", "Nutrição e Saúde", "Mentalidade e Foco"])
            qtd_total = st.slider("Intensidade do Treino (Questões) ⚡", 5, 20, 10)
    
    if st.button("🚀 INICIAR PARTIDA!"):
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
            st.markdown("### 📝 Visão de Jogo: Escolha a Jogada Certa!")
            with st.form("quiz_form"):
                for i, q in enumerate(questoes):
                    st.markdown(f"""<div class="q-card">
                        <small style="color: #4CAF50;"><b>🌟 ÁREA: {q['area']}</b></small><br>
                        <strong style="font-size:1.3em; color:#1B5E20;">Questão {i+1}</strong><br>{q['pergunta']}
                    </div>""", unsafe_allow_html=True)
                    opcoes_formatadas = [f"{k}) {v}" for k, v in q['opcoes'].items()]
                    resp = st.radio(f"Qual a jogada?", options=opcoes_formatadas, key=f"q_{i}")
                    st.session_state.respostas_usuario[i] = resp[0]
                    st.write("")
                if st.form_submit_button("APITO FINAL! 🏁"):
                    st.session_state.desafio_concluido = True
                    st.rerun()
        else:
            st.header("📊 Seu Ranking de Performance")
            acertos = 0
            stats = {}
            for i, q in enumerate(questoes):
                area = q['area']
                if area not in stats: stats[area] = {"corretas": 0, "total": 0}
                stats[area]["total"] += 1
                if st.session_state.respostas_usuario.get(i) == q['correta']:
                    acertos += 1
                    stats[area]["corretas"] += 1
            
            if len(questoes) > 0:
                score_percent = (acertos / len(questoes)) * 100
            else:
                score_percent = 0

            if score_percent >= 90: nivel = "🌟 LENDA DA VÁRZEA"
            elif score_percent >= 70: nivel = "🔥 PROMESSA DA BASE"
            elif score_percent >= 50: nivel = "⚽ JOGADOR REGULAR"
            else: nivel = "👟 PRECISA DE MAIS TREINO"

            col_a, col_b = st.columns(2)
            with col_a: st.metric("Aproveitamento", f"{score_percent:.1f}%")
            with col_b: st.markdown(f"**Seu Nível:** <span style='font-size:20px; color:#FFD700;'>{nivel}</span>", unsafe_allow_html=True)

            if len(stats) > 0:
                df_stats = pd.DataFrame([{"Área": k, "Perc": (v["corretas"]/v["total"])*100} for k, v in stats.items()])
                fig = go.Figure(data=go.Bar(x=df_stats['Área'], y=df_stats['Perc'], marker_color='#FFD700', text=df_stats['Perc'].apply(lambda x: f"{x:.0f}%"), textposition='auto'))
                fig.update_layout(title="Tua Evolução no Campo!", yaxis_range=[0, 100], template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("🔍 Análise do Professor")
            for i, q in enumerate(questoes):
                user_ans = st.session_state.respostas_usuario.get(i, "N/A")
                correct = q['correta']
                color = "#2E7D32" if user_ans == correct else "#B22222"
                st.markdown(f"""<div class="q-card" style="border-left: 10px solid {color}">
                    <strong style="color:#1B5E20;">{q['area']} | Pergunta {i+1}</strong><br>{q['pergunta']}<br><br>
                    Tua jogada: <span style="color:{color}; font-weight:bold;">{user_ans}</span> | 
                    Jogada de Craque: <span style="color:#2E7D32; font-weight:bold;">{correct}</span><br>
                    <small><b style="color:#1B5E20;">⚽ Dica do Prof:</b> {q['justificativa']}</small>
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
                    <strong style="color:#1B5E20;">{q['area']} | Questão {i+1}</strong><br>{q['pergunta']}<br><br>
                    <span style="color:#2E7D32"><b>Resposta de Craque: {q['correta']}</b></span><br>
                    <small><b style="color:#1B5E20;">✅ Dica:</b> {q['justificativa']}</small>
                </div>""", unsafe_allow_html=True)
