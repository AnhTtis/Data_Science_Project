import threading
import queue
import time
import arxiv
from arXiv_handler import get_IDs_All
from downloader import download
from reference_extractor import extract_references_for_paper
import os
import random

# ...existing code...
MISSING_TAILS = [
<<<<<<< HEAD
    "13718","13746","13747","13748","13749","13750","13751","13752","13753","13754",
    "13755","13756","13757","13758","13759","13760","13761","13762","13763","13764",
    "13765","13766","13767","13768","13769","13770","13771","13772","13773","13774",
    "13775","13776","13777","13778","13779","13780","13781","13782","13783","13784",
    "13785","13786","13787","13788","13789","13790","13791","13792","13793","13794",
    "13795","13796","13797","13798","13799","13800","13801","13802","13803","13804",
    "13805","13806","13807","13808","13809","13810","13811","13812","13813","13814",
    "13815","13816","13817","13818","13819","13820","13821","13822","13823","13824",
    "13825","13826","13827","13828","13829","13830","13831","13832","13833","13834",
    "13835","13836","13837","13838","13839","13840","13841","13842","13843","13844",
    "13845","13846","13847","13848","13849","13850","13851","13852","13853","13854",
    "13855","17016","17019","17020","17021","17026","17030","17031","17036",
]
=======
    "12094", "12097"]
>>>>>>> ab7f143b843afca083c7f9af8c6ee35003840800
MISSING_YM = "2303"  # year-month part for all these IDs

def fetch_ids_worker(start_month, start_year, start_ID, end_month, end_year, end_ID, start_index, num_papers, id_queue):
    # Override normal range fetch: use explicit missing IDs
    print("[Step 1] Using explicit missing IDs list.")
    selected_ids = [f"{MISSING_YM}.{tail}" for tail in MISSING_TAILS]
    print(f"[Step 1] Loaded {len(selected_ids)} missing IDs.")
    for arxiv_id in selected_ids:
        id_queue.put(arxiv_id)
    for _ in range(DOWNLOAD_THREAD_COUNT):
        id_queue.put(None)
# ...existing code...

def download_with_retries(client, arxiv_id, max_retries=5):
    """Try downloading paper metadata with exponential backoff for 429/503 errors."""
    for attempt in range(max_retries):
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(client.results(search))
            return result
        except Exception as e:
            error_str = str(e)
            if "HTTP 429" in error_str or "HTTP 503" in error_str:
                wait_time = min(60 * (2 ** attempt), 600)  # exponential backoff (up to 10 min)
                jitter = random.uniform(0, 5)
                print(f"[Download] Server busy ({error_str}). Retrying {arxiv_id} in {wait_time + jitter:.1f}s...")
                time.sleep(wait_time + jitter)
                continue
            else:
                raise  # rethrow unexpected errors
    raise RuntimeError(f"[Download] Failed after {max_retries} retries for {arxiv_id}")


def download_worker(id_queue, base_data_dir, delay=2):
    client = arxiv.Client()
    processed = 0
    while True:
        arxiv_id = id_queue.get()
        if arxiv_id is None:
            # Signal that this download thread is done
            print(f"[Download] Thread finished. Total papers downloaded: {processed}")
            id_queue.task_done()
            break

        try:
            print(f"[Download] Starting: {arxiv_id}")
            result_latest = download_with_retries(client, arxiv_id)

            # Determine latest version number
            version_latest = int(result_latest.get_short_id().split('v')[1])
            list_download = [result_latest]

            # Download older versions
            for v in range(1, version_latest):
                arxiv_id_v = f"{arxiv_id}v{v}"
                result_v = download_with_retries(client, arxiv_id_v)
                list_download.append(result_v)

            # Extract & clean
            download(list_download, base_data_dir)
            processed += 1
            print(f"[Download] Finished: {arxiv_id} (Total: {processed})")
            # download_queue.put(arxiv_id)  # Commented out - no reference processing
            time.sleep(delay)  # Respect API rate

        except Exception as e:
            print(f"[Download] Error for {arxiv_id}: {e}")
        finally:
            id_queue.task_done()


def reference_worker(download_queue, base_data_dir, delay=2):
    processed = 0
    while True:
        arxiv_id = download_queue.get()
        if arxiv_id is None:
            print(f"[Reference] Thread finished. Total papers processed: {processed}")
            download_queue.task_done()
            break
        try:
            print(f"[Reference] Starting: {arxiv_id}")
            extract_references_for_paper(arxiv_id, base_data_dir)
            processed += 1
            print(f"[Reference] Finished: {arxiv_id} (Total: {processed})")
            time.sleep(delay)
        except Exception as e:
            print(f"[Reference] Error for {arxiv_id}: {e}")
        finally:
            download_queue.task_done()

if __name__ == "__main__":
    start_month = 3
    start_year = 2023
    start_ID = 7856
    end_month = 4
    end_year = 2023
    end_ID = 4606
    base_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "23127130"))
    os.makedirs(base_data_dir, exist_ok=True)

    # Ignore range counts; process only missing IDs
    start_index = 0
    num_papers = len(MISSING_TAILS)

    DOWNLOAD_THREAD_COUNT = 5

    REFERENCE_THREAD_COUNT = 2  # Not used currently - references disabled

    print("="*60)
    print("MISSING PAPERS RECOVERY PIPELINE")
    print("="*60)
    print(f"Papers to process: {num_papers} missing papers")
    print(f"Download threads: {DOWNLOAD_THREAD_COUNT}")
    # print(f"Reference threads: {REFERENCE_THREAD_COUNT}")  # References disabled
    print("⚠️  References extraction is DISABLED")
    print("="*60)

    # Use larger queue sizes to avoid blocking
    id_queue = queue.Queue(maxsize=num_papers + DOWNLOAD_THREAD_COUNT)
    # download_queue = queue.Queue(maxsize=num_papers + REFERENCE_THREAD_COUNT)  # Not needed - references disabled

    start_time = time.time()
    print("Starting pipeline for missing IDs...")

    # Step 1: Start ID fetcher
    t1 = threading.Thread(target=fetch_ids_worker, args=(
        start_month, start_year, start_ID, end_month, end_year, end_ID, start_index, num_papers, id_queue))
    t1.start()

    # Step 2: Start download threads
    download_threads = []
    for i in range(DOWNLOAD_THREAD_COUNT):
        t = threading.Thread(target=download_worker, args=(id_queue, base_data_dir, 2))
        t.daemon = False
        t.start()
        download_threads.append(t)

    # Step 3: Start reference threads (DISABLED)
    # reference_threads = []
    # for i in range(REFERENCE_THREAD_COUNT):
    #     t = threading.Thread(target=reference_worker, args=(download_queue, base_data_dir, 2))
    #     t.daemon = False
    #     t.start()
    #     reference_threads.append(t)

    # Wait for ID fetcher to complete
    print("Waiting for ID fetcher to complete...")
    t1.join()
    print("ID fetcher completed.")

    # Wait for all download threads to complete
    print("Waiting for download threads to complete...")
    for t in download_threads:
        t.join()
    print("All download threads completed.")

    # Reference processing is DISABLED
    # # Signal reference threads to stop
    # for _ in range(REFERENCE_THREAD_COUNT):
    #     download_queue.put(None)

    # # Wait for reference threads to complete
    # print("Waiting for reference threads to complete...")
    # for t in reference_threads:
    #     t.join()
    # print("All reference threads completed.")

    end_time = time.time()
    print("\n" + "="*60)
    print("MISSING PAPERS RECOVERY COMPLETE")
    print("="*60)
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print("⚠️  Note: References extraction was DISABLED")
    print("="*60)