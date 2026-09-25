# 🤖 Multi-Agent Research System

> An AI-powered multi-agent research system that searches the web, reads useful sources, generates a structured report, and reviews the final result.

The **Multi-Agent Research System** is a Python-based AI application designed to automate the research process using specialized agents. Each stage handles a specific task, from web search and content extraction to report generation and quality review.

---

## ✨ Features

* 🔎 Web search for relevant research sources
* 📖 Web content extraction and processing
* 🤖 Specialized AI agents for different research tasks
* ✍️ Automated structured report generation
* 🧐 AI-powered report review and feedback
* 🌐 Streamlit-based web interface
* 🔐 Environment-based API key management
* 📚 Source information included with the research output

---

## 🧠 System Architecture

```text
                    Research Topic
                          │
                          ▼
                  ┌───────────────┐
                  │ Search Agent  │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Reader Agent  │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Writer Agent  │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Critic Agent  │
                  └───────┬───────┘
                          │
                          ▼
                   Research Report
```

### Agent Responsibilities

| Agent               | Responsibility                                      |
| ------------------- | --------------------------------------------------- |
| 🔎 **Search Agent** | Searches the web and identifies relevant sources    |
| 📖 **Reader Agent** | Extracts useful information from selected web pages |
| ✍️ **Writer Agent** | Generates a structured research report              |
| 🧐 **Critic Agent** | Reviews the report and provides quality feedback    |

---

## 🛠️ Tools & Technologies

| Tool / Technology | Purpose                                     |
| ----------------- | ------------------------------------------- |
| **Python**        | Core programming language                   |
| **LangChain**     | AI agent and LLM application framework      |
| **Google Gemini** | Large language model used for AI processing |
| **Tavily**        | Web search and research source discovery    |
| **BeautifulSoup** | HTML parsing and web content extraction     |
| **Requests**      | HTTP requests for retrieving web pages      |
| **Streamlit**     | Web-based user interface                    |
| **python-dotenv** | Environment variable and API key management |

---

## 📁 Project Structure

```text
multi-agent-research-system/
│
├── app.py                # Streamlit application
├── agents.py             # AI agents and prompts
├── pipeline.py           # Research workflow
├── tools.py              # Search and web scraping tools
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── .env.example          # Environment variable template
└── .gitignore             # Git ignored files
```

---

## 🔄 How It Works

The application processes a research topic through four main stages:

### 1. Search

The Search Agent uses Tavily to find relevant web sources related to the research topic.

### 2. Read

The Reader Agent selects a useful source and extracts the relevant content from the web page.

### 3. Write

The Writer Agent combines the collected research information and generates a structured report containing key findings, conclusions, and sources.

### 4. Review

The Critic Agent evaluates the generated report and provides feedback on its strengths and areas for improvement.

---

## 🚀 Getting Started

### Prerequisites

### 1. Clone the repository

```bash
git clone https://github.com/armanans1/multi-agent-research-system.git
cd multi-agent-research-system
```

## 📊 Research Pipeline

The complete workflow can be summarized as:

```text
User Input
    │
    ▼
Web Search
    │
    ▼
Source Selection
    │
    ▼
Content Extraction
    │
    ▼
Report Generation
    │
    ▼
Report Review
    │
    ▼
Final Research Output
```

---

## 🔐 Environment Variables

| Variable         | Description                          |
| ---------------- | ------------------------------------ |
| `GOOGLE_API_KEY` | API key used to access Google Gemini |
| `TAVILY_API_KEY` | API key used for web search          |

API keys are loaded from the local `.env` file and are excluded from version control through `.gitignore`.

---

## 📌 Current Limitations

* The current pipeline processes a limited number of sources.
* Source selection can be further improved.
* Web scraping depends on the structure and accessibility of individual websites.
* AI-generated information should be verified against the original sources.

---

## 🚀 Future Improvements

* Multi-source research and comparison
* Improved source ranking and reliability detection
* Automated fact verification
* Enhanced citation management
* Parallel agent execution
* PDF and document research
* Research history and memory
* Downloadable research reports
* Improved error handling
* Cloud deployment
* User authentication

---

## 👨‍💻 Author

**Armaan Ansari**

GitHub: [@armanans1](https://github.com/armanans1)

---

## 📄 License

This project is intended for educational and development purposes.
