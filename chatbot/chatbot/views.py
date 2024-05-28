from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import pandas as pd
import tiktoken
from scipy import spatial
from openai import OpenAI

EMBEDDING_MODEL = 'text-embedding-ada-002'
GPT_MODEL = 'gpt-3.5-turbo'
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        response = client.chat.completions.create(
            messages= [
                {'role': 'user', 'content': data['context']}
            ],
            model=GPT_MODEL,
            temperature=0
        )
        return Response({'response': response.choices[0].message.content}, status=status.HTTP_200_OK)
