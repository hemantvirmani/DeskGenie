# DeskGenie High-Level Architecture Diagram

## System Overview

DeskGenie is an AI-powered desktop agent that enables users to perform file operations, document manipulation, and media processing through natural language commands.

## High-Level Architecture

```mermaid
graph TB
    User[User]
    
    subgraph "Frontend Layer"
        WebUI[Web UI<br/>React + Tailwind CSS]
        CLI[CLI Interface]
    end
    
    subgraph "Backend Layer"
        API[FastAPI REST API]
        MainApp[Main Application]
    end
    
    subgraph "AI Agent Layer"
        Agent[AI Agent<br/>LangGraph + Gemini LLM]
        ToolRegistry[Tool Registry]
    end
    
    subgraph "Tools Layer"
        PDFTools[PDF Operations]
        ImageTools[Image Processing]
        FileTools[File Management]
        MediaTools[Video/Audio Processing]
        WebTools[Web Search & Research]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini API]
        FFmpeg[FFmpeg Media Engine]
        Tesseract[Tesseract OCR]
        WebAPIs[Web APIs<br/>Wikipedia, ArXiv, etc.]
    end
    
    subgraph "Storage"
        FileSystem[Local File System]
        OutputDir[Output Directory]
        DataFiles[Questions & Metadata]
    end
    
    User --> WebUI
    User --> CLI
    WebUI --> API
    CLI --> MainApp
    API --> MainApp
    MainApp --> Agent
    Agent --> ToolRegistry
    ToolRegistry --> PDFTools
    ToolRegistry --> ImageTools
    ToolRegistry --> FileTools
    ToolRegistry --> MediaTools
    ToolRegistry --> WebTools
    Agent --> Gemini
    PDFTools --> FFmpeg
    MediaTools --> FFmpeg
    PDFTools --> Tesseract
    WebTools --> WebAPIs
    PDFTools --> FileSystem
    ImageTools --> FileSystem
    FileTools --> FileSystem
    MediaTools --> FileSystem
    PDFTools --> OutputDir
    ImageTools --> OutputDir
    FileTools --> OutputDir
    MediaTools --> OutputDir
    Agent --> DataFiles
    
    style User fill:#e1f5fe,stroke:#01579b
    style WebUI fill:#f3e5f5,stroke:#4a148c
    style CLI fill:#f3e5f5,stroke:#4a148c
    style API fill:#e8f5e8,stroke:#1b5e20
    style MainApp fill:#e8f5e8,stroke:#1b5e20
    style Agent fill:#fff3e0,stroke:#e65100
    style ToolRegistry fill:#fff3e0,stroke:#e65100
    style PDFTools fill:#fce4ec,stroke:#880e4f
    style ImageTools fill:#fce4ec,stroke:#880e4f
    style FileTools fill:#fce4ec,stroke:#880e4f
    style MediaTools fill:#fce4ec,stroke:#880e4f
    style WebTools fill:#fce4ec,stroke:#880e4f
    style Gemini fill:#fff8e1,stroke:#f57f17
    style FFmpeg fill:#fff8e1,stroke:#f57f17
    style Tesseract fill:#fff8e1,stroke:#f57f17
    style WebAPIs fill:#fff8e1,stroke:#f57f17
    style FileSystem fill:#f1f8e9,stroke:#33691e
    style OutputDir fill:#f1f8e9,stroke:#33691e
    style DataFiles fill:#f1f8e9,stroke:#33691e
```

## Component Descriptions

### Frontend Layer
- **Web UI**: React-based web interface for interactive chat with the AI agent
- **CLI Interface**: Command-line interface for direct interaction and batch processing

### Backend Layer
- **FastAPI REST API**: Handles HTTP requests from web UI, manages task execution
- **Main Application**: Orchestrates the overall application flow and configuration

### AI Agent Layer
- **AI Agent**: LangGraph-based agent powered by Google Gemini LLM for natural language understanding and reasoning
- **Tool Registry**: Manages and provides access to all available tools

### Tools Layer
- **PDF Operations**: Extract, delete, merge, split PDFs and convert to images
- **Image Processing**: Convert formats (HEIC, PNG, JPG, etc.), resize, compress images
- **File Management**: Batch rename, organize files, find duplicates
- **Video/Audio Processing**: Extract audio, compress video, get media info
- **Web Search & Research**: Web search, Wikipedia, ArXiv, YouTube analysis

### External Services
- **Google Gemini API**: Primary LLM provider for natural language processing
- **FFmpeg Media Engine**: Handles video and audio processing
- **Tesseract OCR**: Optical character recognition for text extraction from images
- **Web APIs**: External APIs for web search and knowledge retrieval

### Storage
- **Local File System**: Direct access to user's files and directories
- **Output Directory**: Default location for generated files (~/Desktop_Agent_Output)
- **Questions & Metadata**: Benchmark questions and execution metadata

## Data Flow

1. **User Request**: User sends command via Web UI or CLI
2. **API Processing**: Backend receives and validates the request
3. **Agent Execution**: AI agent analyzes the request and plans tool usage
4. **Tool Execution**: Agent executes appropriate tools to perform the task
5. **File Operations**: Tools interact with file system and external services
6. **Result Return**: Formatted results are returned to user with logging

## Key Capabilities

- **Natural Language Interface**: Understand and execute natural language commands
- **Multi-Format Support**: Handle PDFs, images, videos, documents, and more
- **Desktop Integration**: Direct access to local file system
- **Extensible Architecture**: Easy to add new tools and capabilities
- **Real-Time Feedback**: Live log streaming for operation monitoring
- **Benchmark Testing**: Built-in GAIA benchmark support for evaluation

## Technology Stack

- **Frontend**: React, Tailwind CSS, Vite
- **Backend**: FastAPI, Python 3.10+
- **AI**: LangGraph, Google Gemini API
- **Media**: FFmpeg, Pillow, Tesseract OCR
- **Development**: Python, Node.js