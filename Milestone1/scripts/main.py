import threading
import queue
import time
import arxiv
import psutil
from arXiv_handler import get_IDs_All
from downloader import download
from reference_extractor import extract_references_for_paper
import os
import random
import re

# ---------------------------
# Helpers
# ---------------------------

def now_memory_mb():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)

def print_mem(prefix=""):
    print(f"{prefix} RAM = {now_memory_mb():.2f} MB")

# ---------------------------
# Missing papers detection
# ---------------------------

PATTERN = re.compile(r"^(\d{4})-(\d{5})$")  # folder name pattern YYMM-NNNNN

def collect_existing_ids(base_dir: str, target_months: list):
    """Return a dict of existing paper tails for each target month."""
    existing = {ym: set() for ym in target_months}
    for entry in os.scandir(base_dir):
        if entry.is_dir():
            m = PATTERN.match(entry.name)
            if m:
                yymm, tail = m.group(1), int(m.group(2))
                if yymm in target_months:
                    existing[yymm].add(tail)
    return existing

def find_missing_ids(yymm, existing_set, start_tail, end_tail):
    """Return sorted list of missing tails in a given range."""
    expected_range = set(range(start_tail, end_tail + 1))
    return sorted(expected_range - existing_set)

def format_arxiv_ids(yymm, tails):
    return [f"{yymm}.{t:05d}" for t in tails]

# ---------------------------
# Core Workers
# ---------------------------

def fetch_ids_worker(start_month, start_year, start_ID,
                     end_month, end_year, end_ID,
                     start_index, num_papers,
                     download_all):
    """
    Fetch arXiv IDs and build a dictionary per yymm of start & end IDs.
    Returns:
        selected_ids: list of IDs to download first
        yymm_ranges: dict {yymm: (start_tail, end_tail)}
    """
    print("\n[Step 1] Fetching arXiv IDs...")
    t0 = time.time()
    mem0 = now_memory_mb()

    ids = get_IDs_All(start_month, start_year, start_ID,
                       end_month, end_year, end_ID)

    if download_all:
        selected_ids = ids
        print(f"[Step 1] download_all=True → Using ALL {len(selected_ids)} IDs")
    else:
        selected_ids = ids[start_index:start_index + num_papers]
        print(f"[Step 1] Using RANGE {start_index} → {start_index + num_papers}, total {len(selected_ids)} IDs")

    # Build yymm_ranges dict automatically
    yymm_ranges = {}
    for arxiv_id in ids:
        yymm, tail_str = arxiv_id.split(".")
        tail = int(tail_str)
        if yymm not in yymm_ranges:
            yymm_ranges[yymm] = [tail, tail]
        else:
            yymm_ranges[yymm][0] = min(yymm_ranges[yymm][0], tail)
            yymm_ranges[yymm][1] = max(yymm_ranges[yymm][1], tail)

    print(f"[Step 1] Built yymm_ranges: {yymm_ranges}")
    print(f"[Step 1] Done in {time.time() - t0:.2f} sec | RAM used = {now_memory_mb() - mem0:.2f} MB\n")

    return selected_ids, yymm_ranges

def download_with_retries(client, arxiv_id, max_retries=5):
    for attempt in range(max_retries):
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            return next(client.results(search))
        except Exception as e:
            if "HTTP 429" in str(e) or "HTTP 503" in str(e):
                wait = min(60 * (2 ** attempt), 600) + random.uniform(0, 5)
                print(f"[Download] Busy: {e}. Retry in {wait:.1f}s")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"[Download] Failed after retries: {arxiv_id}")

def download_worker(id_queue, download_queue, base_data_dir, delay=2):
    client = arxiv.Client()
    processed = 0
    while True:
        arxiv_id = id_queue.get()
        if arxiv_id is None:
            id_queue.task_done()
            print(f"[Download] Thread exit. Total downloaded: {processed}")
            break
        try:
            print(f"[Download] Start {arxiv_id}")
            result_latest = download_with_retries(client, arxiv_id)

            version_latest = int(result_latest.get_short_id().split('v')[1])
            list_download = [result_latest]

            for v in range(1, version_latest):
                res = download_with_retries(client, f"{arxiv_id}v{v}")
                list_download.append(res)

            download(list_download, base_data_dir)
            processed += 1
            print(f"[Download] Done {arxiv_id} (Total {processed})")
            download_queue.put(arxiv_id)
            time.sleep(delay)
        except Exception as e:
            print(f"[Download] Error {arxiv_id}: {e}")
        finally:
            id_queue.task_done()

def reference_worker(download_queue, base_data_dir, delay=2):
    processed = 0
    while True:
        arxiv_id = download_queue.get()
        if arxiv_id is None:
            download_queue.task_done()
            print(f"[Reference] Thread exit. Total extracted: {processed}")
            break
        try:
            print(f"[Reference] Start {arxiv_id}")
            extract_references_for_paper(arxiv_id, base_data_dir)
            processed += 1
            print(f"[Reference] Done {arxiv_id} (Total {processed})")
            time.sleep(delay)
        except Exception as e:
            print(f"[Reference] Error {arxiv_id}: {e}")
        finally:
            download_queue.task_done()

# ---------------------------
# Missing papers auto-recovery
# ---------------------------

def recover_missing_papers(base_dir, yymm_ranges):
    """
    Loop until all missing papers are downloaded.
    Automatically detects missing papers in target months.
    """
    target_months = list(yymm_ranges.keys())
    while True:
        existing = collect_existing_ids(base_dir, target_months)
        missing_ids = []

        for yymm in target_months:
            start_tail, end_tail = yymm_ranges[yymm]
            missing_tails = find_missing_ids(yymm, existing.get(yymm, set()), start_tail, end_tail)
            missing_ids.extend(format_arxiv_ids(yymm, missing_tails))

        if not missing_ids:
            print(f"\n✅ No missing papers left for months: {target_months}")
            break

        print(f"\n⚠️ Missing papers detected ({len(missing_ids)}): {missing_ids[:20]}{'...' if len(missing_ids)>20 else ''}")

        id_queue = queue.Queue(maxsize=len(missing_ids) + DOWNLOAD_THREAD_COUNT)
        download_queue = queue.Queue(maxsize=len(missing_ids) + REFERENCE_THREAD_COUNT)

        for aid in missing_ids:
            id_queue.put(aid)
        for _ in range(DOWNLOAD_THREAD_COUNT):
            id_queue.put(None)

        # Start download threads
        download_threads = []
        for _ in range(DOWNLOAD_THREAD_COUNT):
            t = threading.Thread(target=download_worker, args=(id_queue, download_queue, base_dir))
            t.start()
            download_threads.append(t)

        # Start reference threads
        reference_threads = []
        for _ in range(REFERENCE_THREAD_COUNT):
            t = threading.Thread(target=reference_worker, args=(download_queue, base_dir))
            t.start()
            reference_threads.append(t)

        id_queue.join()

        for _ in range(REFERENCE_THREAD_COUNT):
            download_queue.put(None)
        download_queue.join()

        for t in download_threads:
            t.join()
        for t in reference_threads:
            t.join()

        print("✅ Batch complete. Rechecking for missing papers...\n")

# ---------------------------
# Main
# ---------------------------

if __name__ == "__main__":
    DOWNLOAD_THREAD_COUNT = 3
    REFERENCE_THREAD_COUNT = 2

    base_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "23127130_Test"))
    os.makedirs(base_data_dir, exist_ok=True)

    # Parameters
    start_month = 3
    start_year = 2023
    end_month = 4
    end_year = 2023
    start_ID = 7856
    end_ID = 4606
    start_index = 9000
    num_papers = 100
    download_all = False

    print("Starting pipeline...\n")
    print_mem("[START]")
    pipeline_start = time.time()

    # Step 1: fetch IDs and build yymm_ranges
    selected_ids, yymm_ranges = fetch_ids_worker(
        start_month, start_year, start_ID,
        end_month, end_year, end_ID,
        start_index, num_papers,
        download_all
    )
    print(yymm_ranges)

    # Initial download batch
    id_queue = queue.Queue(maxsize=len(selected_ids) + DOWNLOAD_THREAD_COUNT)
    download_queue = queue.Queue(maxsize=len(selected_ids) + REFERENCE_THREAD_COUNT)

    for aid in selected_ids:
        id_queue.put(aid)
    for _ in range(DOWNLOAD_THREAD_COUNT):
        id_queue.put(None)

    download_threads = []
    for _ in range(DOWNLOAD_THREAD_COUNT):
        t = threading.Thread(target=download_worker, args=(id_queue, download_queue, base_data_dir))
        t.start()
        download_threads.append(t)

    reference_threads = []
    for _ in range(REFERENCE_THREAD_COUNT):
        t = threading.Thread(target=reference_worker, args=(download_queue, base_data_dir))
        t.start()
        reference_threads.append(t)

    id_queue.join()
    for _ in range(REFERENCE_THREAD_COUNT):
        download_queue.put(None)
    download_queue.join()
    for t in download_threads:
        t.join()
    for t in reference_threads:
        t.join()

    # Step 2: recover missing papers
    recover_missing_papers(base_data_dir, yymm_ranges)

    total_time = time.time() - pipeline_start
    total_ram_used = now_memory_mb()

    print("\n===============================")
    print(f"Pipeline complete in {total_time:.2f} sec")
    print(f"Total RAM used ≈ {total_ram_used:.2f} MB")
    print("===============================")
