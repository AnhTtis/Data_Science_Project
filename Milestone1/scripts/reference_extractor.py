import requests
import json
import os
import time
import re
from arXiv_handler import format_arxiv_id_for_key


# def sanitize_bibtex_key(title, arxiv_id=None):
#     """
#     Generate a valid BibTeX citation key from title or arxiv_id.
#     Format: FirstWord + Year (if available) or arxiv_id
#     """
#     if arxiv_id:
#         # Clean arxiv_id to use as key
#         return re.sub(r'[^\w]', '_', arxiv_id)
    
#     if not title:
#         return "unknown"
    
#     # Take first word of title and remove special characters
#     words = title.split()
#     if words:
#         first_word = re.sub(r'[^\w]', '', words[0])
#         return first_word[:20]  # Limit length
#     return "unknown"


def format_authors_bibtex(authors):
    """
    Format authors list for BibTeX format.
    Input: list of author names
    Output: "Author1 and Author2 and Author3"
    """
    if not authors:
        return ""
    return " and ".join(authors)


# def convert_to_bibtex(reference, index):
#     """
#     Convert a single reference from Semantic Scholar to BibTeX format.
    
#     Args:
#         reference: dict containing reference data from Semantic Scholar API
#         index: integer index for numbering the reference
    
#     Returns:
#         str: BibTeX entry as string
#     """
#     # Skip if reference is None or empty
#     if not reference:
#         return f"% Reference {index}: No data available"
    
#     # Extract basic information directly from reference
#     title = reference.get("title", "Untitled")
#     authors = reference.get("authors", [])
#     year = reference.get("year", "")
#     venue = reference.get("venue", "")
#     external_ids = reference.get("externalIds", {})
    
#     # Handle None external_ids
#     if external_ids is None:
#         external_ids = {}
    
#     # Determine entry type and citation key
#     arxiv_id = external_ids.get("ArXiv", "")
#     doi = external_ids.get("DOI", "")
    
#     if arxiv_id:
#         entry_type = "article"
#         citation_key = sanitize_bibtex_key(None, arxiv_id)
#     elif doi:
#         entry_type = "article"
#         citation_key = sanitize_bibtex_key(title) + f"_{index}"
#     else:
#         entry_type = "misc"
#         citation_key = sanitize_bibtex_key(title) + f"_{index}"
    
#     # Format authors
#     if authors is None:
#         authors = []
#     author_names = [author.get("name", "") for author in authors if author and author.get("name")]
#     author_str = format_authors_bibtex(author_names)
    
#     # Build BibTeX entry
#     bibtex_lines = [f"@{entry_type}{{{citation_key},"]
    
#     if title:
#         bibtex_lines.append(f'  title = {{{title}}},')
#     if author_str:
#         bibtex_lines.append(f'  author = {{{author_str}}},')
#     if year:
#         bibtex_lines.append(f'  year = {{{year}}},')
#     if venue:
#         bibtex_lines.append(f'  journal = {{{venue}}},')
#     if doi:
#         bibtex_lines.append(f'  doi = {{{doi}}},')
#     if arxiv_id:
#         bibtex_lines.append(f'  eprint = {{{arxiv_id}}},')
#         bibtex_lines.append(f'  archivePrefix = {{arXiv}},')
    
#     bibtex_lines.append("}")
    
#     return "\n".join(bibtex_lines)


def get_paper_references(arxiv_id, delay=2):
    """
    Fetch references for a paper from Semantic Scholar API.
    
    Args:
        arxiv_id: arXiv ID (format: YYMM.NNNNN or YYMM.NNNNNvN)
        retry: number of retry attempts
        delay: delay between retries in seconds
    
    Returns:
        list: List of references with detailed information
    """
    # Clean arxiv_id (remove version suffix if present)
    clean_id = re.sub(r'v\d+$', '', arxiv_id)
    url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{clean_id}"
    params = {
        "fields": "references,references.title,references.authors,references.year,references.venue,references.externalIds,references.publicationDate"
    }

    while True:
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("references", [])
            elif response.status_code == 429:
                print(f"  Rate limit hit. Waiting {delay}s before retry...")
                time.sleep(delay)
            elif response.status_code == 404:
                print(f"  Paper {arxiv_id} not found in Semantic Scholar")
                return []
            else:
                print(f"  API returned status {response.status_code}, retrying in {delay}s...")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}, retrying in {delay}s...")
            time.sleep(delay)
    print(f"  Failed to fetch references after {retry} attempts")
    return []


def convert_to_references_dict(references):
    """
    Convert Semantic Scholar references to the required format:
    Dictionary with arXiv IDs as keys (in "yyyymm-id" format) for papers with arXiv IDs.
    For papers without arXiv IDs, use DOI or generate a unique key.
    
    Args:
        references: List of references from Semantic Scholar API
    
    Returns:
        dict: Dictionary with paper IDs as keys and metadata as values
    """
    result = {}
    non_arxiv_counter = 1
    
    for ref in references:
        # The reference data is directly in ref, not under "citedPaper"
        
        # Skip if reference is None or empty
        if not ref:
            continue
        
        # Extract external IDs (may be None)
        external_ids = ref.get("externalIds", {})
        if external_ids is None:
            external_ids = {}
        
        arxiv_id = external_ids.get("ArXiv", "")
        doi = external_ids.get("DOI", "")
        # Only keep references that have arXiv_id
        if not arxiv_id:
            continue
        
        # Determine the key for this reference
        if arxiv_id:
            # Use arXiv ID in yyyymm-id format
            key = format_arxiv_id_for_key(arxiv_id)
        elif doi:
            # Use DOI as key (sanitize it)
            key = f"doi:{doi.replace('/', '_')}"
        else:
            # Generate a unique key for papers without arXiv ID or DOI
            title = ref.get("title", "")
            if title:
                # Use first word of title + counter
                first_word = re.sub(r'[^\w]', '', title.split()[0] if title.split() else "unknown")
                key = f"ref_{first_word[:20]}_{non_arxiv_counter}"
            else:
                key = f"ref_unknown_{non_arxiv_counter}"
            non_arxiv_counter += 1
        
        # Extract authors
        authors_list = ref.get("authors", [])
        authors = [author.get("name", "") for author in authors_list if author.get("name")]
        
        # Extract dates (use publicationDate if available)
        publication_date = ref.get("publicationDate", "")
        year = ref.get("year")
        
        # If no publication date but have year, create an ISO-like format
        if not publication_date and year:
            publication_date = f"{year}-01-01"  # Use Jan 1st as placeholder
        
        # Build metadata dictionary with required fields
        metadata = {
            "title": ref.get("title", ""),
            "authors": authors,
            "submission_date": publication_date if publication_date else "",
            "revised_dates": []  # Semantic Scholar doesn't provide revision history
        }
        
        # Add optional fields for reference
        if doi:
            metadata["doi"] = doi
        if arxiv_id:
            metadata["arxiv_id"] = arxiv_id
        if ref.get("venue"):
            metadata["venue"] = ref.get("venue")
        if year:
            metadata["year"] = year
        
        result[key] = metadata
    
    return result


def save_references(arxiv_id, paper_folder, verbose=True):
    """
    Fetch and save references for a paper version to both JSON and BibTeX formats.
    
    Args:
        arxiv_id: arXiv ID (e.g., "2304.07856v1")
        version_folder: Path to version folder (e.g., "data/2304.07856/v1/")
        verbose: Whether to print progress messages
    
    Returns:
        bool: True if successful, False otherwise
    """
    if verbose:
        print(f"Fetching references for {arxiv_id}...")
    
    references = get_paper_references(arxiv_id)
    
    if not references:
        if verbose:
            print(f"  No references found for {arxiv_id}")
        # Create empty files to indicate we tried
        json_path = os.path.join(paper_folder, "references.json")
        # bib_path = os.path.join(paper_folder_folder, "references.bib")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
        
        # with open(bib_path, 'w', encoding='utf-8') as f:
        #     f.write("% No references found\n")
        
        return False
    
    # Prepare paths
    json_path = os.path.join(paper_folder, "references.json")
    # bib_path = os.path.join(version_folder, "references.bib")
    
    # Convert to required dictionary format
    references_dict = convert_to_references_dict(references)
    
    # Save JSON format (dictionary with arXiv IDs as keys)
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(references_dict, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"  Saved {len(references_dict)} references to references.json")
    except Exception as e:
        print(f"  Error saving JSON: {e}")
        return False
    
    # # Convert to BibTeX and save
    # try:
    #     bibtex_entries = []
    #     for idx, ref in enumerate(references, start=1):
    #         bibtex_entry = convert_to_bibtex(ref, idx)
    #         bibtex_entries.append(bibtex_entry)
        
    #     with open(bib_path, 'w', encoding='utf-8') as f:
    #         f.write("\n\n".join(bibtex_entries))
        
    #     if verbose:
    #         print(f"  Saved {len(bibtex_entries)} references to references.bib")
    #     return True
    # except Exception as e:
    #     print(f"  Error saving BibTeX: {e}")
    #     return False


def extract_references_for_paper(paper_id, base_data_dir="../data"):
    """
    Extract references for all versions of a paper.
    
    Args:
        paper_id: arXiv paper ID without version (e.g., "2304.07856")
        base_data_dir: Base directory containing data folders
    
    Returns:
        dict: Statistics about the extraction
    """
    paper_id_key = format_arxiv_id_for_key(paper_id)
    paper_folder = os.path.join(base_data_dir, paper_id_key)
    
    # if not os.path.exists(paper_folder):
    #     print(f"Paper folder not found: {paper_folder}")
    #     return {"success": 0, "failed": 0, "total": 0}
    
    # stats = {"success": 0, "failed": 0, "total": 0}
    
    # # Find all version folders
    # version_folders = [d for d in os.listdir(paper_folder) 
    #                   if os.path.isdir(os.path.join(paper_folder, d)) and d.startswith("v")]
    
    # version_folders.sort(key=lambda x: int(x[1:]))  # Sort by version number
    
    # for version_dir in version_folders:
    #     version_num = version_dir[1:]  # Extract version number
    #     version_path = os.path.join(paper_folder, version_dir)
    #     arxiv_id_with_version = f"{paper_id}v{version_num}"
        
    #     stats["total"] += 1
        
    #     print(f"\nProcessing {arxiv_id_with_version}...")
        
    #     if save_references(arxiv_id_with_version, version_path):
    #         stats["success"] += 1
    #     else:
    #         stats["failed"] += 1
        
    #     # Be nice to the API
    #     time.sleep(1)
    save_references(paper_id, os.path.join(paper_folder))
    
    # return stats


# def batch_extract_references(base_data_dir="../data"):
#     """
#     Extract references for all papers in the data directory.
    
#     Args:
#         base_data_dir: Base directory containing paper folders
#     """
#     if not os.path.exists(base_data_dir):
#         print(f"Data directory not found: {base_data_dir}")
#         return
    
#     # Get all paper folders
#     paper_folders = [d for d in os.listdir(base_data_dir) 
#                     if os.path.isdir(os.path.join(base_data_dir, d)) 
#                     and re.match(r'^\d{4}\.\d{5}$', d)]
    
#     paper_folders.sort()
    
#     print(f"Found {len(paper_folders)} paper folders")
#     print("=" * 60)
    
#     total_stats = {"success": 0, "failed": 0, "total": 0}
    
#     for idx, paper_id in enumerate(paper_folders, start=1):
#         print(f"\n[{idx}/{len(paper_folders)}] Processing paper {paper_id}")
#         stats = extract_references_for_paper(paper_id, base_data_dir)
        
#         total_stats["success"] += stats["success"]
#         total_stats["failed"] += stats["failed"]
#         total_stats["total"] += stats["total"]
        
#         # Progress update
#         print(f"  Paper stats: {stats['success']}/{stats['total']} versions successful")
    
#     print("\n" + "=" * 60)
#     print("EXTRACTION COMPLETE")
#     print(f"Total versions processed: {total_stats['total']}")
#     print(f"Successful: {total_stats['success']}")
#     print(f"Failed: {total_stats['failed']}")
#     print(f"Success rate: {total_stats['success']/max(total_stats['total'],1)*100:.1f}%")


# if __name__ == "__main__":
#     # Example usage
#     import sys
    
#     if len(sys.argv) > 1:
#         # Process specific paper: python reference_extractor.py 2304.07856
#         paper_id = sys.argv[1]
#         extract_references_for_paper(paper_id)
#     else:
#         # Process all papers in data directory
#         batch_extract_references()