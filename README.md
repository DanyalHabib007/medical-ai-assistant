# Medical AI Assistant 🤖🏥

Welcome to the **Medical AI Assistant** project! This intelligent system is designed to enhance hospital operations by providing efficient and automated solutions for handling patient queries, appointment bookings, and medical document processing. 🎯

## 🚀 Overview

The Medical AI Assistant integrates cutting-edge technologies to deliver a seamless experience for both hospital staff and patients. Our system uses **Chainlit** for a user-friendly interface, **Llama 3.1** for natural language processing, and **Qdrant** & **MongoDB** for efficient data management. It’s deployed on **Render** for scalability and reliability. 🌐

## 🛠️ Technology Stack

- **Python**: The core programming language used for development.
- **Chainlit**: Frontend framework for handling text, audio, and file inputs. 🖥️🎙️📄
- **Llama 3.1**: Large Language Model (LLM) for generating intelligent responses. 🧠
- **Qdrant**: Vector database for storing and retrieving high-dimensional vectors. 🔍
- **MongoDB**: NoSQL database for managing structured data like appointment bookings. 📊
- **Render**: Cloud platform for deployment, scaling, and monitoring. ☁️

## 💡 Features

- **Multimodal Input Handling**: Supports text, audio, and file uploads for flexible user interaction. ✏️🎤📁
- **Smart Query Processing**: Utilizes Llama 3.1 and RAG model to provide accurate responses to hospital-related queries. 🗂️
- **Efficient Appointment Management**: Automatically handles appointment requests and stores details in MongoDB. 📅
- **Document Processing**: Extracts and interprets information from uploaded medical documents. 📄🔍

## 🧩 Installation

To get started, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/your-username/medical-ai-assistant.git
cd medical-ai-assistant
pip install -r requirements.txt
```

## 🔧 Configuration

1. **Set Up Environment Variables**: Create a `.env` file in the root directory with the following variables:
    ```
    MONGO_DB_URI=your_mongodb_uri
    QDRANT_API_KEY=your_qdrant_api_key
    GROQ_API_KEY=your_llama3.1_api_key
    ```
2. **Run the Application**: Start the server locally:
    ```bash
    chainlit run main.py
    ```

## 🎉 Usage

- **Frontend**: Access the Medical AI Assistant through the Chainlit interface. 
- **Queries**: Type or speak your questions, or upload medical documents.
- **Appointments**: Book, view, and manage appointments directly through the system.

## Architecture

![Architecture.png](https://i.ibb.co/ZWJ91Mh/Final.png)

## Presentation

[Link to PPT](https://docs.google.com/presentation/d/1xwYNdejY8XjbtCfvec-sTiLKBA5B8bOg/edit?usp=sharing&ouid=107570087942373100747&rtpof=true&sd=true)

## Technical Document

[Link to Doc](https://docs.google.com/document/d/1wjEMPK8lmcr4z9QsmOaryqgiuJMqiiLj/edit?usp=sharing&ouid=107570087942373100747&rtpof=true&sd=true)

## 🌟 Contributors

[@Amber Bagchi](https://github.com/amber-bagchi)
[@Ankit Kumar](https://github.com/iamankit7667)
[@Danyal Habib](https://github.com/DanyalHabib007)
[@Om Shankar Thakur](https://github.com/Om-Shankar-Thakur)

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 📝

## 🤝 Acknowledgements

- **Chainlit**: For an amazing UI framework.
- **Llama 3.1**: For powerful language modeling.
- **Qdrant**: For efficient vector storage and retrieval.
- **MongoDB**: For reliable data management.
- **Render**: For scalable and reliable cloud deployment.



Thank you for checking out the Medical AI Assistant! We hope it brings value to healthcare environments by streamlining operations and enhancing patient interactions. 🚀👨‍⚕️👩‍⚕️
