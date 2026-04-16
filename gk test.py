import streamlit as st
import pandas as pd
import json
import os
import glob
import streamlit.components.v1 as components

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title="The LikeStudy - Premium Quiz")

# --- 🛡️ ANTI-COPY SECURITY (STREAMLIT UI) 🛡️ ---
st.markdown("""
    <style>
    /* Disable Text Selection */
    * {
        -webkit-user-select: none; /* Safari */
        -ms-user-select: none; /* IE 10+ */
        user-select: none; /* Standard */
    }
    /* Hide Streamlit Top Menu for Security */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- UNLIMITED AUTO-LOADER SYSTEM ---
def load_all_csv_data():
    all_questions = []
    # Find ALL .csv files in the folder
    csv_files = glob.glob("*.csv")
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if all(col in df.columns for col in ['q', 'A', 'B', 'C', 'D', 'ans']):
                if 'sub' not in df.columns: df['sub'] = file.replace(".csv", "").upper() # Name subject by filename if missing
                df = df.fillna("")
                clean_df = df[['q', 'A', 'B', 'C', 'D', 'ans', 'sub']]
                all_questions.extend(clean_df.to_dict(orient='records'))
        except:
            pass # Skip corrupted files
            
    if len(all_questions) > 0:
        return all_questions
    else:
        # Emergency Fallback
        return [
            {"q": "अमेज़ॅन नदी किस महासागर में गिरती है?", "A": "आर्कटिक", "B": "अटलांटिक", "C": "हिंद", "D": "प्रशांत", "ans": "B", "sub": "Geography"},
            {"q": "भारतीय संविधान में कितने भाग (Parts) हैं?", "A": "22", "B": "25", "C": "20", "D": "18", "ans": "B", "sub": "Polity"}
        ]

def save_manual_data():
    # Save manual dashboard entries to a specific file so it doesn't overwrite your uploads
    if len(st.session_state.quiz_data) > 0:
        pd.DataFrame(st.session_state.quiz_data).to_csv('studio_added_questions.csv', index=False)

if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = load_all_csv_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe; text-align:center;'>⚡ NEON STUDIO</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#ff00cc; text-align:center; font-size:12px; font-weight:bold;'>© 2026 The LikeStudy.<br>All Rights Reserved.</p>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color: rgba(0, 242, 254, 0.3);'>", unsafe_allow_html=True)

app_mode = st.sidebar.radio("🎮 SELECT MODE:", ["📱 Live Neon Quiz", "⚙️ Studio Dashboard"])

# 🎯 SUBJECT FILTER
if len(st.session_state.quiz_data) > 0:
    unique_subjects = list(set([q.get('sub', 'GK') for q in st.session_state.quiz_data]))
    unique_subjects.sort()
    options = ["🌐 Mixed (All Subjects)"] + unique_subjects
    selected_subject = st.sidebar.selectbox("Choose Subject:", options)
else:
    selected_subject = "None"

# ==========================================
# MODE 1: LIVE QUIZ (WITH ANTI-THEFT)
# ==========================================
if app_mode == "📱 Live Neon Quiz":
    display_sub = selected_subject.replace("🌐 ", "")
    st.markdown(f"<h3 style='text-align:center; color:#00f2fe; text-transform:uppercase;'>⚡ LIVE: {display_sub} TEST</h3>", unsafe_allow_html=True)
    
    if len(st.session_state.quiz_data) > 0:
        if selected_subject == "🌐 Mixed (All Subjects)":
            filtered_data = st.session_state.quiz_data
        else:
            filtered_data = [q for q in st.session_state.quiz_data if q.get('sub', 'GK') == selected_subject]
        
        quiz_json = json.dumps(filtered_data)
        
        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Mukta:wght@400;700&display=swap');
            
            /* 🛡️ ANTI-COPY CSS 🛡️ */
            body { 
                font-family: 'Mukta', sans-serif; background-color: transparent; margin: 0; padding: 10px 0; display: flex; justify-content: center;
                -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; /* Block Text Selection */
            }
            
            .mobile-screen { width: 440px; height: 800px; background: radial-gradient(circle at top, #1a1a2e 0%, #050505 100%); border-radius: 30px; box-shadow: 0 0 30px rgba(0, 242, 254, 0.3); padding: 20px; box-sizing: border-box; position: relative; display: flex; flex-direction: column; border: 2px solid #00f2fe; overflow: hidden; }
            .flash-effect { background: white !important; box-shadow: 0 0 100px white !important; }
            #start-overlay, #restart-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5, 5, 5, 0.95); z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(10px); }
            .start-btn { background: linear-gradient(45deg, #00f2fe, #ff00cc); color: white; border: none; padding: 15px 40px; border-radius: 50px; font-size: 24px; font-weight: bold; font-family: 'Orbitron'; cursor: pointer; }
            .time-display { font-family: 'Orbitron', sans-serif; font-size: 38px; font-weight: bold; color: #00f2fe; text-shadow: 0 0 15px #00f2fe; text-align: center;}
            .timer-bg { width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden; margin-top: 5px;}
            .timer-fill { height: 100%; width: 100%; background: linear-gradient(90deg, #00f2fe, #ff00cc); transition: width 10s linear; }
            .question-box { background: rgba(255, 255, 255, 0.03); border-left: 4px solid #ff00cc; padding: 15px; border-radius: 12px; font-size: 24px; font-weight: bold; color: #fff; margin-bottom: 20px; min-height: 110px; display: flex; align-items: center; }
            .option { background: rgba(15, 15, 26, 0.8); border: 1px solid #333; border-radius: 12px; padding: 15px; font-size: 20px; font-weight: bold; color: #ddd; margin-bottom: 12px; display: flex; align-items: center; transition: 0.2s; }
            .opt-tag { background: rgba(0, 242, 254, 0.1); border: 1px solid #00f2fe; padding: 4px 12px; border-radius: 8px; margin-right: 15px; color: #00f2fe; font-family: 'Orbitron'; }
            .option.correct { background: rgba(0, 255, 136, 0.2) !important; border-color: #00ff88 !important; box-shadow: 0 0 30px #00ff88; transform: scale(1.05); animation: shake 0.5s both; }
            .option.wrong { opacity: 0.3; filter: grayscale(1); }
            @keyframes shake { 10%, 90% { transform: translate3d(-1px, 0, 0) scale(1.05); } 30%, 70% { transform: translate3d(-4px, 0, 0) scale(1.05); } 50% { transform: translate3d(4px, 0, 0) scale(1.05); } }
            
            /* BRANDING */
            .brand-footer { margin-top: auto; text-align: center; padding-top: 15px; border-top: 1px dashed rgba(0, 242, 254, 0.3); }
            .brand-name { font-family: 'Orbitron', sans-serif; font-size: 24px; font-weight: bold; color: #fff; text-shadow: 0 0 10px #ff00cc; letter-spacing: 2px; text-transform: uppercase; }
            .brand-handle { font-family: 'Orbitron', sans-serif; font-size: 14px; color: #00f2fe; margin-top: 5px; margin-bottom: 8px; }
            .creator-name { font-family: 'Mukta', sans-serif; font-size: 13px; color: #888; text-transform: uppercase; }
        </style>
        </head>
        <body>
        <div class="mobile-screen" id="quiz-box">
            <div id="start-overlay"><button class="start-btn" onclick="startQuiz()">🚀 START QUIZ</button></div>
            <div id="restart-overlay" style="display:none; text-align:center;">
                <div style="color:#00f2fe; font-size:24px; font-family:Orbitron;">QUIZ RESTARTING...</div>
                <div id="restart-timer" style="font-size:60px; color:#ff00cc; font-family:Orbitron;">30</div>
            </div>
            <div class="timer-container"><div class="time-display" id="timer-text">10.0s</div><div class="timer-bg"><div class="timer-fill" id="t-bar"></div></div></div>
            <div style="display:flex; justify-content:space-between; margin:10px 0; font-family:Orbitron; color:#aaa;">
                <div id="sub-tag" style="color:#00f2fe;">SUBJECT</div>
                <div id="q-num">Q 1/10</div>
            </div>
            <div class="question-box" id="q-text">Loading...</div>
            <div class="options-container">
                <div class="option" id="opt-A"><div class="opt-left"><span class="opt-tag">A</span> <span id="text-A">...</span></div></div>
                <div class="option" id="opt-B"><div class="opt-left"><span class="opt-tag">B</span> <span id="text-B">...</span></div></div>
                <div class="option" id="opt-C"><div class="opt-left"><span class="opt-tag">C</span> <span id="text-C">...</span></div></div>
                <div class="option" id="opt-D"><div class="opt-left"><span class="opt-tag">D</span> <span id="text-D">...</span></div></div>
            </div>
            <div class="brand-footer">
                <div class="brand-name">The LikeStudy</div>
                <div class="brand-handle">@TopStudyPro</div>
                <div class="creator-name">Created by Anuj Kumar</div>
            </div>
        </div>
        <script>
            // 🛡️ ANTI-THEFT JAVASCRIPT 🛡️
            document.addEventListener('contextmenu', event => event.preventDefault()); // Block Right Click
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && (e.key === 'c' || e.key === 'u' || e.key === 'i' || e.key === 'j' || e.key === 's')) {
                    e.preventDefault(); // Block Inspect Element & Copying
                }
            });

            const quizData = """ + quiz_json + """;
            let currentIndex = 0; let timerInterval; let tickCount = 0;
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            let audioCtx;

            function initAudio() { if (!audioCtx) audioCtx = new AudioContext(); if (audioCtx.state === 'suspended') audioCtx.resume(); }
            
            function playTick() { 
                if(!audioCtx) return; const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                tickCount++; let isTock = (tickCount % 2 === 0);
                osc.type = 'triangle'; osc.frequency.setValueAtTime(isTock ? 600 : 800, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.5, audioCtx.currentTime); gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime+0.05);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime+0.05);
            }

            function playWin() {
                if(!audioCtx) return; const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'square'; osc.frequency.setValueAtTime(150, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.5, audioCtx.currentTime); gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime+0.5);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime+0.5);
            }

            function startQuiz() { document.getElementById("start-overlay").style.display = "none"; initAudio(); loadQuestion(); }

            function loadQuestion() {
                if(currentIndex >= quizData.length) { showRestart(); return; }
                let q = quizData[currentIndex];
                document.getElementById("q-num").innerText = `Q ${currentIndex + 1}/${quizData.length}`;
                document.getElementById("sub-tag").innerText = q.sub || "GK";
                document.getElementById("q-text").innerText = q.q;
                ['A','B','C','D'].forEach(opt => {
                    document.getElementById("opt-" + opt).className = "option";
                    document.getElementById("text-" + opt).innerText = q[opt];
                });
                let timeLeft = 100;
                let tBar = document.getElementById("t-bar"); tBar.style.transition = "none"; tBar.style.width = "100%";
                setTimeout(() => { tBar.style.transition = "width 10s linear"; tBar.style.width = "0%"; }, 50);
                clearInterval(timerInterval);
                timerInterval = setInterval(() => {
                    timeLeft--;
                    if(timeLeft > 0 && timeLeft % 10 === 0) playTick();
                    document.getElementById("timer-text").innerText = (timeLeft / 10).toFixed(1) + "s";
                    if(timeLeft <= 0) { clearInterval(timerInterval); showAnswer(q.ans); }
                }, 100);
            }

            function showAnswer(ans) {
                playWin(); document.getElementById("quiz-box").classList.add("flash-effect");
                setTimeout(() => document.getElementById("quiz-box").classList.remove("flash-effect"), 200);
                ['A','B','C','D'].forEach(opt => {
                    let el = document.getElementById("opt-" + opt);
                    if(opt === ans.toUpperCase()) el.classList.add("correct"); else el.classList.add("wrong");
                });
                setTimeout(() => { currentIndex++; loadQuestion(); }, 2000); 
            }

            function showRestart() {
                document.getElementById("restart-overlay").style.display = "flex";
                let wait = 30;
                let loop = setInterval(() => {
                    wait--; document.getElementById("restart-timer").innerText = wait;
                    if(wait <= 0) { clearInterval(loop); document.getElementById("restart-overlay").style.display = "none"; currentIndex = 0; loadQuestion(); }
                }, 1000);
            }
        </script>
        </body>
        </html>
        """
        components.html(html_code, height=850)

# ==========================================
# MODE 2: STUDIO DASHBOARD
# ==========================================
elif app_mode == "⚙️ Studio Dashboard":
    st.title("⚙️ Security & Dashboard")
    st.error("🔒 **Anti-Copy Protection Active:** Right-click and text selection are disabled on the live quiz.")
    
    total_q = len(st.session_state.quiz_data)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<div style='background:rgba(0,242,254,0.1); border:2px solid #00f2fe; padding:20px; border-radius:15px; text-align:center;'><h2 style='margin:0; color:#00f2fe; font-size:40px;'>{total_q}</h2><p style='margin:0; color:white; font-weight:bold;'>Total Questions Loaded</p></div>", unsafe_allow_html=True)
        st.info("💡 **PRO TIP:** You can upload as many `.csv` files as you want to your GitHub repo. The app will automatically merge them all!")

    with col2:
        tab1, tab2 = st.tabs(["✍️ Add Manual Question", "🔍 View All Questions"])

        with tab1:
            st.write("ये सवाल सीधा डेटाबेस में परमानेंट सेव हो जाएंगे।")
            new_q = st.text_area("Question:")
            c1, c2 = st.columns(2)
            with c1: a = st.text_input("A:"); c = st.text_input("C:")
            with c2: b = st.text_input("B:"); d = st.text_input("D:")
            c3, c4 = st.columns(2)
            with c3: correct_opt = st.selectbox("Answer:", ["A", "B", "C", "D"])
            with c4: sub_name = st.text_input("Subject:", "GK")

            if st.button("➕ Add & Save"):
                if new_q and a and b and c and d and sub_name:
                    st.session_state.quiz_data.append({"q": new_q, "A": a, "B": b, "C": c, "D": d, "ans": correct_opt, "sub": sub_name})
                    save_manual_data()
                    st.success("✅ Saved!")
                    import time; time.sleep(0.5); st.rerun()

        with tab2:
            if total_q > 0: 
                st.dataframe(pd.DataFrame(st.session_state.quiz_data), use_container_width=True)
            else: st.info("No questions to show.")
