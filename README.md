# AI-Powered Idea Generator

An AI-powered idea and title generator using Flask, Vanilla JS, and GPT-4 models with continuous generation and user feedback.

## Features

- Generate creative titles and ideas based on user input
- Categorize generated content as normal, edgy, or ultra new
- User account system for saving and managing multiple idea sessions
- Export functionality for generated ideas and titles
- Visual mind-map feature for exploring idea relationships
- Support for multiple AI models (gpt-4o-mini-2024-07-18 and gpt-4o)

## Prerequisites

- Python 3.7+
- Flask
- SQLAlchemy
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-powered-idea-generator.git
   cd ai-powered-idea-generator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

1. Start the Flask server:
   ```
   python main.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Register for an account or log in if you already have one

4. Enter an initial title and idea, then click "Generate" to start creating content

5. Use the feedback buttons to like or dislike generated ideas

6. Create relationships between ideas by clicking on them in the mind map

7. Export your idea session as a CSV file for further analysis

## Project Structure

- `main.py`: Main Flask application
- `models.py`: Database models
- `utils/ai_generator.py`: AI content generation logic
- `static/`: CSS and JavaScript files
- `templates/`: HTML templates
- `openai_chat_completion/`: OpenAI API integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
