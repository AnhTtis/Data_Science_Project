# I. Group information 

| Student ID      | Full Name                |
| :-------------- | :----------------------- | 
| **23127130**    | Nguyễn Hữu Anh Trí       |
| **23127107**    | Nguyễn Huy Quân          | 
| **23127051**    | Cao Tấn Hoàng Huy        |  

# II. Summary our work:

## II.1 Achievements:

In this milestone, we have applied data scraping techniques to build a system that collects resources from the **arXiv** open-access repository, including:

* **Resources to Scrape:** Full TeX sources, metadata, and BibTeX/Semantic Scholar reference information for a specified range of arXiv IDs.
* **Version Requirement:** Must collect **all versions** of each paper (e.g., `2310.12345v1`, `v2`, ...).
* **File Handling Note:** Must **REMOVE all image/figure files** from the scraped source data.

---

## II.2. Tools and Methodology

| Function                  | Tool/Library                                            | Description                                                                                                     |
| :------------------------ | :------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------- |
| **ID Detection/Query**    | `arxiv.py`, `get_IDs_All` (Internal function)           | Uses the arXiv API to check ID existence and determine ID ranges across months.                                 |
| **Download Full Sources** | `arxiv.Client().download_source()`, `requests`          | Downloads the `.tar.gz` source archive of all versions of each paper [cite: 93, 121].                           |
| **Reference Extraction**  | Semantic Scholar API                                    | Retrieves citation/reference structures (`references`) and related IDs (e.g., `externalIds` including `ArXiv`). |
| **Parallelization**       | `threading` and `queue`                                 | Uses separate worker threads for **Download** and **Reference Extraction** to speed up execution.               |
| **Rate Limiting**         | Lock mechanism (`threading.Lock`) and `time.sleep(1.0)` | Ensures compliance with Semantic Scholar's 1 request/second limit.                                              |
| **Performance Tracking**  | `psutil` (RAM) and `Benchmark` (internal class)         | Measures runtime, max/avg RAM, and max/final disk usage.                                                        |

---

## II.3. Data folder structure

All data must be organized inside a big folder, can be named by a Student ID  (`23127130`) or customized name (`arxiv_data`).

```
<student_ID> or a customized name/ 
|-- <yymm-id>/ (e.g., 2310-12345)
|   |-- metadata.json           
|   |-- references.json         
|   |-- tex/                    
|       |-- <yymm-id>v<version>/  
|       |   |-- *.tex           
|       |   |-- *.bib           
|       |   |-- <subfolders>/  
|       |-- <yymm-id>v<version>/  
```

---

# III. Setting environment and execution steps

---

## Step 1: Extracting file .zip
From Moodle, we have to dowload a ZIP file **23121730.zip**  (`[student_ID].zip`) and extract it. We can see all the files in the structure below:

```
<student_ID>/ (In this case is 23127130)
|-- src/                      
|   |-- Milestone1.ipynb
|-- requirements.txt         
|-- README.md                 
|-- Report.{docx/tex}         
```
Then we will upload the Jupyter Notebook file (**`Milestone1.ipynb`**) to the Google Colab and we can follow the next steps to excute the program on Google Colab.

---

## Step 2: Setup environment

1. **Open the Notebook** and run the dependency installation (`!pip install...`) and imports.
2. **Connect Google Drive:** The program will automatically request permission to mount Drive. Provide authorization when prompted.
3. **Configure Paths:** Set the persistent data storage directory in Drive:

```python
# Replace {NAME_FOLDER} with the name of the folder you want to store data
base_data_dir = f"/content/drive/MyDrive/{NAME_FOLDER}"
os.makedirs(base_data_dir, exist_ok=True)
```

---

## Step 3: Adjust runtime parameters

You must adjust the variables in the main block to define the scraping range and speed:

| Parameter                                            | Meaning                                                                                   |
| :--------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| `start_month`, `start_year`, `end_month`, `end_year` | Define the date range.                                                                    |
| `start_ID`, `end_ID`                                 | Define the tail-number constraints within the range.                                      |
| `start_index`, `num_papers`, `download_all`          | Select a subset (slicing) from the computed ID list.                                      |
| `DOWNLOAD_THREAD_COUNT` (default: 3)                 | Number of parallel threads for downloading source files.                                  |
| `REFERENCE_THREAD_COUNT` (default: 2)                | Number of parallel threads for extracting references (optimized for the 1 req/sec limit). |

---

## Step 4: Execution and Recovery

1. **Main Execution:** Run the final code block. The program will:

   * Detect target IDs and initialize queues (`id_queue`, `download_queue`).
   * Launch `download_worker` and `reference_worker` threads to process data concurrently.
2. **Synchronization:** The program uses `queue.join()` to wait for all thread tasks to finish.
3. **Recovery:** After the main threads finish, the function `recover_missing_papers` runs. It inspects the output directory for missing papers in the selected range and **automatically restarts the pipeline** to fetch missing items.

   * **Note:** Using Google Drive allows this Recovery mechanism to persist even if the Colab session disconnects.
4. **Performance Report:** Finally, `benchmark.report()` prints a full summary of runtime, RAM usage, and disk usage—required for the final report.

---

## Step 5: (Optional) Watch the Demo Video to Learn How to Run the Pipeline Properly

Alongside the source code and collected data, we also have a **YouTube demo video** (maximum **120 seconds**) that showcases how the scraper works.

1. **Content:**
   * Show the pipeline in action by running the submitted code.
   * Demonstrate the **data processing workflow**, including queues, threading, and recovery of missing papers.
   * Highlight the **output structure**, e.g., how downloaded papers and extracted references are organized.
   * Display key **intermediate logs** to illustrate progress and debug information.

2. **Explanation:**
   * Provide a clear explanation of **how the scraper operates**.
   * Describe the **design rationale**, including why certain threading, rate-limiting, or recovery mechanisms were implemented.

3. **Video:**

   * The video at **[YouTube](https://youtu.be/MWt4aQyfHkc)**.
   * The video is **publicly viewable**.
   * Online for at least **1 month after the course ends**.
   * The Link is included in the `Report` document.
---


