# VERSION 2:
import os
import uuid
import logging
from flask import Flask, request, jsonify
import requests
import boto3
from gtts import gTTS
from botocore.exceptions import BotoCoreError, ClientError
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure AWS
aws_region = os.getenv('AWS_REGION')
s3_bucket = os.getenv('S3_BUCKET_NAME')
s3_output_bucket = os.getenv('S3_OUTPUT_BUCKET')

# Initialize AWS clients
transcribe = boto3.client('transcribe', region_name=aws_region)

# Global variable to store transcription
transcripcion = ""

def text_to_speech(chat_response, lang="es"):
    """Convert text to speech and save as MP3 file."""
    try:
        tts = gTTS(text=chat_response, lang=lang)
        tts.save("audioChatResponse.mp3")
        logger.info("Text-to-speech conversion completed successfully")
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        raise

def generar_respuesta(prompt):
    """Generate response using OpenAI's ChatGPT."""
    try:
        respuesta = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5
        )
        messages = respuesta.choices[0].text.split("\n")
        ai_message = messages[0].replace("AI: ", "").strip()
        
        chat_response = {"response": ai_message}
        text_to_speech(chat_response['response'])
        return jsonify(chat_response)
    except Exception as e:
        logger.error(f"Error generating ChatGPT response: {str(e)}")
        return jsonify({"error": "Failed to generate response"}), 500

@app.route('/audio', methods=['POST'])
def handle_audio():
    """Handle audio file upload and transcription."""
    global transcripcion
    
    if 'audio' not in request.files:
        logger.error("No audio file found in request")
        return jsonify({"error": "No audio file provided"}), 400
        
    try:
        file = request.files['audio']
        filename = file.filename
        file.save(filename)
        logger.info(f"Audio file saved: {filename}")

        # Start transcription job
        job_name = str(uuid.uuid4())
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='es-US',
            MediaFormat='mp3',
            Media={
                'MediaFileUri': f's3://{s3_bucket}/{filename}'
            },
            OutputBucketName=s3_output_bucket
        )
        logger.info(f"Transcription job started: {job_name}")

        # Wait for transcription to complete
        while True:
            status = transcribe.get_transcription_job(
                TranscriptionJobName=job_name
            )
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            response_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            response = requests.get(response_uri).json()
            transcripcion = response['results']['transcripts'][0]['transcript']
            logger.info("Transcription completed successfully")
            return jsonify({"transcription": transcripcion}), 200
        else:
            logger.error("Transcription job failed")
            return jsonify({"error": "Transcription failed"}), 500

    except (BotoCoreError, ClientError) as e:
        logger.error(f"AWS error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Process transcribed text and return ChatGPT response."""
    global transcripcion
    try:
        prompt = f"Humano: {transcripcion}\nAI:"
        return generar_respuesta(prompt)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Failed to process chat request"}), 500

#https://openai.com/research/whisper

if __name__ == '__main__':
    app.run(debug=True)



# VERSION 1:
# from flask import Flask, request
# import uuid
# import requests
# import boto3
# from botocore.exceptions import BotoCoreError, ClientError
# import openai
# openai.api_key = "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"

# app = Flask(__name__)

# def generar_respuesta(prompt):
#     respuesta = openai.Completion.create(
#         engine="davinci", prompt=prompt, max_tokens=1024, n=1, stop=None, temperature=0.5
#     )
#     return respuesta.choices[0].text

# @app.route('/audio', methods=['POST'])
# def handle_audio():
#     if 'audio' not in request.files:
#         return 'No se encontró el archivo de audio', 400
        
#     file = request.files['audio']
#     filename = file.filename
#     file.save(filename)

#     transcribe = boto3.client('transcribe', region_name='eu-west-2')
    
#     try:
#         # Enviamos el archivo de audio a Amazon Transcribe para su transcripción
#         response = transcribe.start_transcription_job(
#             TranscriptionJobName='TranscriptionJobDemoV7',
#             LanguageCode='es-US',
#             MediaFormat='mp3',
#             Media={
#                 'MediaFileUri': f's3://demo-audio-eu-west-2-danielabsola-v2/{filename}'
#             },
#             OutputBucketName='response-audio-eu-west-2-danielabsola' # El nombre del bucket de S3 donde quieres almacenar el resultado de la transcripción
#         )

#         # Obtenemos el ID del trabajo de transcripción
#         job_name = response['TranscriptionJob']['TranscriptionJobName']
#         # job_name = f"transcription-{str(uuid.uuid4())}"

#         # Esperamos a que el trabajo de transcripción finalice
#         while True:
#             status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
#             if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
#                 break

#         # Obtenemos el resultado de la transcripción y lo devolvemos como respuesta a la solicitud
#         if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
#             response_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
#             response = requests.get(response_uri).json()
#             return generar_respuesta(response['results']['transcripts'][0]['transcript']), 200
#         else:
#             return 'Hubo un error al transcribir el archivo de audio', 500

#     except (BotoCoreError, ClientError) as e:
#         return str(e), 500



# # pregunta = "Hola, quiero una receta de una torta de chocolate"
# # chatGPT = generar_respuesta(HUMAN)
# # print("chatGPT: ", chatGPT)

# if __name__ == '__main__':
#     app.run(debug=True)