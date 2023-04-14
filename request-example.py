import requests
import time


response = requests.post('http://127.0.0.1:5000/upscale/', json={
    'image_1': 'lama_300px.png',
    'image_2': 'lama_600px.png'
})

response_json = response.json()
task_id = response_json['task_id']
status = 'PENDING'


while status == 'PENDING':
    response = requests.get(f'http://127.0.0.1:5000/tasks/{task_id}/')
    response_json = response.json()
    status = response_json['status']
    if status == "PENDING":
        print('Please wait...')
        time.sleep(2)

print(status)
print(response_json['full_path'])

file_id = response_json['file_id']
open_image = requests.get(f'http://127.0.0.1:5000/processed/{file_id}/')
open_image_json = open_image.json()
print(open_image_json['result'])
