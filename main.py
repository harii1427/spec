from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageFilter
import io
from gtts import gTTS
from deep_translator import GoogleTranslator

app = FastAPI()

# Mount the static files directory for serving HTML and CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("index.html") as f:
        return f.read()

@app.post("/process-input/")
async def process_input(
    file_image: UploadFile = File(...),
    file_audio: UploadFile = File(...),
    text_input: str = Form(...)
):
    # Process image
    image = Image.open(file_image.file)
    blurred_image = image.filter(ImageFilter.GaussianBlur(5))
    img_byte_arr = io.BytesIO()
    blurred_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Save the blurred image
    image_path = "static/blurred_image.png"  # Adjust your path accordingly
    with open(image_path, 'wb') as f:
        f.write(img_byte_arr.getvalue())

    # Save the audio file
    audio_path = f"static/{file_audio.filename}"
    with open(audio_path, 'wb') as f:
        f.write(await file_audio.read())

    # Translate the text to Tamil using deep-translator
    translated_text = GoogleTranslator(source='auto', target='ta').translate(text_input)

    # Convert translated text to audio
    tts = gTTS(text=translated_text, lang='ta')
    audio_output_path = "static/translated_audio.wav"
    tts.save(audio_output_path)

    return JSONResponse(content={
        "image_url": f"/static/blurred_image.png",
        "translated_text": translated_text,
        "audio_url": f"/static/translated_audio.wav",  # Updated to match the JavaScript
    })

# Ensure to run your FastAPI app with uvicorn
# Command to run: uvicorn main:app --reload
