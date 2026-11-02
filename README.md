# 🇮🇳 Nagrik: AI-Powered Civic Intelligence Platform

**Making civic information accessible, actionable, and conversational.**

Nagrik is an AI-powered civic technology platform designed to bridge the gap between citizens and public information. It leverages intelligent information retrieval and conversational AI to help users access relevant civic knowledge through an intuitive web interface and WhatsApp chatbot.

By combining modern backend architecture, AI-driven retrieval, and conversational interfaces, Nagrik aims to make navigating civic information simpler and more accessible.

---

## ✨ Key Features

- **AI-Powered Civic Intelligence:** Uses GraphRAG-based retrieval to understand contextual relationships and deliver relevant civic information.
- **WhatsApp Chatbot Integration:** Enables citizens to interact with the platform through a familiar messaging interface.
- **Contextual Information Retrieval:** Retrieves relevant information based on user queries and contextual relationships.
- **REST API Backend:** Built with FastAPI for efficient API development and service integration.
- **Database Integration:** MongoDB-powered data management for flexible and scalable storage.
- **Interactive Web Interface:** Provides a dedicated frontend for accessing platform functionality.

## 🏗️ System Architecture

Nagrik follows a modular architecture comprising three primary components:

| Component | Responsibility |
|---|---|
| Frontend | User interaction and web interface |
| Backend | API orchestration, application logic and database operations |
| AI Layer | GraphRAG-powered contextual retrieval and intelligent responses |
| WhatsApp Integration | Conversational access through WhatsApp |

## 🛠️ Technology Stack

**Backend**
- Python
- FastAPI
- MongoDB

**Artificial Intelligence**
- Retrieval-Augmented Generation (RAG)
- GraphRAG
- Large Language Models (LLMs)

**Frontend**
- JavaScript
- TypeScript
- CSS

**Integrations**
- WhatsApp Business API

## 📁 Repository Structure

```text
Nagrik/
│
├── backend/
│   ├── API services
│   ├── AI and retrieval components
│   └── WhatsApp integration
│
├── frontend/
│   └── nexcholar/
│       └── Web application
│
├── pyproject.toml
├── .python-version
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js and npm
- MongoDB instance
- Required AI/LLM API credentials
- WhatsApp Business API credentials (for chatbot integration)

### 1. Clone the Repository

```bash
git clone https://github.com/Epic021/Nagrik.git
cd Nagrik
```

### 2. Backend Setup

```bash
cd backend
```

Install the dependencies according to the project's Python configuration.

Configure the required environment variables in a `.env` file.

Example configuration:

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=nagrik
LLM_API_KEY=your_api_key
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

Start the FastAPI server using the project's application entry point:

```bash
uvicorn <app_module>:app --reload
```

Once running, access the interactive API documentation at:

`http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend/nexcholar
npm install
npm run dev
```

Follow the frontend configuration for any additional environment variables.

## 🔮 Vision

Nagrik aims to make civic knowledge more accessible by transforming complex public information into understandable, conversational experiences.

The long-term vision is to build an intelligent civic ecosystem where citizens can discover information, understand public services, and interact with civic resources through AI-powered interfaces.

## 🤝 Contributing

Contributions, feature requests, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

## 📄 License

Add the appropriate license information before distributing or modifying this project.

---

<p align="center">
  <b>Nagrik: Technology for a More Informed Citizenry.</b>
</p>
