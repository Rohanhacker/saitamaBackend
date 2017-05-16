from flask import Flask, request, jsonify
from timeout import timeout
import threading
import requests
import time

result = {
    'query': '',
    'results': {
        'google': {
            'url': '',
            'text': ''
        },
        'twitter': {
            'url': '',
            'text': ''
        },
        'duckduckgo': {
            'url': '',
            'text': ''
        }
    }
}


def searchDuck(keyword):
    try:
        req = requests.get('http://api.duckduckgo.com/?q={}&format=json'.format(keyword),timeout=1)
        results = req.json()
        # print(results.get('Heading'), results.get('AbstractURL'))
        result['results']['duckduckgo'] = { 'url': results.get('AbstractURL'), 'text': results.get('Heading') } 
    except requests.exceptions.Timeout:
        result['results']['duckduckgo'] = 'timeout'        

def searchGoogle(keyword):
    try:
        req = requests.get('https://www.googleapis.com/customsearch/v1?key=AIzaSyC-7M6lMWbYroXnZ3Y3AoBc8lcOLp52MFI&cx=001033254069548393564:3z8-gnrutii&fields=items(title,link)&q={}'.format(keyword),timeout=1)
        results = req.json()['items'][0]
        # print(results.get('link'), results.get('title'))
        result['results']['google'] = { 'url': results.get('link'), 'text': results.get('title')}
    except requests.exceptions.Timeout:
        result['results']['google'] = 'timeout'
    except KeyError:
        result['results']['google'] = 'api limit exceeded'

def searchTwitter(keyword):
    try:
        headers = {'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAB290gAAAAAA6eGMVV8n0q1OgI%2BmgiMD0pCiVhc%3Dqj3jaBNPsp7kfS3siPuHL4ZG5Cfl6kzCsD9fd0FWwU5Fm9vBcF'}
        req = requests.get('https://api.twitter.com/1.1/search/tweets.json?q={}'.format(keyword), headers=headers, timeout=1)
        results = req.json()['statuses'][0]
        # print(results.get('text'), results['entities']['urls'])
        result['results']['twitter'] = {'url': 'https://twitter.com/statuses/{}'.format(results.get('id')), 'text': results.get('text')}
    except requests.exceptions.Timeout:
        result['results']['twitter'] = 'timeout'




app = Flask(__name__)

@app.route('/', methods=['GET'])
def search():
    q = request.args['q']
    result['query'] = q
    start = time.time()
    threads = [threading.Thread(target=searchTwitter, args=(q,)),threading.Thread(target=searchDuck, args=(q,)), threading.Thread(target=searchGoogle, args=(q,))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    elapsedTime = time.time() - start
    print("Elapsed Time: %s" % (elapsedTime))
    # print(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(threaded=True, debug=True)







