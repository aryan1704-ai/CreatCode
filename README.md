# 🚀 CreatCode

> AI-powered developer workspace for generating, explaining, debugging, optimizing, converting, and analyzing code.

CreatCode is a full-stack AI coding assistant designed to help developers write and understand code faster.

It combines a modern developer-focused frontend with a FastAPI backend, MySQL database, and OpenRouter-powered AI services.

---

## ✨ Features

### 🤖 AI Code Generation
Describe what you want to build in natural language and CreatCode generates code automatically.

### 📖 Code Explanation
Understand existing code with clear AI-generated explanations.

### 🐛 Code Debugging
Analyze code and identify possible errors and fixes.

### ⚡ Code Optimization
Get suggestions for improving code quality and efficiency.

### 🧪 Test Case Generator
Generate test cases for the current code.

### 📊 Complexity Analysis
Analyze the time and space complexity of code.

### 🔄 Code Conversion
Convert code between supported programming languages.

### 💬 AI Coding Chat
Ask questions about your current code and receive AI-powered assistance.

### ▶️ Code Execution
Run Python code directly through the CreatCode backend with execution timeout protection.

> Note: Multi-language server-side execution is not currently enabled.

### 📁 Projects
Create and manage coding projects.

### 🕘 Generation History
Previously generated code is stored and can be loaded again.

### 📋 Developer Tools

- Copy code
- Download code
- Syntax highlighting
- Line numbers
- Cursor position
- Language detection
- Dark / Light mode
- Responsive interface
- Keyboard shortcuts
- Accessibility-focused UI

---

## 🖥️ Screenshots

Add screenshots of the application here.

Example:

```text
screenshots/
├── dashboard.png
├── code-generation.png
├── ai-chat.png
└── mobile.png
```

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      User Browser    │
                    │                      │
                    │  HTML + CSS + JS     │
                    └──────────┬───────────┘
                               │
                               │ HTTP / REST API
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │      Backend         │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐   ┌──────────────┐
       │  OpenRouter│   │    MySQL    │   │ Code Runner  │
       │     AI     │   │  Database   │   │   Python     │
       └────────────┘   └─────────────┘   └──────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Prism.js
- Lucide Icons
- Responsive Design
- Accessibility / WCAG-focused UI

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy

### Database

- MySQL
- PyMySQL

### AI

- OpenRouter API
- OpenAI-compatible Python SDK

### Development

- Visual Studio Code
- Git
- GitHub
- Windows / PowerShell

---

## 📁 Project Structure

```text
CreatCode/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── complexity.py
│   │   │   ├── convert.py
│   │   │   ├── debug.py
│   │   │   ├── explain.py
│   │   │   ├── generate.py
│   │   │   ├── history.py
│   │   │   ├── optimize.py
│   │   │   ├── projects.py
│   │   │   ├── prompt.py
│   │   │   ├── run.py
│   │   │   ├── testcases.py
│   │   │   └── users.py
│   │   │
│   │   ├── services/
│   │   │   └── ai_service.py
│   │   │
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   ├── .env
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── assets/
│   │   └── logo.png
│   ├── css/
│   │   ├── style.css
│   │   └── a11y.css
│   ├── js/
│   │   └── app.js
│   └── index.html
│
├── database/
│
├── .gitignore
└── README.md
```

> `.env` is intentionally excluded from GitHub.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/aryan1704-ai/CreatCode.git
cd CreatCode
```

---

## 2. Backend setup

Go to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. MySQL Database

Install MySQL and create the database:

```sql
CREATE DATABASE creatcode;
```

The application uses MySQL through SQLAlchemy and PyMySQL.

---

## 4. Environment Variables

Create:

```text
backend/.env
```

Add:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free

DATABASE_URL=mysql+pymysql://username:password@localhost:3306/creatcode
```

Never commit the real `.env` file to GitHub.

---

## 5. Start the Backend

From:

```text
backend/
```

run:

```powershell
uvicorn main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🌐 Start the Frontend

Open another PowerShell terminal.

Go to:

```powershell
cd C:\CreatCode\frontend
```

Start a local web server:

```powershell
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

---

# 🔌 API Endpoints

| Feature | Endpoint | Method |
|---|---|---|
| Generate Code | `/api/generate/` | POST |
| Explain Code | `/api/explain/` | POST |
| Debug Code | `/api/debug/` | POST |
| Optimize Code | `/api/optimize/` | POST |
| Complexity | `/api/complexity/` | POST |
| Test Cases | `/api/testcases/` | POST |
| Convert Code | `/api/convert/` | POST |
| Prompt Generator | `/api/prompt/` | POST |
| Projects | `/api/projects/` | GET/POST |
| History | `/api/history/` | GET |
| Users | `/api/users/` | GET/POST |
| Run Code | `/api/run/` | POST |
| AI Chat | `/api/chat/` | POST |

---

# 🧠 AI Workflow

CreatCode follows this basic workflow:

```text
User Requirement
       ↓
Prompt Input
       ↓
FastAPI Backend
       ↓
AI Service
       ↓
OpenRouter
       ↓
AI Generated Response
       ↓
Frontend Editor
       ↓
Project History
```

---

# 🗄️ Database

CreatCode stores application data in MySQL.

Main entities include:

```text
Users
Projects
Code Generations
```

Generated code can be associated with a project and retrieved through the history system.

---

# 🔐 Security Notes

The current project is intended primarily for development and portfolio demonstration.

Important production improvements should include:

- Authentication and authorization
- Strong API validation
- Rate limiting
- Secure secret management
- Sandboxed multi-language code execution
- Resource limits
- HTTPS
- Production database credentials
- CORS restriction
- Logging and monitoring

Never expose API keys in frontend JavaScript or commit `.env` files.

---

# ♿ Accessibility

CreatCode includes accessibility-focused improvements such as:

- Keyboard navigation
- Visible focus indicators
- ARIA labels
- Live status announcements
- Reduced-motion support
- Accessible dialogs
- Improved mobile controls

---

# 📱 Responsive Design

The interface is designed for:

- Desktop
- Laptop
- Tablet
- Mobile screens

The developer workspace adapts to smaller screen sizes while keeping the core coding workflow accessible.

---

# 🧪 Current Development Status

| Feature | Status |
|---|---|
| FastAPI Backend | ✅ |
| MySQL Database | ✅ |
| OpenRouter AI | ✅ |
| Code Generation | ✅ |
| Code Explanation | ✅ |
| Debugging | ✅ |
| Optimization | ✅ |
| Complexity Analysis | ✅ |
| Test Case Generation | ✅ |
| Code Conversion | ✅ |
| AI Chat | ✅ |
| Projects | ✅ |
| History | ✅ |
| Python Execution | ✅ |
| Multi-language Execution | ⏳ |
| Authentication | ⏳ |
| Production Deployment | ⏳ |

---

# 🚀 Future Improvements

Planned improvements include:

- User authentication
- GitHub OAuth
- Cloud deployment
- Secure sandboxed code execution
- More programming languages
- Project sharing
- AI coding history
- Advanced code analysis
- Usage limits and rate limiting
- Developer analytics

---

# 👨‍💻 Author

**Aryan**

Computer Engineering Student

GitHub:

https://github.com/aryan1704-ai

---

# 📄 License

This project is currently available for educational and portfolio purposes.

A formal open-source license can be added later.