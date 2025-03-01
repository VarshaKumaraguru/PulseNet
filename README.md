# Wireless ECG Measurement System

## Overview
The **Wireless ECG Measurement System** is a wearable device designed to monitor and display real-time ECG signals on a website. It captures ECG signals using the **AD8232ACPZ-R7** sensor and transmits data via an **HC-05 Bluetooth module** to an **Arduino Uno**. The data is then processed and visualized on a website built with **React.js**, **Node.js**, **Flask**, and stored in a **PostgreSQL** database.

The system integrates **AI-based analytics** to assist in detecting potential heart abnormalities. Additionally, it features an **AI-powered RAG chatbot** built using **Google’s Gemma**, which provides instant answers to ECG-related queries, enhancing user experience and medical insights.

## Features
- **Real-time ECG signal monitoring** using AD8232ACPZ-R7.
- **Wireless data transmission** via HC-05 Bluetooth module.
- **Web-based visualization** using React.js, Node.js, Flask, and PostgreSQL.
- **AI-based ECG analysis** for early detection of abnormalities.
- **RAG chatbot powered by Google's Gemma** for ECG-related queries.

## Technologies Used
- **Frontend:** React.js
- **Backend:** Node.js, Flask
- **Database:** PostgreSQL
- **Hardware:** AD8232ACPZ-R7, HC-05 Bluetooth module, Arduino Uno
- **AI Integration:** Google’s Gemma (RAG chatbot)

## Installation & Setup
### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/wireless-ecg-monitor.git
cd wireless-ecg-monitor
```

### 2. Setup the Web Application
#### Install Dependencies
```sh
cd frontend
npm install
```
#### Start the React Frontend
```sh
npm start
```

### 3. Setup the Backend
#### Install Dependencies
```sh
cd backend
pip install -r requirements.txt
npm install
```
#### Start the Flask Server
```sh
python app.py
```
#### Start the Node.js Server
```sh
node server.js
```

## Usage
- Wear the ECG device and ensure the **HC-05 Bluetooth module** is connected to the Arduino Uno.
- Open the **web app** to visualize real-time ECG data.
- Use the **AI-based chatbot** to ask ECG-related medical questions.
