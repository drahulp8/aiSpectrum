# AI Spectrum

AI Spectrum is a web application that allows users to compare responses from multiple AI models side by side. Users can input their API keys for OpenAI, Anthropic, and DeepSeek models, send a single query, and view all responses simultaneously.

## Features

- **API Key Management:** Securely enter and save API keys for different AI providers
- **Model Selection:** Choose specific model versions for each provider
- **Side-by-Side Comparison:** View responses from all models in a three-column layout
- **Markdown Rendering:** Properly formats AI responses with markdown support
- **Responsive Design:** Works on both desktop and mobile devices

## Setup Instructions

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aiSpectrum.git
   cd aiSpectrum
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

1. Enter your API keys for the AI models you want to use (OpenAI, Anthropic, DeepSeek)
2. Select the desired model version for each provider
3. Type your query in the input field
4. Click "Send to All Models"
5. View the responses side by side

## API Keys

You'll need to obtain API keys from the following providers:

- OpenAI: https://platform.openai.com/
- Anthropic: https://console.anthropic.com/
- DeepSeek: https://platform.deepseek.ai/ (Uses REST API directly)

API keys are stored locally in your browser's localStorage and are never sent to any server other than the respective AI providers.

## Security Note

This application sends your API keys directly to the respective AI providers' APIs. No keys are stored on any server, only in your browser's localStorage for convenience. Always be cautious about where you enter your API keys.

## License

MIT License