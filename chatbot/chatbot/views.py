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
from .prompt import generatePrompt
from pinecone import Pinecone

EMBEDDING_MODEL = 'text-embedding-ada-002'
GPT_MODEL = 'gpt-3.5-turbo'
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PINECON_API_KEY = os.environ["PINECONE_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECON_API_KEY)

index = pc.Index('job-posting')

def get_embedding(text):
    res = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    embed = [record.embedding for record in res.data]
    return embed[0]

@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        question = request.data['context']
        embed_question = get_embedding(question)
        search_result = index.query(vector=[embed_question], top_k=3, include_metadata=True)
        relevant_docs = [match['metadata']['text'] for match in search_result['matches']]
        answer = client.chat.completions.create(
            messages= [
                {'role': 'system', 'content': generatePrompt(relevant_docs)},
                {'role': 'user', 'content': question}
            ],
            model=GPT_MODEL,
            temperature=0
        )
        message_queue.put(f"Bot: {answer.choices[0].message.content}")
        print(answer.choices[0].message.content)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'invalid method'})


def sse(request):
    message_queue.put(f"Bot: 안녕하세얍! 무엇을 도와드릴까얍?")
    def event_stream():
        while True:
            if not message_queue.empty():
                message = message_queue.get()
                yield f"data: {message}\n\n"
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response
