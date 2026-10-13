"""Manual end-to-end API smoke test. Start api.py before running this script."""

def main():
    import requests
    import time

    print("1. Submitting search job for 'tesla'...")
    res = requests.post('http://127.0.0.1:5000/search', json={'query': 'tesla'}).json()
    print("Response:", res)

    job_id = res['job_id']

    print(f"\n2. Polling for job {job_id}...")
    while True:
        res = requests.get(f'http://127.0.0.1:5000/results?job_id={job_id}').json()
        status = res.get('status')
        print(f"Status: {status}")
        if status == 'completed' or status == 'failed':
            break
        time.sleep(2)

    if status == 'completed':
        print("\n3. Success!")
        print(f"Processed {res['summary']['total_entries']} entries")
        print(f"Sentiment: {res['summary']['positive_pct']}% Pos, {res['summary']['negative_pct']}% Neg, {res['summary']['neutral_pct']}% Neu")
        print(f"Aggregate Score: {res['summary']['aggregate_score']} -> {res['summary']['signal']}")
        print(f"CSV File generated: {res['csv_file']}")
        print("\nSample Entry:")
        if res['entries']:
            e = res['entries'][0]
            print(f"[{e['source']}] {e['title']}")
            print(f"Label: {e['label']}, Score: {e['score']}")
    else:
        print("\nJob failed:")
        print(res)

if __name__ == "__main__":
    main()
