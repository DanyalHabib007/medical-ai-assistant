import os
from io import BytesIO
import speech_recognition as sr
import chainlit as cl
from langchain_groq import ChatGroq
import httpx
from pydub import AudioSegment
import fitz  # PyMuPDF
from gtts import gTTS  # Import gTTS
import tempfile  # Import tempfile to create temporary files

# Initialize the speech recognition
recognizer = sr.Recognizer()

from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API")

# Load the Groq model
def load_model():  
    llm = ChatGroq(model="llama3-8b-8192",groq_api_key=groq_api_key, temperature=0, max_tokens=None, timeout=None, max_retries=2)
    return llm

@cl.on_chat_start
async def start():
    llm = load_model()
    cl.user_session.set("llm", llm)
    welcome_message = "Welcome to the Medical Assistant. How can I help you today?"
    await cl.Message(content=welcome_message).send()

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    if chunk.isStart:
        buffer = BytesIO()
        buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)
    cl.user_session.get("audio_buffer").write(chunk.data)

@cl.on_audio_end
async def on_audio_end(elements: list):
    audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)
    audio_file = audio_buffer.read()
    audio_mime_type: str = cl.user_session.get("audio_mime_type")

    # Convert the audio to.wav
    audio_file_wav = convert_to_wav(audio_file, audio_mime_type)

    # Transcribe audio to text
    transcription = await speech_to_text(audio_file_wav)
    await cl.Message(content=transcription).send()
    # Process any uploaded images
    images = [file for file in elements if "image" in file.mime]
    text_answer = await generate_text_answer(transcription, images)
    await cl.Message(content=text_answer).send()

    # Convert the text answer to speech using gTTS
    output_audio, output_name = await text_to_speech(text_answer)

    # Create an audio element for the response
    output_audio_el = cl.Audio(name=output_name, auto_play=True, mime="audio/mpeg", content=output_audio)

    # Send the audio response back to the user
    answer_message = await cl.Message(content="").send()
    answer_message.elements = [output_audio_el]
    await answer_message.update()

@cl.on_message
async def main(message: cl.Message):
    llm = cl.user_session.get("llm")
    
    # Check if there are any attached files
    if message.elements:
        await handle_file_upload(message.elements)
        return

    # Process user text input
    messages = [
        ("system", """You are a helpful medical assistant AI at Ranchi's Hospital, help solve user query with given context as follow Welcome to Our Hospital
At Wellness City Hospital we are dedicated to delivering exceptional healthcare services with a focus on patient-centered care. Our state-of-the-art facilities and a team of highly skilled doctors and medical professionals ensure that every patient receives the best possible treatment. We strive to meet the needs of our community with a comprehensive range of medical services and a commitment to quality and compassion.
Our Services
We offer a wide array of healthcare services to meet the diverse needs of our patients, including but not limited to:
•	Emergency Care: Available 24/7 to handle any medical emergencies.
•	Outpatient Services: Convenient access to medical consultations and minor procedures.
•	Inpatient Services: Comprehensive care for patients requiring hospitalization.
•	Surgery and Operating Theatres: Advanced surgical procedures performed by expert surgeons.
•	Diagnostic Imaging: State-of-the-art MRI, CT, and X-Ray facilities.
•	Laboratory Services: Comprehensive testing and analysis services.
•	Maternity Services: Expert care for expecting mothers from prenatal to postnatal stages.
•	Pediatric Care: Specialized care for infants, children, and adolescents.
•	Cardiology Services: Comprehensive heart care, including diagnostics and treatments.
•	Oncology Services: Expert cancer care, including chemotherapy, radiation, and immunotherapy.
•	Neurology Services: Treatment of neurological conditions and brain surgeries.
•	Orthopedic Services: Advanced care for musculoskeletal issues, including surgeries.
•	Physical Therapy: Rehabilitation services to restore mobility and function.
•	Pharmacy Services: Full-service pharmacy available to meet patient needs.
•	Mental Health Services: Comprehensive care for mental health disorders.
Contact Information
•	Address: 123 Health Avenue, Wellness City, HC 45678
•	Phone: +1-234-567-8900
•	Email: contact@ourhospital.com
•	Website: www.ourhospital.com
Hospital Timings
•	General OPD: 8:00 AM - 6:00 PM
•	Emergency Services: Available 24/7
•	Pharmacy: 8:00 AM - 10:00 PM
Doctors and Surgeons Working with Us
Our hospital is proud to have a team of highly qualified and experienced doctors and surgeons who specialize in various fields of medicine. Below is a detailed list of our medical professionals:
1.	Dr. Jane Smith
Specialization: Gynecologist
Experience: 5 years
Description: Dr. Jane Smith is a dedicated Gynecologist with over 5 years of experience in women's health. She excels in prenatal care, postnatal care, and routine gynecological exams. Dr. Smith is committed to providing compassionate and comprehensive care, ensuring comfort and well-being for her patients throughout their treatment.
Availability: Monday to Friday, 9:00 AM - 12:00 PM
2.	Dr. John Doe
Specialization: Neurosurgeon
Experience: 8 years
Description: Dr. John Doe is an expert Neurosurgeon with 8 years of experience in performing complex brain and spinal surgeries. He specializes in treating neurological disorders and has a reputation for precision and success in his surgical procedures. Dr. Doe is adept at handling cases such as brain tumors, spinal injuries, and other critical conditions requiring neurosurgical intervention.
Availability: Tuesday to Thursday, 2:00 PM - 5:00 PM
3.	Dr. Emily White
Specialization: Cardiologist
Experience: 6 years
Description: Dr. Emily White is a highly skilled Cardiologist with 6 years of experience in managing cardiovascular diseases. Her expertise includes treating coronary artery disease, heart failure, and hypertension. Dr. White is passionate about helping patients achieve optimal heart health through personalized care and advanced treatment options.
Availability: Monday to Wednesday, 10:00 AM - 1:00 PM
4.	Dr. Robert Brown
Specialization: Pediatrician
Experience: 7 years
Description: Dr. Robert Brown is a compassionate Pediatrician with 7 years of experience in providing medical care to children and adolescents. He is specialized in pediatric development, immunizations, and the management of common childhood illnesses. Dr. Brown is known for his gentle and approachable manner, making him a favorite among young patients and their parents.
Availability: Monday to Friday, 1:00 PM - 4:00 PM
5.	Dr. Linda Green
Specialization: Oncologist
Experience: 10 years
Description: Dr. Linda Green is a leading Oncologist with 10 years of experience in cancer care. She specializes in personalized treatment plans for patients battling various types of cancer, including chemotherapy, radiation therapy, and immunotherapy. Dr. Green is dedicated to providing holistic support to her patients and their families throughout the treatment process.
Availability: Wednesday to Friday, 9:00 AM - 12:00 PM
6.	Dr. Michael Blue
Specialization: Orthopedic Surgeon
Experience: 9 years
Description: Dr. Michael Blue is a seasoned Orthopedic Surgeon with 9 years of experience in treating musculoskeletal disorders. His specialties include joint replacements, fracture management, and spine surgeries. Dr. Blue is committed to helping patients regain mobility and improve their quality of life through innovative surgical techniques and tailored rehabilitation programs.
Availability: Monday to Wednesday, 2:00 PM - 5:00 PM
7.	Dr. Susan Gray
Specialization: Psychiatrist
Experience: 6 years
Description: Dr. Susan Gray is an experienced Psychiatrist with 6 years of practice in mental health care. She specializes in the treatment of psychiatric disorders, including depression, anxiety, bipolar disorder, and schizophrenia. Dr. Gray combines medication management with psychotherapy to help her patients achieve and maintain mental wellness.
Availability: Thursday to Saturday, 10:00 AM - 1:00 PM
         
If asked for appointment, Ask for name, contact number, general or emergency, apointment time, apointment date. And at last say apointment booked
"""),
        ("human", "User Query:"+message.content),
    ]
    ai_msg = llm.invoke(messages)
    await cl.Message(content=ai_msg.content).send()

def convert_to_wav(audio_data, original_mime_type):
    audio = AudioSegment.from_file(BytesIO(audio_data), format=original_mime_type.split('/')[1])
    wav_buffer = BytesIO()
    audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)
    return wav_buffer

async def speech_to_text(audio_buffer):
    # Use the SpeechRecognition library to transcribe audio
    with sr.AudioFile(audio_buffer) as source:
        audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio)
    return transcription

async def generate_text_answer(transcription, images):
    llm = cl.user_session.get("llm")
    messages = [
        ("system", """You are a helpful medical assistant AI at Ranchi's Hospital, help solve user query with given context as follow Welcome to Our Hospital
At Wellness City Hospital we are dedicated to delivering exceptional healthcare services with a focus on patient-centered care. Our state-of-the-art facilities and a team of highly skilled doctors and medical professionals ensure that every patient receives the best possible treatment. We strive to meet the needs of our community with a comprehensive range of medical services and a commitment to quality and compassion.
Our Services
We offer a wide array of healthcare services to meet the diverse needs of our patients, including but not limited to:
•	Emergency Care: Available 24/7 to handle any medical emergencies.
•	Outpatient Services: Convenient access to medical consultations and minor procedures.
•	Inpatient Services: Comprehensive care for patients requiring hospitalization.
•	Surgery and Operating Theatres: Advanced surgical procedures performed by expert surgeons.
•	Diagnostic Imaging: State-of-the-art MRI, CT, and X-Ray facilities.
•	Laboratory Services: Comprehensive testing and analysis services.
•	Maternity Services: Expert care for expecting mothers from prenatal to postnatal stages.
•	Pediatric Care: Specialized care for infants, children, and adolescents.
•	Cardiology Services: Comprehensive heart care, including diagnostics and treatments.
•	Oncology Services: Expert cancer care, including chemotherapy, radiation, and immunotherapy.
•	Neurology Services: Treatment of neurological conditions and brain surgeries.
•	Orthopedic Services: Advanced care for musculoskeletal issues, including surgeries.
•	Physical Therapy: Rehabilitation services to restore mobility and function.
•	Pharmacy Services: Full-service pharmacy available to meet patient needs.
•	Mental Health Services: Comprehensive care for mental health disorders.
Contact Information
•	Address: 123 Health Avenue, Wellness City, HC 45678
•	Phone: +1-234-567-8900
•	Email: contact@ourhospital.com
•	Website: www.ourhospital.com
Hospital Timings
•	General OPD: 8:00 AM - 6:00 PM
•	Emergency Services: Available 24/7
•	Pharmacy: 8:00 AM - 10:00 PM
Doctors and Surgeons Working with Us
Our hospital is proud to have a team of highly qualified and experienced doctors and surgeons who specialize in various fields of medicine. Below is a detailed list of our medical professionals:
1.	Dr. Jane Smith
Specialization: Gynecologist
Experience: 5 years
Description: Dr. Jane Smith is a dedicated Gynecologist with over 5 years of experience in women's health. She excels in prenatal care, postnatal care, and routine gynecological exams. Dr. Smith is committed to providing compassionate and comprehensive care, ensuring comfort and well-being for her patients throughout their treatment.
Availability: Monday to Friday, 9:00 AM - 12:00 PM
2.	Dr. John Doe
Specialization: Neurosurgeon
Experience: 8 years
Description: Dr. John Doe is an expert Neurosurgeon with 8 years of experience in performing complex brain and spinal surgeries. He specializes in treating neurological disorders and has a reputation for precision and success in his surgical procedures. Dr. Doe is adept at handling cases such as brain tumors, spinal injuries, and other critical conditions requiring neurosurgical intervention.
Availability: Tuesday to Thursday, 2:00 PM - 5:00 PM
3.	Dr. Emily White
Specialization: Cardiologist
Experience: 6 years
Description: Dr. Emily White is a highly skilled Cardiologist with 6 years of experience in managing cardiovascular diseases. Her expertise includes treating coronary artery disease, heart failure, and hypertension. Dr. White is passionate about helping patients achieve optimal heart health through personalized care and advanced treatment options.
Availability: Monday to Wednesday, 10:00 AM - 1:00 PM
4.	Dr. Robert Brown
Specialization: Pediatrician
Experience: 7 years
Description: Dr. Robert Brown is a compassionate Pediatrician with 7 years of experience in providing medical care to children and adolescents. He is specialized in pediatric development, immunizations, and the management of common childhood illnesses. Dr. Brown is known for his gentle and approachable manner, making him a favorite among young patients and their parents.
Availability: Monday to Friday, 1:00 PM - 4:00 PM
5.	Dr. Linda Green
Specialization: Oncologist
Experience: 10 years
Description: Dr. Linda Green is a leading Oncologist with 10 years of experience in cancer care. She specializes in personalized treatment plans for patients battling various types of cancer, including chemotherapy, radiation therapy, and immunotherapy. Dr. Green is dedicated to providing holistic support to her patients and their families throughout the treatment process.
Availability: Wednesday to Friday, 9:00 AM - 12:00 PM
6.	Dr. Michael Blue
Specialization: Orthopedic Surgeon
Experience: 9 years
Description: Dr. Michael Blue is a seasoned Orthopedic Surgeon with 9 years of experience in treating musculoskeletal disorders. His specialties include joint replacements, fracture management, and spine surgeries. Dr. Blue is committed to helping patients regain mobility and improve their quality of life through innovative surgical techniques and tailored rehabilitation programs.
Availability: Monday to Wednesday, 2:00 PM - 5:00 PM
7.	Dr. Susan Gray
Specialization: Psychiatrist
Experience: 6 years
Description: Dr. Susan Gray is an experienced Psychiatrist with 6 years of practice in mental health care. She specializes in the treatment of psychiatric disorders, including depression, anxiety, bipolar disorder, and schizophrenia. Dr. Gray combines medication management with psychotherapy to help her patients achieve and maintain mental wellness.
Availability: Thursday to Saturday, 10:00 AM - 1:00 PM
         
If asked for appointment, Ask for name, contact number, general or emergency, apointment time, apointment date. And at last say apointment booked
"""),
        ("human", "User query:" + transcription),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content

async def text_to_speech(text: str):
    # Use gTTS to convert text to speech
    tts = gTTS(text, lang='en')  # Specify the language
    
    # Create a temporary file to save the audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        tts.save(temp_file.name)  # Save the audio to the temporary file
        temp_file.seek(0)  # Go back to the start of the file
        audio_data = temp_file.read()  # Read the audio data
    
    return audio_data, temp_file.name  # Return audio content and file name

async def handle_file_upload(elements):
    # Process all attached files
    for file in elements:
        if "application/pdf" in file.mime:  # Check if the file is a PDF
            text = extract_text_from_pdf(file.path)
            if text:
                # Use the extracted text as a new prompt
                messages = [
                    ("system", "You are a helpful medical assistant AI. The following is the extracted text from a prescription:\n\n" ),
                    ("human", "User Prescription"+ text),
                ]
                ai_msg = cl.user_session.get("llm").invoke(messages)
                await cl.Message(content=ai_msg.content).send()
            else:
                response_message = "Sorry, I couldn't extract any text from the PDF."
                await cl.Message(content=response_message).send()
        elif "image" in file.mime:  # Check if the file is an image
            await cl.Message(content="Image received. Processing images is not implemented yet.").send()
        else:
            await cl.Message(content="Unsupported file type. Please upload a PDF or image.").send()

def extract_text_from_pdf(file_path):
    try:
        # Open the PDF file
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None