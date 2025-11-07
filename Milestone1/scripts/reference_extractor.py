# import os
# import re
# import time
# import json
# import requests
# import arxiv


# SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}"
# RATE_LIMIT_DELAY = 1.1  # seconds between requests to stay under 1 req/s


# def get_paper_references(arxiv_id: str):
#     """
#     Query Semantic Scholar for references of a given arXiv paper.
#     Follows the structure in Section 2.3.1 of the documentation.
#     """
#     #base = arxiv_id.split("v")[0]  # strip version suffix
#     url = SEMANTIC_SCHOLAR_API.format(arxiv_id=arxiv_id)
#     params = {"fields": "references,references.externalIds,references.title,references.year,references.authors,references.venue,references.doi"}
#     try:
#         resp = requests.get(url, params=params)
#         if resp.status_code == 429:
#             print("⚠️ Rate limit reached — waiting 10 s...")
#             time.sleep(10)
#             return get_paper_references(arxiv_id)
#         resp.raise_for_status()
#         data = resp.json()
#         return data.get("references", [])
#     except Exception as e:
#         print(f"⚠️ Failed to query Semantic Scholar for {arxiv_id}: {e}")
#         return []


# def get_arxiv_metadata(arxiv_id: str):
#     """
#     Retrieve title, authors, submission, and revision dates for an arXiv paper.
#     """
#     client = arxiv.Client()
#     search = arxiv.Search(id_list=[arxiv_id])
#     try:
#         result = next(client.results(search))
#     except StopIteration:
#         return None
#     except Exception as e:
#         print(f"⚠️ arXiv fetch failed for {arxiv_id}: {e}")
#         return None

#     return {
#         "title": result.title.strip(),
#         "authors": [a.name for a in result.authors],
#         "submission_date": result.published.strftime("%Y-%m-%d"),
#         "revised_dates": [result.updated.strftime("%Y-%m-%d")] if result.updated else []
#     }


# def build_references(arxiv_id: str, output_dir: str = "."):
#     """
#     Build references.json and references.bib for all arXiv references of a given paper.
#     Implements rate-limit compliance and missing-ID handling (Section 2.3.3).
#     """
#     os.makedirs(output_dir, exist_ok=True)

#     references = get_paper_references(arxiv_id)
#     all_meta = {}
#     bib_entries = []

#     for ref in references:
#         cited = ref.get("citedPaper", ref)  # handle variations in field nesting
#         ext_ids = cited.get("externalIds", {}) if cited else {}
#         arxiv_ref = ext_ids.get("ArXiv")

#         if not arxiv_ref:
#             # Skip non-arXiv references (journals, books, etc.)
#             continue

#         title = cited.get("title", "")
#         doi = cited.get("doi", "")
#         year = cited.get("year", "")
#         venue = cited.get("venue", "")
#         authors = [a["name"] for a in cited.get("authors", [])]

#         time.sleep(RATE_LIMIT_DELAY)  # obey 1 req/s limit
#         meta = get_arxiv_metadata(arxiv_ref)
#         if not meta:
#             meta = {
#                 "title": title,
#                 "authors": authors,
#                 "submission_date": None,
#                 "revised_dates": []
#             }

#         # Normalize arXiv ID to "yyyymm-id"
#         key = re.sub(r"^(\d{4})\.(\d{5})v?\d*$", r"\1-\2", arxiv_ref)

#         all_meta[key] = meta

#         # Build BibTeX entry
#         authors_bib = " and ".join(authors)
#         bib = f"""@article{{{key},
#   title = {{{title}}},
#   author = {{{authors_bib}}},
#   journal = {{{venue}}},
#   year = {{{year}}},
#   doi = {{{doi or ""}}}
# }}"""
#         bib_entries.append(bib)

#     # Write outputs
#     json_path = os.path.join(output_dir, "references.json")
#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(all_meta, f, ensure_ascii=False, indent=4)

#     bib_path = os.path.join(output_dir, "references.bib")
#     with open(bib_path, "w", encoding="utf-8") as f:
#         f.write("\n\n".join(bib_entries))

#     print(f"✅ Saved {len(all_meta)} arXiv references:")
#     print(f"   - JSON → {json_path}")
#     print(f"   - BibTeX → {bib_path}")


# if __name__ == "__main__":
#     # Example usage
#     test_id = "2303.07856v1"  # Replace with any valid arXiv ID
#     build_references(test_id, output_dir=".")
