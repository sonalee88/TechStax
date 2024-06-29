@app.route('/events', methods=['GET'])
def get_events():
    events = events_collection.find().sort('timestamp', -1).limit(10)
    return jsonify(list(events))

