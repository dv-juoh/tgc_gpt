from pinecone import Pinecone, ServerlessSpec
from PIL import Image
import pytesseract
import os
import numpy as np
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']

client = OpenAI(
    api_key=OPENAI_API_KEY
)

class FileToPineconeDB:
    def __init__(self, folder_path, pinecone_api_key, index_name):
        self.folder_path = folder_path
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        self.init_pinecone()
        self.files = self._list_files_in_folder()

    def init_pinecone(self):
        pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = pc.Index(self.index_name)

    def _list_files_in_folder(self):
        files = []
        for root, dirs, filenames in os.walk(self.folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        return files

    def extract_text_from_image(self, image_path):
        img = Image.open(image_path)
        text = pytesseract.image_to_string(image=img, lang='kor+eng')
        return text

    def get_embedding(self, text):
        res = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embeds = [record.embedding for record in res.data]
        return embeds[0]

    def process_files(self):
        for file_path in self.files:
            if file_path.endswith('.jpg') or file_path.endswith('.png'):
                extracted_text = self.extract_text_from_image(file_path)
                embedding = self.get_embedding(extracted_text)
                filename = os.path.basename(file_path)
                self.index.upsert(vectors=[(filename, embedding, {'text': extracted_text})])

file_processor = FileToPineconeDB(folder_path='/Users/ybj1217-mac/Desktop/tgc_gpt/pinecone/data', pinecone_api_key=PINECONE_API_KEY, index_name='job-posting')
file_processor.process_files()