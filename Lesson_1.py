import requests
import json

#Tast 1
#username - ник на githab
#выводит список репозиториев
username = 'grayhor'
req = requests.get('https://api.github.com/users/' + username+ '/repos')
data = req.json()
for i in range(len(data)):
    print(data[i]['name'])

#task 2

req = requests.get('https://api.nytimes.com/svc/movies/v2/reviews/search.json?query=godfather&api-key=9fu5gRSfku6xrIV0WecVddS26VAAhscu')
print(req.status_code)
data_movie = req.json()
#print(json.dump(data_movie, indent=4, sort_keys=True))
with open('movie.json', 'w') as f:
    json.dump(data_movie, f, indent=4, sort_keys= True)
