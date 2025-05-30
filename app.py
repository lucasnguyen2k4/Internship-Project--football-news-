from flask import Flask, send_file, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "AjHJ8y3ZPnroSXIvKK_f"),
    verify_certs=False
)

@app.route('/')
def home():
    return send_file('index.html')


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get("query", "")
    league = data.get("league", "")
    club = data.get("club", "")
    source = data.get("source", "")
    date_sort = data.get("date", "desc")
    from_value = data.get("from", 0)

    es_query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "type": "phrase",
                        "fields": [
                            "title^3", "summary^2", "source",
                            "clubs^5", "leagues^6", "main_league^7"
                        ]
                    }
                }
            ] if query else [{"match_all": {}}],
            "filter": []
        }
    }
    if league:
        es_query["bool"]["filter"].append({"term": {"main_league": league}})
    if club:
        es_query["bool"]["filter"].append({"term": {"clubs": club}})
    if source:
        es_query["bool"]["filter"].append({"term": {"source": source}})

    results = es.search(
        index="football_news",
        query=es_query,
        sort=[{"date": {"order": date_sort}}],
        size=20,
        from_=from_value
    )

    hits = results["hits"]["hits"]

    return jsonify([
        {
            "title": hit["_source"].get("title", ""),
            "summary": hit["_source"].get("summary", ""),
            "url": hit["_source"].get("url", ""),
            "source": hit["_source"].get("source", ""),
            "date": hit["_source"].get("date", ""),
            "clubs": hit["_source"].get("clubs", []),
            "leagues": hit["_source"].get("leagues", [])
        }
        for hit in hits
    ])


@app.route('/api/clubs', methods=["GET"])
def get_clubs():
    league = request.args.get("league", "")
    query = {"match_all": {}} if not league else {"term": {"main_league": league}}

    response = es.search(
        index="football_news",
        size=0,
        query=query,
        aggs={
            "clubs": {
                "terms": {"field": "clubs", "size": 1000}
            }
        }
    )

    clubs = [bucket["key"] for bucket in response["aggregations"]["clubs"]["buckets"]]
    return jsonify(sorted(clubs))


@app.route('/api/leagues', methods=["GET"])
def get_leagues():
    response = es.search(
        index="football_news",
        size=0,
        aggs={
            "unique_leagues": {
                "terms": {"field": "leagues", "size": 1000}
            }
        }
    )

    leagues = [bucket["key"] for bucket in response["aggregations"]["unique_leagues"]["buckets"]]
    return jsonify(sorted(leagues))

@app.route('/api/sources')
def get_sources():
    body = {
        "size": 0,
        "aggs": {
            "sources": {
                "terms": {"field": "source", "size": 1000}
            }
        }
    }
    res = es.search(index='football_news', body=body)
    sources = [bucket['key'] for bucket in res['aggregations']['sources']['buckets']]
    return jsonify(sources)
if __name__ == '__main__':
    app.run(debug=True)
