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
    st.error("⚠️ Erro: Chave de API não encontrada.")

# ==============================================================================
# 2. SISTEMA de BANCO de DADOS (Base Craque DB)
# ==============================================================================
DB_NAME = 'base_craque_v1.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabela de Desafios (Simulados)
    c.execute('CREATE TABLE IF NOT EXISTS desafios (id INTEGER PRIMARY KEY, categoria TEXT, posicao TEXT, tema TEXT, data TEXT)')
    # Tabela de Questões
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
    Você é o 'Professor Craque', um mentor lendário de categorias de base de futebol.
    Seu objetivo é criar um "Desafio de QI de Jogo" para um jovem atleta.
    CATEGORIA: {categoria} (Ex: Sub-11, Sub-15).
    POSIÇÃO: {posicao} (Ex: Zagueiro, Meio-campo, Atacante).
    TEMA: {tema} (Ex: Posicionamento Tático, Nutrição para Jogadores, Regras do Jogo, Mentalidade Vencedora).
    QUANTIDADE: {qtd} questões.
    
    Siga estas regras:
    1. Use linguagem simples, motivadora e jovem (estilo 'estamos juntos na caminhada').
    2. Misture perguntas teóricas com "Cenários de Jogo" (Ex: 'Você está com a bola no meio de campo, dois adversários fecham seu caminho, o que você faz?').
    3. Retorne EXCLUSIVAMENTE um JSON.
    
    Modelo do JSON:
    {{
      "questoes": [
        {{
          "area": "Tática/Nutrição/Regra/Mental",
          "pergunta": "Texto da pergunta ou cenário",
          "opcoes": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
          "correta": "A",
          "justificativa": "Explicação curta e educativa sobre por que essa é a melhor escolha."
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
# 4. INTERFACE DO USUÁRIO (FOOTBALL THEME)
# ==============================================================================
init_db()
st.set_page_config(page_title="Base Craque AI | Escola de Futebol", layout="wide", page_icon="⚽")

# CSS para transformar o app em um "estádio digital"
st.markdown("""
    <style>
    .stApp { background-color: #E8F5E9; color: #1B5E20; }
    [data-testid="stSidebar"] { background-color: #2E7D32 !important; color: white !important; }
    .q-card { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 2px solid #4CAF50; margin-bottom: 20px; color: #333; box-shadow: 4px 4px 0px #2E7D32; }
    .stButton>button { background-color: #FFD700 !important; color: #1B5E20 !important; font-weight: 800 !important; border-radius: 10px !important; border: 2px solid #1B5E20 !important; text-transform: uppercase; }
    .stButton>button:hover { background-color: #FFC107 !important; transform: scale(1.02); }
    h1, h2, h3 { color: #1B5E20 !important; font-family: 'Comic Sans MS', cursive, sans-serif !important; }
    .stat-box { background-color: #C8E6C9; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #2E7D32; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("⚽ Base Craque AI")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Menu do Atleta", ["🏠 Vestiário (Home)", "🎮 Iniciar Desafio", "🏆 Meus Troféus (Histórico)"])

if menu == "🏠 Vestiário (Home)":
    st.title("🏟️ Bem-vindo ao Vestiário, Craque!")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### Transforme seu jogo com inteligência! 🧠⚽
        Aqui você não treina apenas as pernas, treina a **mente**. 
        Aprenda tática, nutrição e regras para subir de nível e chegar ao profissional.
        
        **O que você encontra aqui:**
        - 🎯 **Desafios de QI de Jogo:** Teste sua visão de campo.
        - 🍎 **Dicas de Nutrição:** Coma como um atleta.
        - 📜 **Regras da Bola:** Saiba tudo para não levar cartão bobo.
        - 🛡️ **Mentalidade:** Aprenda a lidar com a pressão.
        """)
        st.success("💡 **Dica do Prof:** 'O talento ganha jogos, mas a inteligência ganha campeonatos!'")
    with col2:
        st.image("https://img.freepik.com/free-vector/soccer-player-concept-illustration_114360-11761.jpg", use_container_width=True)

elif menu == "🎮 Iniciar Desafio":
    st.title("🎮 Desafio de QI de Jogo")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Sua Categoria", ["Sub-11", "Sub-13", "Sub-15", "Sub-17", "Várzea Adulto"])
            posicao = st.selectbox("Sua Posição", ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"])
        with col2:
            tema = st.selectbox("O que quer dominar hoje?", ["Tática e Posicionamento", "Regras do Futebol", "Nutrição e Saúde", "Mentalidade e Foco"])
            qtd_total = st.slider("Quantas perguntas?", 5, 20, 10)
    
    if st.button("🚀 Começar Partida!"):
        with st.spinner("🏃 Coach preparando o treino..."):
            try:
                questoes = ai_generate_football_quiz(categoria, posicao, tema, qtd_total)
                if questoes:
                    id_desafio = save_desafio(categoria, posicao, tema)
                    save_questoes(id_desafio, questoes)
                    st.session_state.desafio_atual_id = id_desafio
                    st.session_state.respostas_usuario = {}
                    st.session_state.desafio_concluido = False
                    st.rerun()
            except Exception as e:
                st.error(f"Erro no treino: {e}")

    if 'desafio_atual_id' in st.session_state:
        des_id = st.session_state.desafio_atual_id
        questoes = get_questoes(des_id)
        
        if not st.session_state.get('desafio_concluido', False):
            st.markdown("### 📝 Hora de mostrar a visão de jogo!")
            with st.form("quiz_form"):
                for i, q in enumerate(questoes):
                    st.markdown(f"""<div class="q-card">
                        <small style="color: #2E7D32;"><b>ÁREA: {q['area']}</b></small><br>
                        <strong style="font-size:1.2em;">Questão {i+1}</strong><br>{q['pergunta']}
                    </div>""", unsafe_allow_html=True)
                    opcoes_formatadas = [f"{k}) {v}" for k, v in q['opcoes'].items()]
                    resp = st.radio(f"Qual a melhor jogada?", options=opcoes_formatadas, key=f"q_{i}")
                    st.session_state.respostas_usuario[i] = resp[0]
                    st.write("")
                if st.form_submit_button("Finalizar Partida 🏁"):
                    st.session_state.desafio_concluido = True
                    st.rerun()
        else:
            st.header("📊 Seu Relatório de Desempenho")
            
            # Cálculo de acertos
            acertos = 0
            stats = {}
            for i, q in enumerate(questoes):
                area = q['area']
                if area not in stats: stats[area] = {"corretas": 0, "total": 0}
                stats[area]["total"] += 1
                if st.session_state.respostas_usuario.get(i) == q['correta']:
                    acertos += 1
                    stats[area]["corretas"] += 1
            
            score_percent = (acertos / len(questoes)) * 100
            
            # Ranking de Nível
            if score_percent >= 90: nivel = "🌟 Lenda da Várzea"
            elif score_percent >= 70: nivel = "🔥 Promessa da Base"
            elif score_percent >= 50: nivel = "⚽ Jogador Regular"
            else: nivel = "👟 Iniciante (Precisa de Treino)"

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Aproveitamento", f"{score_percent:.1f}%")
            with col_b:
                st.markdown(f"**Seu Nível:** {nivel}")

            # Gráfico de Radar (Habilidades)
            df_stats = pd.DataFrame([{"Área": k, "Acertos": v["corretas"], "Total": v["total"], "Perc": (v["corretas"]/v["total"])*100} for k, v in stats.items()])
            
            fig = go.Figure(data=go.Bar(
                x=df_stats['Área'], y=df_stats['Perc'], 
                marker_color='#4CAF50', text=df_stats['Perc'].apply(lambda x: f"{x:.0f}%"), 
                textposition='auto'
            ))
            fig.update_layout(title="Habilidades Desenvolvidas", yaxis_range=[0, 100], template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("🔍 Análise do Treinador")
            for i, q in enumerate(questoes):
                user_ans = st.session_state.respostas_usuario.get(i, "N/A")
                correct = q['correta']
                color = "#2E7D32" if user_ans == correct else "#B22222"
                st.markdown(f"""<div class="q-card" style="border-left: 8px solid {color}">
                    <strong style="color:#1B5E20;">{q['area']} | Pergunta {i+1}</strong><br>{q['pergunta']}<br><br>
                    Sua jogada: <span style="color:{color}; font-weight:bold;">{user_ans}</span> | 
                    Jogada Correta: <span style="color:#2E7D32; font-weight:bold;">{correct}</span><br>
                    <small><b style="color:#1B5E20;">⚽ Explicação do Prof:</b> {q['justificativa']}</small>
                </div>""", unsafe_allow_html=True)
            
            if st.button("Voltar ao Vestiário 🏠"):
                st.session_state.desafio_atual_id = None
                st.session_state.desafio_concluido = False
                st.rerun()

elif menu == "🏆 Meus Troféus (Histórico)":
    st.title("🏆 Galeria de Conquistas")
    df = get_desafios()
    if df.empty:
        st.info("Você ainda não participou de nenhum desafio. Comece agora!")
    else:
        opcoes = df['id'].tolist()
        nomes = [f"ID {id} - {row['tema']} ({row['categoria']}) - {row['data']}" for id, row in zip(df['id'], df.to_dict('records'))]
        escolha = st.selectbox("Revisar qual treino?", opcoes, format_func=lambda x: nomes[df[df['id']==x].index[0]])
        if st.button("Rever Jogadas"):
            questoes = get_questoes(escolha)
            for i, q in enumerate(questoes):
                st.markdown(f"""<div class="q-card">
                    <strong style="color:#1B5E20;">{q['area']} | Questão {i+1}</strong><br>{q['pergunta']}<br><br>
                    <span style="color:#2E7D32"><b>Resposta Correta: {q['correta']}</b></span><br>
                    <small><b style="color:#1B5E20;">✅ Explicação:</b> {q['justificativa']}</small>
                </div>""", unsafe_allow_html=True)
