# CreatCode — AI Code Generator & Explainer

> An AI-powered coding assistant that helps developers generate, explain, debug, optimize, test, convert, and analyze code using natural language.

🌐 **Live Website:** https://creatcode.onrender.com/

📦 **GitHub Repository:** https://github.com/aryan1704-ai/CreatCode

---

## 🚀 Overview

**CreatCode** is an AI-powered online code generator and programming assistant designed to make software development easier and faster.

Users can describe a programming problem in natural language and use AI to generate code, understand existing code, find bugs, optimize solutions, analyze time and space complexity, create test cases, convert code between programming languages, and interact with an AI coding assistant.

The project combines a modern developer-focused frontend with a **FastAPI backend** and **OpenRouter AI models**.

---

## ✨ Features

### 🤖 AI Code Generation
Generate programming solutions from natural-language prompts.

### 📖 Code Explanation
Understand complex code through simple, structured explanations.

### 🐛 AI Debugging
Analyze code and errors to identify possible bugs and suggest fixes.

### ⚡ Code Optimization
Get suggestions for improving code efficiency, readability, and performance.

### 📊 Complexity Analysis
Analyze algorithms and understand their:

- Time Complexity
- Space Complexity
- Big-O notation
- Performance considerations

### 🧪 Test Case Generation
Automatically generate useful test cases for programming problems.

### 🔄 Code Conversion
Convert code between supported programming languages.

### 💬 AI Coding Chat
Ask questions about programming concepts or the currently opened code.

### ▶️ Code Execution
Run supported Python code directly through the backend.

### 📁 Project Management
Create and manage coding projects and maintain generated-code history.

### 🎨 Developer-Focused Interface
A dark, modern SaaS-style coding workspace inspired by professional developer tools.

---

## 🖥️ Live Demo

Try CreatCode online:

👉 **https://creatcode.onrender.com/**

No local installation is required to explore the deployed application.

---

## 🛠️ Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Prism.js
- Lucide Icons
- Responsive UI
- Dark/Light theme

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### AI

- OpenRouter API
- OpenAI-compatible API interface

### Database

- SQLite for deployment
- MySQL for local development

### Deployment

- GitHub
- Render

---

## 🏗️ Project Architecture

```text
CreatCode
│
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   │
│   │   ├── api
│   │   │   ├── generate.py
│   │   │   ├── explain.py
│   │   │   ├── debug.py
│   │   │   ├── optimize.py
│   │   │   ├── complexity.py
│   │   │   ├── testcases.py
│   │   │   ├── convert.py
│   │   │   ├── prompt.py
│   │   │   ├── projects.py
│   │   │   ├── history.py
│   │   │   ├── users.py
│   │   │   ├── run.py
│   │   │   └── chat.py
│   │   │
│   │   └── services
│   │       └── ai_service.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend
│   ├── index.html
│   ├── css
│   │   ├── style.css
│   │   └── a11y.css
│   │
│   └── js
│       └── app.js
│
├── database
│
├── README.md
└── .gitignore