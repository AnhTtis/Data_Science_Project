import feedparser
import re
import json
import time

def id_to_tuple(arxiv_id: str):
    clean = re.sub(r'^arXiv:', '', arxiv_id)
    match = re.match(r'(\d{4})\.(\d+)(v\d+)?$', clean)
    if not match:
        raise ValueError(f"Invalid arXiv id format: {arxiv_id}")
    prefix, num, version = match.groups()
    return prefix, int(num), version

def tuple_to_id(prefix, num):
    return f"{prefix}.{num:05d}"

def get_arxiv_id_exists(arxiv_id):
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    feed = feedparser.parse(url)
    return bool(feed.entries)

def collect_ids_sequentially(start_id, end_id):
    prefix, start_num, _ = id_to_tuple(start_id)
    _, end_num, _ = id_to_tuple(end_id)
    ids = []
    for num in range(start_num, end_num + 1):
        arxiv_id = tuple_to_id(prefix, num)
        if get_arxiv_id_exists(arxiv_id):
            ids.append(arxiv_id)
            print(f"Found: {arxiv_id}")
        else:
            print(f"Not found: {arxiv_id}")
        time.sleep(0.5)  # Be polite to the API
    return ids

# --- Run ---
start_id = "2303.07856"
end_id   = "2304.04606"

arxiv_ids = collect_ids_sequentially(start_id, end_id)

output_file = f"arxiv_ids_{start_id}_{end_id}_sequential.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(arxiv_ids, f, ensure_ascii=False, indent=2)

print(f"Saved {len(arxiv_ids)} arXiv IDs to {output_file}")