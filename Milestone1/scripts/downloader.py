import os
import re
import arxiv
import tarfile
from arXiv_handler import format_arxiv_id_for_key
from metadata_collector import save_metadata


def safe_extract_tar(tar_path: str, extract_to: str) -> None:
    """Safely extract a tar.gz file using filter='data'."""
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_to, filter="data")
    except Exception as e:
        print(f"Extraction error in {tar_path}: {e}")
        raise


def cleanup_non_tex_bib_files(folder: str) -> None:
    """Remove all non-.tex and non-.bib files."""
    for root, _, files in os.walk(folder):
        for file in files:
            if not (file.endswith(".tex") or file.endswith(".bib")):
                try:
                    os.remove(os.path.join(root, file))
                except OSError as e:
                    print(f"Warning: could not remove {file}: {e}")


def download(list_download: list[arxiv.Result], base_dir: str) -> None:
    """
    Downloads all versions of an arXiv paper, extracts .tex/.bib,
    and creates separate .bib files from embedded bibliographies if needed.
    Handles download and extraction errors robustly.
    """
    if not list_download:
        print("⚠️ list_download is empty — skipping.")
        return

    match = re.match(r"^(\d{4}\.\d{5})", list_download[0].get_short_id())
    if not match:
        print(f"Invalid arXiv ID format: {list_download[0].get_short_id()}")
        return

    arxiv_id = match.group(1)
    folder_arxiv = os.path.join(base_dir, format_arxiv_id_for_key(arxiv_id))
    print(f"Processing {arxiv_id} → {folder_arxiv}")

    for result in list_download:
        folder_version = os.path.join(folder_arxiv, result.get_short_id())
        os.makedirs(folder_version, exist_ok=True)

        try:
            tar_path = result.download_source(dirpath=folder_version)
        except Exception as e:
            print(f"[Error] No source for {result.get_short_id()}: {e}")
            tar_path = None

        if tar_path and os.path.exists(tar_path) and tar_path.endswith('.tar.gz') and os.path.getsize(tar_path) > 1024:
            try:
                safe_extract_tar(tar_path, folder_version)
            except Exception as e:
                print(f"[Error] Extraction failed for {tar_path}: {e}")

            try:
                os.remove(tar_path)
            except Exception as e:
                print(f"[Error] Removing {tar_path}: {e}")

            cleanup_non_tex_bib_files(folder_version)
        else:
            print(f"[Info] No valid source file for extraction: {result.get_short_id()}")

    save_metadata(result, folder_arxiv)
