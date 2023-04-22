from requests import get, post

print(post('http://127.0.0.1:8080/api/news').json())

print(post('http://127.0.0.1:8080/api/news',
           json={'title': 'Заголовок'}).json())

print(post('http://127.0.0.1:8080/api/news',
           json={'title': 'Заголовок',
                 'content': 'я самая самая красотка!',
                 'user_id': 3,
                 'is_private': False}).json())