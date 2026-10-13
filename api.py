from flask import Flask, request, jsonify, send_from_directory
import threading
import uuid
import os
import time
import sys

# Ensure stdout can handle utf-8 characters on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from config import API_HOST, API_PORT, OUTPUT_DIR
from query_generator import SmartQueryGenerator
from scraper import WebScraper
from data_cleaner import DataCleaner
from sentiment_analyzer import SentimentAnalyzer
from signal_generator import SignalGenerator
from csv_generator import CSVGenerator

app = Flask(__name__)

# In-memory store for jobs
jobs = {}

def process_job(job_id, raw_query):
    try:
        jobs[job_id]["status"] = "processing"
        
        # 1. Smart Query
        query_gen = SmartQueryGenerator()
        query_info = query_gen.generate(raw_query)
        search_query = query_info["optimized"]
        jobs[job_id]["query_info"] = query_info
        
        # 2. Web Scraping
        scraper = WebScraper()
        raw_data = scraper.scrape_all(search_query)
        
        # 3. Data Cleaning
        cleaner = DataCleaner()
        cleaned_data = cleaner.process_data(raw_data)
        
        # 4. Sentiment Analysis
        analyzer = SentimentAnalyzer()
        analyzed_data = analyzer.analyze_articles(cleaned_data)
        
        # 5. Signal Generation
        generator = SignalGenerator()
        result_summary = generator.aggregate_sentiment(analyzed_data)
        
        # 6. CSV Generation
        csv_gen = CSVGenerator()
        csv_filename = csv_gen.generate(search_query, analyzed_data)
        
        # Store results
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result_summary"] = result_summary
        jobs[job_id]["entries"] = analyzed_data
        jobs[job_id]["csv_filename"] = csv_filename
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
        
    raw_query = data['query']
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "queued",
        "original_query": raw_query,
        "created_at": time.time()
    }
    
    # Start background thread
    thread = threading.Thread(target=process_job, args=(job_id, raw_query))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "message": "Scraping and analysis job started in the background."
    }), 202

@app.route('/results', methods=['GET'])
def get_results():
    job_id = request.args.get('job_id')
    if not job_id:
        return jsonify({"error": "Missing 'job_id' parameter"}), 400
        
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    if job["status"] != "completed":
        return jsonify({
            "job_id": job_id,
            "status": job["status"],
            "error": job.get("error")
        })
        
    summary = job["result_summary"]
    dist = summary.get("distribution", {})
    total = summary.get("article_count", 0)
    
    pos_pct = round((dist.get("positive", 0) / total * 100) if total else 0, 1)
    neg_pct = round((dist.get("negative", 0) / total * 100) if total else 0, 1)
    neu_pct = round((dist.get("neutral", 0) / total * 100) if total else 0, 1)
    
    response = {
        "job_id": job_id,
        "status": "completed",
        "query": job["original_query"],
        "query_info": job.get("query_info"),
        "summary": {
            "total_entries": total,
            "positive": dist.get("positive", 0),
            "negative": dist.get("negative", 0),
            "neutral": dist.get("neutral", 0),
            "positive_pct": pos_pct,
            "negative_pct": neg_pct,
            "neutral_pct": neu_pct,
            "aggregate_score": summary.get("aggregate_score", 0.0),
            "signal": summary.get("signal", "HOLD")
        },
        "entries": job.get("entries", []),
        "csv_file": job.get("csv_filename")
    }
    
    return jsonify(response)

@app.route('/download', methods=['GET'])
def download():
    job_id = request.args.get('job_id')
    if not job_id:
        return jsonify({"error": "Missing 'job_id' parameter"}), 400
        
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    if job["status"] != "completed":
        return jsonify({"error": f"Job is not completed yet (status: {job['status']})"}), 400
        
    csv_filename = job.get("csv_filename")
    if not csv_filename:
        return jsonify({"error": "No CSV file generated for this job"}), 500
        
    try:
        return send_from_directory(
            os.path.abspath(OUTPUT_DIR),
            csv_filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": f"Failed to send file: {e}"}), 500

if __name__ == '__main__':
    print(f"Starting API server on {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=False)
