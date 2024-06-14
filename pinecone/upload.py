from pinecone import Pinecone, ServerlessSpec
from PIL import Image
import pytesseract
import os
import numpy as np
from openai import OpenAI
import base64

EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']

client = OpenAI(
    api_key=OPENAI_API_KEY
)

JOB_POSTING_PROMPT = """
    너는 구글 채용 큐레이터야.
    채용공고 이미지를 텍스트로 변환한 후 정리해야해.
    기업명, 채용분야, 담당업무, 전형일정, 지원자격, 자격요건, 채용기간, 우대사항, 복지혜택, 근무지, 계약형태, 채용담당자 연락처 혹은 이메일, 입사후 처우 등등
    채용기간은 구체적일수록 좋아 채용 스텝별 기간이 적혀있으면 정리해줘.
 
    아래는 정리해야 할 예시야. 아래 양식에 맞춰서 정리해줘.
 
    기업명: 마이다스인
    채용분야: 프론트엔드 개발
    담당업무: 웹 클라우드 기반 채용서비스 프론트엔드 직무를 담당합니다.
    지원자격: 4년제 졸업, jquery, react, javascript 를 사용할 수 있어야 합니다.
    계약형태: 3개월 계약직 검토 후 정규직 전환
    채용기간: 2024년 5월 30일부터 서류 접수를 시작합니다. 2024년 6월 중 역량검사 전형이 예정돼있고, 2024년 7월에 1차면접, 2024년 8월에 2차면접 후, 2024년 9월에 처우협의 및 최종합격자 발표 예정입니다.
    채용담당자: 유병재 (이메일: ybj121725@gmail.com, 연락처: 010-8279-4218)
    복리후생: 마이다스 복지포인트 지급, 사내 헬스장 사용 가능.
"""
 

class FileToPineconeDB:
    def __init__(self, folder_path, pinecone_api_key, index_name):
        self.folder_path = folder_path
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        self.init_pinecone()
        self.files = self.list_files_in_folder()

    def init_pinecone(self):
        pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = pc.Index(self.index_name)

    def list_files_in_folder(self):
        files = []
        for root, dirs, filenames in os.walk(self.folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        return files
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_text_from_image(self, image_path):
        # img = Image.open(image_path)
        # text = pytesseract.image_to_string(image=img, lang='kor+eng')
        # return text
        base64_image = self.encode_image(image_path)
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": JOB_POSTING_PROMPT
            },
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "이 채용공고 이미지를 한글로 정리해줘."},
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high"
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
        print(response.choices[0].message.content)
        print('\n====================')
        return response.choices[0].message.content

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