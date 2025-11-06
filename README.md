# UML Class Diagram Generator

An AI-powered hybrid system for generating accurate UML Class Diagrams from user requirements through automated NLP extraction and interactive refinement.

## 🚀 Features

### Stage 1: Automated NLP Extraction
- **BERT-based Entity Recognition**: Identifies candidate classes, attributes, and methods
- **spaCy Dependency Parsing**: Extracts relationships and system structure
- **Intelligent Text Processing**: Handles technical terms and software-specific patterns
- **Confidence Scoring**: Ranks extracted elements by likelihood

### Stage 2: Interactive Refinement
- **Conversational Interface**: Chat with an AI assistant to validate and refine diagrams
- **Visual Diagram Editing**: Real-time updates with Mermaid.js
- **Multiple Export Formats**: Mermaid, JSON, SVG, PNG
- **Relationship Validation**: AI-powered suggestions for relationship types

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │  Flask Backend  │    │  Rasa Chatbot   │
│                 │    │                 │    │                 │
│ • Requirement   │◄──►│ • NLP Pipeline  │◄──►│ • Conversation  │
│   Input         │    │ • BERT + spaCy  │    │   Management    │
│ • Diagram       │    │ • Mermaid Gen   │    │ • Diagram       │
│   Viewer        │    │ • REST API      │    │   Refinement    │
│ • Chat          │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (optional)
- 4GB+ RAM for NLP models

## 🛠️ Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd uml-generator

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# Chatbot: http://localhost:5005
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Set environment variables
export FLASK_ENV=development
export MODEL_PATH=./models/fine_tuned_bert

# Start the Flask server
python app.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

#### Rasa Chatbot Setup

```bash
cd backend/rasa_bot

# Install dependencies
pip install -r requirements.txt

# Train the model
rasa train

# Start the Rasa server
rasa run --enable-api --cors "*"
```

## 📖 Usage

### 1. Input Requirements
- Paste your software requirements in the text area
- Minimum 50 characters for meaningful analysis
- Maximum 10,000 characters

### 2. AI Processing
- BERT identifies classes, attributes, and methods
- spaCy extracts relationships between entities
- System generates initial UML diagram

### 3. Interactive Refinement
- Chat with AI assistant to validate relationships
- Add/remove classes, attributes, and methods
- Refine relationship types (composition, association, inheritance, aggregation)

### 4. Export
- **Mermaid**: Code for documentation tools
- **JSON**: Structured UML model data
- **SVG/PNG**: Visual diagram images

## 🎯 Example Requirements

### E-commerce System
```
Users can create accounts with username and password. Users have shopping carts that contain multiple products. Products have prices and descriptions. Orders are created from carts and contain order details. Users can add items to their cart and checkout to complete purchases.
```

### Education System
```
Students enroll in courses. Courses have instructors. Students submit assignments. Instructors grade assignments and provide feedback. Courses have schedules and prerequisites. Students can view their grades and academic progress.
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Flask environment |
| `PORT` | `5000` | Backend port |
| `MODEL_PATH` | `./models/fine_tuned_bert` | BERT model location |
| `RASA_ENDPOINT` | `http://localhost:5005` | Rasa server URL |
| `MAX_TEXT_LENGTH` | `10000` | Maximum input length |
| `MIN_TEXT_LENGTH` | `50` | Minimum input length |

### Model Configuration

The system uses:
- **BERT**: `bert-base-uncased` for entity recognition
- **spaCy**: `en_core_web_lg` for dependency parsing
- **Fine-tuning**: Can be trained on domain-specific software requirements

## 🧪 Testing

### Manual Testing Scenarios

1. **Basic E-commerce System**
   - Input: User-product-order requirements
   - Expected: 4+ classes, composition relationships

2. **Ambiguous Relationships**
   - Input: Student-course requirements
   - Expected: Chatbot asks about relationship types

3. **Technical Terms**
   - Input: REST API requirements
   - Expected: Proper technical term handling

4. **Long Documents**
   - Input: 5000+ character requirements
   - Expected: Text chunking and processing

### API Testing

```bash
# Health check
curl http://localhost:5000/health

# Extract UML from text
curl -X POST http://localhost:5000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Your requirements here..."}'

# Validate diagram
curl -X POST http://localhost:5000/api/diagram/validate \
  -H "Content-Type: application/json" \
  -d '{"uml_model": {...}}'
```

## 🚨 Troubleshooting

### Common Issues

1. **BERT Model Loading Error**
   - Solution: Ensure 4GB+ RAM available
   - Check internet connection for model download

2. **spaCy Model Missing**
   - Solution: Run `python -m spacy download en_core_web_lg`

3. **Chatbot Not Responding**
   - Solution: Check Rasa server status
   - Verify chatbot training completion

4. **Frontend Connection Error**
   - Solution: Check backend API is running
   - Verify CORS configuration

### Performance Optimization

- **Model Caching**: BERT model loaded once per session
- **Text Chunking**: Large documents processed in chunks
- **Lazy Loading**: Models loaded on first request
- **Rate Limiting**: Prevents API abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face**: BERT model implementation
- **spaCy**: Dependency parsing and NLP
- **Mermaid.js**: Diagram rendering
- **Rasa**: Conversational AI framework
- **React**: Frontend framework
- **Flask**: Backend API framework

## 📞 Support

For support, please:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information
4. Include requirements text and error messages

---

**Built with ❤️ using AI-powered Natural Language Processing**