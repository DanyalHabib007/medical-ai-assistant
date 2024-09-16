import re
from src.helper import appointment_manager




class AppointmentBookingFlow:
    def _init_(self):
        self.details = {
            'patient_name': None,
            'doctor_name': None,
            'appointment_date': None,
            'appointment_time': None,
            'contact_information': None,
            'purpose_of_booking': None
        }

    def set_patient_name(self, name):
        self.details['patient_name'] = name

    def set_doctor_name(self, name):
        self.details['doctor_name'] = name

    def set_appointment_date(self, date):
        self.details['appointment_date'] = date

    def set_appointment_time(self, time):
        self.details['appointment_time'] = time

    def set_contact_information(self, contact):
        self.details['contact_information'] = contact

    def set_purpose_of_booking(self, purpose):
        self.details['purpose_of_booking'] = purpose

    def complete_booking(self):
        # Example booking logic
        if all(self.details.values()):
            # Perform booking logic here

            # Assuming AppointmentManager is already instantiated as appointment_manager
            doctor_name = self.details.get('doctor_name')
            patient_name = self.details.get('patient_name')
            appointment_time = f"{self.details.get('appointment_date')} {self.details.get('appointment_time')}"
            contact_information = self.details.get('contact_information')
            purpose_of_booking = self.details.get('purpose_of_booking')

            # Book the appointment and handle any errors
            try:
                response = appointment_manager.book_appointment(
                doctor_name, 
                patient_name, 
                appointment_time, 
                contact_information, 
                purpose_of_booking
                )
                return response
            except Exception as e:
                return f"An error occurred during booking: {str(e)}"

            return "Appointment booked successfully!"
        else:
            return "Please provide all required details."

booking_flow = AppointmentBookingFlow()

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from pinecone import Pinecone
from pymongo import MongoClient
from bson.objectid import ObjectId
import os



class AppointmentManager:
    def _init_(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def close(self):
        self.client.close()

    def check_availability(self, doctor_name, desired_time):
        print(f"Checking availability for {doctor_name} at {desired_time}")
        # Check if an appointment already exists for the desired time
        existing_appointment = self.db.appointments.find_one({
            "doctor_name": doctor_name,
            "appointment_time": desired_time
        })
        
        if existing_appointment:
            print(f"Appointment already exists at {desired_time} for doctor {doctor_name}.")
            return False, "The desired time is not available. Please choose another time."
        
        print(f"Time slot {desired_time} is available.")
        return True, None

    def book_appointment(self, doctor_name, patient_name, desired_time, contact_information, purpose_of_booking):
        print(f"Attempting to book appointment for {patient_name} with {doctor_name} at {desired_time}")
        
        is_available, message = self.check_availability(doctor_name, desired_time)
        if not is_available:
            print(f"Booking failed: {message}")
            return message

        # Create a new appointment with additional fields
        try:
            self.db.appointments.insert_one({
                "doctor_name": doctor_name,
                "patient_name": patient_name,
                "appointment_time": desired_time,
                "contact_information": contact_information,
                "purpose_of_booking": purpose_of_booking,
                "appointment_status": "confirmed"
            })
            print(f"Appointment successfully booked for {patient_name} with {doctor_name} at {desired_time}.")
            return f"Your appointment is confirmed with {doctor_name} at {desired_time}."
        except Exception as e:
            print(f"Error booking appointment: {e}")
            return "An error occurred while booking the appointment. Please try again."

# MongoDB connection setup
mongo_uri = os.getenv("MONGO_URI")
mongo_db = "medical_db"
appointment_manager = AppointmentManager(mongo_uri, mongo_db)