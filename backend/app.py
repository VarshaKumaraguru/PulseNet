from flask import Flask, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO
import time
import serial
import threading
import os
import csv
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
PDF_PATH = "temp.pdf" 

# Initialize Flask App
app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost/ecg_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "5b337c9cc35b5efd77de3b64bd577461fc9492dee2752153d371492844021d9c"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User Model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Sign-Up Route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, email=email, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    session["username"] = username
    return jsonify({"message": "User registered successfully", "username": username}), 201

# Login Route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "All fields are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session["username"] = user.username
        return jsonify({"message": "Login successful", "username": user.username}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Logout Route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

# Serve the CSV file
@app.route('/ecg_data.csv')
def serve_csv():
    return send_from_directory('.', 'ecg_data.csv')

# Summarize ECG Data
@app.route('/summarize_ecg', methods=['GET'])
def summarize_ecg():
    try:
        # Read ECG data from CSV
        data = pd.read_csv('ecg_data.csv')

        # Assuming the CSV has columns 'timestamp' and 'ecg_value'
        timestamps = data['timestamp'].values
        ecg_values = data['ecg_value'].values

        # Normalize timestamps (shift so the first time starts at zero)
        timestamps = timestamps - timestamps[0]

        # Find R-peaks (highest points in ECG)
        r_peaks, _ = find_peaks(ecg_values, height=np.mean(ecg_values) + 20)

        # Find Q-peaks (local minima before each R-peak)
        q_peaks = []
        for r_idx in r_peaks:
            search_window = range(max(0, r_idx - 10), r_idx)
            if len(search_window) > 0:
                q_idx = search_window[np.argmin(ecg_values[search_window])]
                q_peaks.append(q_idx)

        q_peaks = np.array(q_peaks)

        # Find P-peaks (local maxima before Q-peak)
        p_peaks = []
        for q_idx in q_peaks:
            search_window = range(max(0, q_idx - 15), q_idx)
            if len(search_window) > 0:
                p_idx = search_window[np.argmax(ecg_values[search_window])]
                p_peaks.append(p_idx)

        p_peaks = np.array(p_peaks)

        # Find S-peaks (local minima after R-peak)
        s_peaks = []
        for r_idx in r_peaks:
            search_window = range(r_idx, min(len(ecg_values), r_idx + 10))
            if len(search_window) > 0:
                s_idx = search_window[np.argmin(ecg_values[search_window])]
                s_peaks.append(s_idx)

        s_peaks = np.array(s_peaks)

        # Find T-peaks (local maxima after S-peak)
        t_peaks = []
        for s_idx in s_peaks:
            search_window = range(s_idx, min(len(ecg_values), s_idx + 20))
            if len(search_window) > 0:
                t_idx = search_window[np.argmax(ecg_values[search_window])]
                t_peaks.append(t_idx)

        t_peaks = np.array(t_peaks)

        # Convert time to milliseconds (ms)
        p_peak_times = timestamps[p_peaks] * 1000  # Convert seconds to ms
        q_peak_times = timestamps[q_peaks] * 1000
        r_peak_times = timestamps[r_peaks] * 1000
        s_peak_times = timestamps[s_peaks] * 1000
        t_peak_times = timestamps[t_peaks] * 1000

        # Calculate intervals (in ms)
        pr_intervals = (r_peak_times - p_peak_times)  # PR interval
        qrs_durations = (s_peak_times - q_peak_times)  # QRS duration
        qt_intervals = (t_peak_times - q_peak_times)  # QT interval

        # Calculate average values
        avg_p_peak_time = np.mean(p_peak_times)
        avg_q_peak_time = np.mean(q_peak_times)
        avg_r_peak_time = np.mean(r_peak_times)
        avg_s_peak_time = np.mean(s_peak_times)
        avg_t_peak_time = np.mean(t_peak_times)

        avg_p_value = np.mean(ecg_values[p_peaks])
        avg_q_value = np.mean(ecg_values[q_peaks])
        avg_r_value = np.mean(ecg_values[r_peaks])
        avg_s_value = np.mean(ecg_values[s_peaks])
        avg_t_value = np.mean(ecg_values[t_peaks])

        avg_pr_interval = np.mean(pr_intervals)
        avg_qrs_duration = np.mean(qrs_durations)
        avg_qt_interval = np.mean(qt_intervals)

        # Calculate R-R intervals in seconds
        rr_intervals_seconds = np.diff(r_peak_times / 1000)  # Convert ms to seconds and compute differences

        # Calculate Heart Rate (HR) for each R-R interval
        heart_rates = 60 / rr_intervals_seconds  # Convert R-R intervals to bpm

        # Filter out heart rates exceeding 110 bpm
        valid_indices = heart_rates <= 110
        filtered_rr_intervals = rr_intervals_seconds[valid_indices]
        filtered_heart_rates = heart_rates[valid_indices]

        # Calculate P wave duration (assuming P wave lasts a few ms before and after peak)
        p_wave_durations = []
        for p_idx in p_peaks:
            search_window = range(max(0, p_idx - 5), min(len(ecg_values), p_idx + 5))  # Small window around P peak
            start_p_idx = search_window[0]  # Start of P wave
            end_p_idx = search_window[-1]   # End of P wave
            p_wave_durations.append((timestamps[end_p_idx] - timestamps[start_p_idx]) * 1000)  # Convert to ms

        p_wave_durations = np.array(p_wave_durations)
        avg_p_wave_duration = np.mean(p_wave_durations)

        # Calculate QTc interval using Bazett’s formula
        if len(filtered_rr_intervals) > 0:
            avg_rr_interval = np.mean(filtered_rr_intervals)  # Already in seconds
            avg_qt_interval_sec = avg_qt_interval / 1000  # Convert ms to seconds
            qt_corrected = avg_qt_interval_sec / np.sqrt(avg_rr_interval)  # Bazett’s formula
            qt_corrected_ms = qt_corrected * 1000  # Convert back to ms
        else:
            qt_corrected_ms = None  # If no RR intervals are found

        # Prepare summary
        summary = {
            "data": {
                "heart_rate": 60 / np.mean(filtered_rr_intervals) if len(filtered_rr_intervals) > 0 else None,
                "p_wave_duration": avg_p_wave_duration,
                "pr_interval": avg_pr_interval,
                "qrs_duration": avg_qrs_duration,
                "qt_interval": avg_qt_interval,
                "qtc_interval": qt_corrected_ms,
            },
        }
        print("Summary:", summary)
        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serial Port Configuration
SERIAL_PORT = "COM5"
BAUD_RATE = 9600
serial_connection = None
ecg_data = []
collecting = False

def read_ecg_data():
    global serial_connection, collecting, ecg_data
    start_time = time.time()
    while collecting and (time.time() - start_time) < 120:
        try:
            if serial_connection is None:
                serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                print(f"✅ Connected to {SERIAL_PORT}")

            line = serial_connection.readline().decode("utf-8").strip()
            if line:
                try:
                    time_val, ecg_val = map(float, line.split(","))
                    print(f"ECG Data -> Time: {time_val}, Value: {ecg_val}")

                    socketio.emit("live_ecg_data", {"time": time_val, "ecg": ecg_val})

                    ecg_data.append((time_val, ecg_val))

                except ValueError:
                    print("⚠ Invalid ECG Data Format: ", line)
        
        except serial.SerialException as e:
            print(f"❌ Serial Error: {e}")
            serial_connection = None
            time.sleep(3)

    collecting = False
    if serial_connection:
        try:
            serial_connection.close()
        except Exception as e:
            print(f"❌ Error closing serial connection: {e}")
        serial_connection = None
    save_to_csv()

def save_to_csv():
    file_path = r'C:\Users\Varsha K\ECG_WEB\backend\ecg_data.csv'
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(ecg_data)
    ecg_data.clear()

@socketio.on("start_ecg")
def handle_start_ecg():
    global collecting
    if not collecting:
        collecting = True
        threading.Thread(target=read_ecg_data, daemon=True).start()

@socketio.on("stop_ecg")
def handle_stop_ecg():
    global collecting
    collecting = False
    save_to_csv()

@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Gemma2-9b-It")

# Load PDF and initialize retriever
if os.path.exists(PDF_PATH):
    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever()
else:
    retriever = None

search_tool = DuckDuckGoSearchRun()

# Initialize session store for chat history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    user_input = data.get("query")
    session_id = data.get("session_id", "default_session")

    if not retriever:
        return jsonify({"error": "Backend document missing. Please upload a PDF in the backend."}), 400

    # Initialize chains
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history and the last user question, reformulate it into a standalone question."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Use retrieved context to answer. If unknown, say 'I don't know'. \n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Get session history
    session_history = get_session_history(session_id)

    # Invoke the RAG chain
    response = rag_chain.invoke({"input": user_input, "chat_history": session_history.messages})
    answer = response.get('answer', 'No response')

    # Remove asterisks from the answer
    answer = answer.replace("**", "")

    # Fallback to search engine if the answer is "I don't know"
    if "don't know" in answer.lower():
        search_results = search_tool.run(user_input)
        answer = f"Based on an online search: {search_results}" if search_results else "I'm sorry, I couldn't find an answer."

    # Update session history
    session_history.add_user_message(user_input)
    session_history.add_ai_message(answer)

    return jsonify({"response": answer})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)