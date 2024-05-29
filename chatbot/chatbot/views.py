from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import pandas as pd
import tiktoken
from scipy import spatial
from openai import OpenAI
import time
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from .message_queue import message_queue

EMBEDDING_MODEL = 'text-embedding-ada-002'
GPT_MODEL = 'gpt-3.5-turbo'
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        question = request.data['context']
        answer = client.chat.completions.create(
            messages= [
                {'role': 'system', 'content': '모든 말 끝에는 "얍" 이라는 말을 붙여. 예를들어 안녕하세요얍, 만나서 반갑습니다얍 이런식으로 모든 말 끝에 공백없이 얍을 붙여줘.'},
                {'role': 'user', 'content': question}
            ],
            model=GPT_MODEL,
            temperature=0
        )
        message_queue.put(f"Bot: {answer.choices[0].message.content}")
        return JsonResponse({'status': 'Message received'})
    else:
        return JsonResponse({'status': 'Only POST method is allowed'})


def sse(request):
    def event_stream():
        while True:
            if not message_queue.empty():
                message = message_queue.get()
                print(message)
                yield f"data: {message}\n\n"
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response
