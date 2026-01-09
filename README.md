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

## 🎯 Milestone 2: Hierarchical Parsing and Reference Matching

Milestone 2 transitions from simple data collection to advanced data processing and analysis. The focus is on transforming unstructured raw data (LaTeX sources) into a structured hierarchical format and applying machine learning techniques to match citation entries extracted from the text with external metadata. This practice mimics real-world data science workflows involving unstructured text processing, standardization, feature engineering, and entity resolution/matching algorithms.

### 🗂️ Task 1: Hierarchical Parsing and Standardization

Students are required to implement an automatic parser that processes the scraped LaTeX source files from Milestone 1. The processing pipeline consists of the following components:

#### 1. Multi-file Gathering

LaTeX content is often spread across multiple `.tex` files (e.g., using `\input` or `\include`). Students must programmatically:
* Identify the main compilation path
* Parse only those files that are actually included in the final PDF rendering
* Ignore unused or redundant files found in the source directory

#### 2. Hierarchy Construction

**Hierarchy Structure:** The goal is to convert raw LaTeX code into a hierarchical tree structure for each version of each publication.

* **Document** acts as the root
* **Chapters or Sections** typically comprise the second level
* **Subsections, Paragraphs**, and subsequent logical divisions form the lower levels

The parser must automatically identify the appropriate hierarchical level for each element based on the publication's specific formatting.

**Parsing Rules:**

* **Smallest Elements (Leaf Nodes):**
  * **Sentences** (separated by dots/periods)
  * **Block Formulas** (mathematical blocks such as contents within `equation` environments or `$$...$$`)
  * **Figures** (note that Tables are also considered a type of Figure)
  * Itemized points: `\begin{itemize}...\end{itemize}` blocks are considered higher components with each point being a next-level element

* **Exclusions:** References sections should not be parsed into the hierarchy

* **Inclusions:** Acknowledgements and Appendices (often unnumbered using `\section*`) must be included

#### 3. Standardization and Deduplication

**Cleanup and Normalization:**

* **LaTeX Cleanup:** Remove unnecessary formatting commands (e.g., `\centering`, `[htpb]`, `\midrule`) that do not contribute to semantic meaning
* **Math Normalization:** 
  * Convert all inline mathematics to a unified format (e.g., `$...$`)
  * Convert all block mathematics to a unified format (e.g., `\begin{equation}...\end{equation}`)

**Reference Extraction:**

* For citations defined using `\bibitem` within `.tex` files, convert them into standard BibTeX entries using programmatic tools (e.g., Regular Expressions)

**Deduplication at Two Levels:**

1. **Reference Entries:** 
   * Handle duplicated reference entries inside each version or across different versions
   * If different citation keys refer to the same underlying reference content, choose a single citation key
   * Rename the `\cite{}` commands of remaining entries to this chosen key
   * Unionize the fields of duplicate entries rather than selecting one entry while discarding all other information

2. **Full-text Content:**
   * Apply full-text content deduplication to hierarchical elements
   * If an element's text content matches exactly across different versions (full-text match), represent it by a single identifier in the final output
   * **Note:** Full-text matching should be performed after cleanup to remove discrepancies in minor details (such as formatting or spacing)

### 🤖 Task 2: Reference Matching Pipeline

This task requires performing a matching operation between:
* The references extracted and standardized from Task 1 (BibTeX entries)
* The scraped `references.json` data from Milestone 1

**Goal:** Identify which extracted BibTeX entry corresponds to which arXiv ID (or metadata entry) in the `references.json` file.

Students must perform the full data science pipeline including:
* Data preprocessing and feature engineering
* Model selection and training
* Evaluation and validation
* Entity resolution/matching algorithms

---

**© 2025 University of Science (VNU-HCMC)**  
Developed for **Introduction to Data Science – Milestones 1 & 2** under the guidance of **Huỳnh Lâm Hải Đăng**.

