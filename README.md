# Data_Science_Project

*A Multi-Milestone Data Science Project*

---

## 🧭 Overview

- This project is part of the **Introduction to Data Science** course offered by the **Department of Computer Science, University of Science (VNU-HCMC)**.

- The first milestone focuses on **data scraping engineering** — transforming theoretical knowledge of data crawling into practical implementation by harvesting academic papers from **arXiv**, an open-access scientific repository.

---

## 👨‍💻 Team Members

| Name                   | Student ID | 
| ---------------------- | ---------- | 
| **Nguyễn Hữu Anh Trí** | 23127130   | 
| **Nguyễn Huy Quân**    | 23127107   | 
| **Cao Tấn Hoàng Huy**  | 23127051   | 

---

## 🎯 Milestone 1: Data Scraping and Repository Engineering

Milestone 1 enables students to:

* Implement **multi-threaded web scraping** techniques to retrieve structured data at scale and  understand the **engineering workflow** of building a data collection pipeline from open APIs.
* Practice handling **large datasets** and **metadata organization**.
* Integrate and synchronize multiple data sources: **arXiv API**, **OAI-PMH**, **Semantic Scholar API**, and **Kaggle dataset**.

---

## ⚙️ Tools and Technologies

| Tool / Library                   | Purpose                                                            |
| -------------------------------- | ------------------------------------------------------------------ |
| **arXiv API**                    | Retrieve paper metadata, version history, and source URLs          |
| **OAI-PMH (Sickle library)**     | Harvest bulk metadata for large-scale retrieval                    |
| **Semantic Scholar Graph API**   | Extract paper references, citation graphs, and related identifiers |
| **Kaggle Cornell ArXiv Dataset** | Pre-aggregated metadata for local data exploration                 |
| **Python threading & requests**  | Concurrent download and network request handling                   |
| **pandas / json / os**           | Data transformation, storage, and management                       |

---

## 🧵 Multi-Threaded Data Pipeline

To ensure efficiency and scalability, the pipeline employs **four concurrent threads**, each managing a critical phase of the data scraping workflow:

1. **Thread 1 – Entry Discovery**

   * Uses the **arXiv API** and **OAI-PMH** to collect all assigned **arXiv IDs**.
   * Initializes folder structures for each paper in the format `yyyymm-id/`.

2. **Thread 2 – Metadata Retrieval**

   * Queries all available versions of each paper.
   * Extracts title, authors, submission/revision dates, and venue.
   * Stores results as structured **`metadata.json`** files.

3. **Thread 3 – Full-Text Download**

   * Retrieves `.tar.gz` LaTeX sources (via `arxiv.py` or `arxiv-downloader`) and corresponding PDFs.
   * Handles file integrity and version tracking within the `tex/` subdirectory.
   * Removes figure files to reduce data size, as per course requirements.

4. **Thread 4 – Reference Extraction**

   * Fetches **BibTeX** entries and **external identifiers** (DOI, ArXiv ID) via **Semantic Scholar API**.
   * Saves structured references to `references.json` and citation data to `references.bib`.

This modularized and concurrent design supports fault isolation, improved runtime performance, and higher throughput for large datasets.

---

## 📂 Project Structure

The folder hierarchy follows the required format from the course guideline:

```
Data_Scince_Project/
│
├── README.md                                   # Main project documentation
│
└── Milestone1/
    │
    ├── data/                                   # Main data repository
    │   ├── 232303-07857/                         # Folder named after an arXiv ID (yyyymm-id)
    │   │   ├── 2303.07857v1/                             # Subfolder for version 1 of the paper
    │   │   │   ├── paper_2310-12345v1.tex
    │   │   │   └── references.bib
    │   │   ├── v2/                             # Version 2, same structure
    │   │   │   ├── paper_2310-12345v2.tex
    │   │   │   ├── references.json
    │   │   │   └── references.bib
    │   │   ├── metadata.json
    │   │   │── references.json
    │   ├── 232303-07858/
    │   │   ├── v1/
    │   │   │   ├── paper_2310-12678v1.tex
    │   │   │   └── references.bib
    │   │   │── metadata.json
    │   │   │── references.json
    │   │
    │   └── ...                                 # Additional arXiv paper folders
    │
    ├── scripts/                                # Source code and automation modules
    │   ├── main.py                             # Entry point to run the complete pipeline
    │   ├── arxiv_handler.py                    # Handles API queries, ID retrieval, folder creation
    │   ├── downloader.py                       # Downloads .tar.gz sources and PDFs
    │   ├── metadata_collector.py               # Retrieves metadata for all versions
    │   ├── reference_extractor.py              # Collects references from Semantic Scholar
    │
    ├── Milestone1_Report.pdf                   # Single official report file (methodology & performance)
    │
    ├── Milestone1_Demo_Video.mp4               # Single 2-minute demo video
    │
    └──requirements.txt                        # Python dependencies

```

---

## 🧰 Environment Setup

**Requirements:**

* Python ≥ 3.9
* Internet connection (for API requests)
* Recommended libraries:

```bash
pip install -r requirements.txt
```

**Run Command Example:**

```bash
python scripts/main.py
```
---

## 📊 Evaluation Metrics

Each scraper execution is evaluated using the following criteria (as required by the course specification):

| Category              | Metric                                       |
| --------------------- | -------------------------------------------- |
| **Data Completeness** | Number of papers scraped successfully        |
| **Metadata Coverage** | Ratio of successfully retrieved JSON entries |
| **Performance**       | Average runtime and memory footprint         |
| **Data Efficiency**   | Storage reduction after removing figures     |
| **Quality**           | Correctness of references and file structure |

---

## 🧾 Deliverables

* **Source Code:** All `.py` files organized under `scripts/` and `src/`.
* **Dataset:** Compressed `.zip` following the naming rule `<StudentID>.zip`.
* **Report:** Technical report detailing implementation and performance analysis.
* **Demo Video:** 2-minute demonstration of system execution and explanation.

---

## 📚 References

1. Waleed Ammar et al., *The Semantic Scholar Open Research Corpus*, [arXiv:1805.02234](https://arxiv.org/abs/1805.02234)
2. [arXiv API Basics](https://info.arxiv.org/help/api/basics.html)
3. [OAI-PMH Protocol](https://info.arxiv.org/help/oa/index.html)
4. [Semantic Scholar Graph API](https://api.semanticscholar.org/api-docs/graph)
5. [Cornell University ArXiv Dataset on Kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv)
6. [arxiv-downloader GitHub Repository](https://github.com/braun-steven/arxiv-downloader)
7. [arxiv.py Wrapper Library](https://github.com/lukasschwab/arxiv.py)

---

**© 2025 University of Science (VNU-HCMC)**
Developed for **Introduction to Data Science – Milestone 1** under the guidance of **Huỳnh Lâm Hải Đăng**.
