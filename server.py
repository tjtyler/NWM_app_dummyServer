import json
from flask import Flask, jsonify, render_template, request
from flask_caching import Cache
from bisect import bisect_left
# TEST URL: http://127.0.0.1:5000/rivernodes?minLng=-106.123&minLat=39.3&maxLng=-106.0&maxLat=39.5
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=900)  # Cache the result for 15 minutes (adjust as needed)
def load_rivernodes_data():
    # Read and parse the JSON file here
    with open('rivernodes.json') as f:
        data = json.load(f)
    lngs = []
    for node in data:
        lngs.append(node['lon'])
    return data, lngs

def binary_search_filter(data, lo, hi):
    lower_bound = bisect_left(data, lo)
    upper_bound = bisect_left(data, hi)
    return lower_bound, upper_bound

def filter_points(data, lngsList, minLng, minLat, maxLng, maxLat):
    left_ind, right_ind = binary_search_filter(lngsList, minLng, maxLng)
    filtered_data = data[left_ind:right_ind]

    # return every node in filtered_data where minLat <= node.lat <= maxLat
    return [node for node in filtered_data if minLat <= node['lat'] <= maxLat]

@app.route('/rivernodes', methods=['GET'])
def get_rivernodes_data():
    minLng = float(request.args.get('minLng'))
    minLat = float(request.args.get('minLat'))
    maxLng = float(request.args.get('maxLng'))
    maxLat = float(request.args.get('maxLat'))

    data, lngsList = load_rivernodes_data()
    filtered_data = filter_points(data, lngsList, minLng, minLat, maxLng, maxLat)

    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
