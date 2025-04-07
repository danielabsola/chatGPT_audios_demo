# ChatGPT Audio Chat Application

This project demonstrates the integration of OpenAI's ChatGPT API with AWS Transcribe and S3 services to create an audio-based chat application. The application allows users to send audio messages, which are transcribed using AWS Transcribe, processed by ChatGPT, and returned as both text and audio responses.

## Features

- Audio file processing and transcription using AWS Transcribe
- Natural language processing using OpenAI's ChatGPT
- Text-to-speech conversion for responses
- RESTful API endpoints for audio processing and chat

## Prerequisites

- Python 3.7+
- AWS Account with Transcribe and S3 access
- OpenAI API key
- AWS Access Key and Secret Key

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your credentials:
```
OPENAI_API_KEY=your_openai_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=eu-west-2
S3_BUCKET_NAME=your_s3_bucket_name
S3_OUTPUT_BUCKET=your_output_bucket_name
```

## Usage

1. Start the Flask application:
```bash
python chat.py
```

2. The application will be available at `http://localhost:5000`

## API Endpoints

- `POST /audio`: Accepts audio files for transcription
- `POST /chat`: Processes transcribed text and returns ChatGPT response
