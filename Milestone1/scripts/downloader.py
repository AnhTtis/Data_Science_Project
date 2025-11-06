import os
import re
import json
import arxiv
from sickle import Sickle
import tarfile
import chardet

def extract_and_clean_source(tar_path: str, extract_dir: str):
    """
    Extract an arXiv source .tar.gz file into the same directory, remove all figure/image files,
    delete the original archive, and verify extraction integrity.

    Args:
        tar_path (str): Full path to source.tar.gz
        extract_dir (str): Directory where the archive should be extracted

    Behavior:
        - Extracts all files from the archive into extract_dir.
        - Removes any figure/image files (.png, .pdf, .jpg, .eps, etc.).
        - Deletes the .tar.gz after successful extraction.
        - Prints detected encodings for remaining text files.
        - Verifies extracted file count for sanity check.
    """
    if not os.path.exists(tar_path):
        print(f"⚠️ File not found: {tar_path}")
        return

    # --- 1️⃣ Open and inspect archive ---
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            members = tar.getmembers()
            total_files = len(members)
            tar.extractall(path=extract_dir)
        print(f"📦 Extracted {total_files} files from {os.path.basename(tar_path)}")
    except Exception as e:
        print(f"❌ Extraction failed for {tar_path}: {e}")
        return

    # --- 2️⃣ Remove figure/image files ---
    figure_exts = {
        # raster formats
        ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".webp",
        # vector and PDF-based figures
        ".pdf", ".eps", ".ps", ".svg", ".ai",
        # misc formats occasionally found
        ".ico", ".heic", ".heif", ".jp2"
    }

    removed_count = 0
    extracted_files = 0
    for root, _, files in os.walk(extract_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            fpath = os.path.join(root, fname)
            if ext in figure_exts:
                os.remove(fpath)
                removed_count += 1
            else:
                extracted_files += 1

    print(f"🧹 Removed {removed_count} figure/image files")
    print(f"📁 Remaining {extracted_files} non-image files after cleanup")

    # --- 3️⃣ Detect encoding for remaining text files (optional check) ---
    for root, _, files in os.walk(extract_dir):
        for fname in files:
            path = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()
            if ext not in figure_exts:
                try:
                    with open(path, "rb") as f:
                        raw = f.read(4096)
                    enc = chardet.detect(raw)["encoding"]
                    print(f"📄 {os.path.relpath(path, extract_dir)} → {enc}")
                except Exception:
                    pass

    # --- 4️⃣ Delete the archive after successful extraction ---
    try:
        os.remove(tar_path)
        print(f"🗑️ Deleted archive: {os.path.basename(tar_path)}")
    except Exception as e:
        print(f"⚠️ Could not delete archive: {e}")

    # --- 5️⃣ Verify extraction sanity ---
    if extracted_files == 0:
        print(f"⚠️ Warning: No non-image files found after extraction in {extract_dir}")
    else:
        print(f"✅ Extraction and cleanup complete: {extract_dir}")


def get_oai_metadata(arxiv_id: str):
    """
    Fetch OAI-PMH metadata for a given arXiv ID (without saving to file).
    Returns: dict
    """
    sickle = Sickle("https://export.arxiv.org/oai2")
    oai_identifier = f"oai:arXiv.org:{arxiv_id}"

    try:
        record = sickle.GetRecord(identifier=oai_identifier, metadataPrefix="arXiv")
        return record.metadata
    except Exception as e:
        print(f"⚠️ OAI fetch failed for {arxiv_id}: {e}")
        return {"error": str(e)}


# def merge_metadata(api_result, oai_metadata):
#     """
#     Merge arXiv API and OAI-PMH metadata into a unified dict
#     that meets the project’s metadata.json requirements.
#     """

#     # --- Extract dates ---
#     # OAI: "created" -> submission, "updated" -> revisions
#     submission_date = None
#     revised_dates = []

#     if "created" in oai_metadata and oai_metadata["created"]:
#         submission_date = oai_metadata["created"][0]
#     elif hasattr(api_result, "published"):
#         submission_date = api_result.published.strftime("%Y-%m-%dT%H:%M:%SZ")

#     if "updated" in oai_metadata:
#         revised_dates = oai_metadata["updated"]

#     # --- Authors ---
#     authors = []
#     if hasattr(api_result, "authors") and api_result.authors:
#         authors = [a.name for a in api_result.authors]
#     else:
#         fn = oai_metadata.get("forenames", [])
#         kn = oai_metadata.get("keyname", [])
#         authors = [f"{f} {k}".strip() for f, k in zip(fn, kn)]

#     # --- Publication info ---
#     publication_venue = None
#     if "journal-ref" in oai_metadata and oai_metadata["journal-ref"]:
#         publication_venue = oai_metadata["journal-ref"][0]
#     elif getattr(api_result, "journal_ref", None):
#         publication_venue = api_result.journal_ref

#     # --- DOI ---
#     doi = None
#     if "doi" in oai_metadata and oai_metadata["doi"]:
#         doi = oai_metadata["doi"][0]
#     elif getattr(api_result, "doi", None):
#         doi = api_result.doi

#     # --- Build the merged metadata ---
#     merged = {
#         "title": (
#             oai_metadata.get("title", [api_result.title])[0]
#             if "title" in oai_metadata
#             else api_result.title
#         ).strip(),
#         "authors": authors,
#         "submission_date": submission_date,
#         "revised_dates": revised_dates,
#         "publication_venue": publication_venue,
#         "doi": doi,
#         "arxiv_id": api_result.get_short_id(),
#         "primary_category": getattr(api_result, "primary_category", None),
#         "categories": api_result.categories,
#         "comment": (
#             oai_metadata.get("comments", [getattr(api_result, "comment", None)])[0]
#             if "comments" in oai_metadata
#             else getattr(api_result, "comment", None)
#         ),
#         "summary": (
#             oai_metadata.get("abstract", [api_result.summary])[0]
#             if "abstract" in oai_metadata
#             else api_result.summary
#         ).strip(),
#         "entry_id": api_result.entry_id,
#         "pdf_url": api_result.pdf_url,
#         "source_url": f"https://arxiv.org/src/{api_result.get_short_id()}.tar.gz"
#     }

#     return merged

def download(arxiv_id: str):
    """
    Create folders for all versions of a known arXiv ID (e.g. '2312.09876v3'),
    then download each version's PDF, source, and metadata as JSON.
    """
    # --- 1️⃣ Base paths ---
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    # --- 2️⃣ Parse ID and latest version ---
    match = re.match(r"^(\d{4}\.\d{5})v(\d+)$", arxiv_id)
    if not match:
        raise ValueError(f"Invalid arXiv ID format: {arxiv_id} (expected like '2312.09876v3')")
    
    main_id, latest_v = match.groups()
    latest_v = int(latest_v)

    print(f"📦 Preparing folders for {main_id} (up to v{latest_v})")

    paper_folder = os.path.join(base_dir, main_id)
    os.makedirs(paper_folder, exist_ok=True)

    client = arxiv.Client()

    # --- 3️⃣ Loop through all versions 1..vN ---
    for v in range(1, latest_v + 1):
        vid = f"{main_id}v{v}"
        ver_folder = os.path.join(paper_folder, f"v{v}")
        os.makedirs(ver_folder, exist_ok=True)

        print(f"📥 Downloading {vid} ...")

        try:
            search = arxiv.Search(id_list=[vid])
            result = next(client.results(search))

            # --- 4️⃣ Download files ---
            result.download_pdf(dirpath=ver_folder, filename="paper.pdf")
            result.download_source(dirpath=ver_folder, filename="source.tar.gz")
            extract_and_clean_source(
                tar_path=os.path.join(ver_folder, "source.tar.gz"),
                extract_dir=ver_folder
            )

            # # --- 5️⃣ Save metadata to JSON ---
            # oai_meta = get_oai_metadata(vid)
            # meta = merge_metadata(result, oai_meta)
        
            # json_path = os.path.join(ver_folder, "metadata.json")
            # with open(json_path, "w", encoding="utf-8") as f:
            #     json.dump(meta, f, indent=4, ensure_ascii=False)

            print(f"✅ Saved {vid} → {ver_folder}")

        except StopIteration:
            print(f"❌ Version {vid} not found (maybe withdrawn).")
        except Exception as e:
            print(f"⚠️ Error downloading {vid}: {e}")

    print(f"\n🎯 Completed {main_id} (v1 → v{latest_v}).")