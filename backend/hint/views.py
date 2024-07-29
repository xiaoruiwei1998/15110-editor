# views.py

import requests
from django.http import JsonResponse

def get_hint(request):
    if request.method == 'POST':
        # You can customize your prompt and other parameters as needed
        data = {
            'model': 'gpt-4',  # or any other appropriate model
            'messages': [{"role": "user", "content": "generate a hint"}],
            'max_tokens': 50
        }
        headers = {
            'Authorization': 'open-ai-api-here'
        }
        print(data)
        response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
        print(response)
        response_json = response.json()
        return JsonResponse(response_json)
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests'}, status=405)
