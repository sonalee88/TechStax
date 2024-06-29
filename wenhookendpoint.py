from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']
events_collection = db['events']

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'push':
        event_data = {
            'type': 'push',
            'author': payload['pusher']['name'],
            'to_branch': payload['ref'].split('/')[-1],
            'timestamp': datetime.datetime.utcnow()
        }
    elif event == 'pull_request':
        action = payload['action']
        if action in ['opened', 'closed']:
            event_data = {
                'type': 'pull_request',
                'author': payload['pull_request']['user']['login'],
                'from_branch': payload['pull_request']['head']['ref'],
                'to_branch': payload['pull_request']['base']['ref'],
                'timestamp': datetime.datetime.utcnow()
            }
    elif event == 'pull_request_review' and payload['action'] == 'submitted':
        event_data = {
            'type': 'merge',
            'author': payload['review']['user']['login'],
            'from_branch': payload['pull_request']['head']['ref'],
            'to_branch': payload['pull_request']['base']['ref'],
            'timestamp': datetime.datetime.utcnow()
        }
    else:
        return jsonify({'status': 'ignored'})

    events_collection.insert_one(event_data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)


@app.route('/events', methods=['GET'])
def get_events():
    events = events_collection.find().sort('timestamp', -1).limit(10)
    return jsonify(list(events))

