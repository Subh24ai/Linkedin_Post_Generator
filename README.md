# LinkedIn Post Generator 💼

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.20+-red)
![LangChain](https://img.shields.io/badge/langchain-0.1.0+-green)

**Generate professional, engaging LinkedIn posts with the power of AI**

[Features](#key-features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [Contributing](#contributing)

![LinkedIn Post Generator Demo](https://via.placeholder.com/800x400?text=LinkedIn+Post+Generator)

</div>

## 🚀 Overview

LinkedIn Post Generator is an AI-powered tool that creates tailored, professional social media content in seconds. Leveraging the LLama 3.2 90B Vision model through Groq API, the application produces high-quality posts customized to your specific industry, tone preferences, and language requirements.

## ✨ Key Features

### Content Creation
- **🎯 Industry-Specific Topics** - Generate relevant content across professional categories (Leadership, Career Advice, Job Search, etc.)
- **🌎 Multiple Languages** - Create posts in English, Hindi, Hinglish, and Spanish
- **🎭 Tone Customization** - Choose from Professional, Casual, Motivational, Informative, or Story-based styles
- **📏 Flexible Length** - Select Short (1-5 lines), Medium (6-10 lines), or Long (11-15 lines) formats

### Smart Technology
- **🧠 Few-Shot Learning** - Learns from successful examples to improve output quality
- **🏷️ Intelligent Tagging** - Automatically categorizes and standardizes content topics
- **📊 Performance Analysis** - Tracks content metrics to continuously improve generation

### User Experience
- **🖱️ One-Click Generation** - Create professional content with minimal effort
- **📜 Post History** - Access and reuse your previously generated content
- **📋 Easy Export** - Download or copy posts with a single click
- **✏️ Custom Instructions** - Fine-tune generation with specific requirements

## 📥 Installation

### Prerequisites
- Python 3.8+
- Groq API key

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/linkedin-post-generator.git
cd linkedin-post-generator

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GROQ_API_KEY=your_api_key_here" > .env
```

## 🖥️ Usage

### Running the Application

```bash
streamlit run app.py
```

### Generating a Post

1. **Configure your post**:
   - Select a topic from the dropdown
   - Choose your preferred length, language, and tone
   - Add custom instructions if needed

2. **Generate content**:
   - Click the "Generate Post" button
   - Review the generated content

3. **Export your post**:
   - Download as a text file
   - Copy directly to clipboard
   - Generate variations as needed

## 🏗️ Architecture

The application follows a modular design with five main components:

```
├── app.py                # Streamlit web interface
├── llm_helper.py         # LLM API integration 
├── post_generator.py     # Post creation engine
├── preprocess.py         # Data analysis tools
├── data/
│   ├── few_shot.py       # Example management
│   ├── processed_posts.json  # Training data
│   └── history/          # User generation history
```

### Component Overview:

- **LLM Integration** - Manages communication with Groq API
- **Few-Shot Learning** - Handles example management and retrieval
- **Post Generation** - Creates optimized prompts and processes responses
- **Preprocessing** - Analyzes and categorizes content for better examples
- **Web Interface** - Provides the user-facing application

## 🛠️ Advanced Customization

Power users can modify:

- **Model Parameters** - Adjust temperature and token settings
- **Default Preferences** - Set preferred topics, languages, and tones
- **Custom Topics** - Add specialized industry categories

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/), and [Groq API](https://groq.com/)
- Powered by LLama 3.2 90B Vision model
- Inspired by the need for quality professional content on LinkedIn
