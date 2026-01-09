# I. Group Information 

| Student ID      | Full Name                |
| :-------------- | :----------------------- | 
| **23127130**    | Nguyễn Hữu Anh Trí       |
| **23127107**    | Nguyễn Huy Quân          | 
| **23127051**    | Cao Tấn Hoàng Huy        |  

---

# II. Summary of Our Work

## II.1 Achievements

In this milestone, we have implemented advanced data processing and machine learning techniques to transform unstructured LaTeX documents into structured hierarchical data and perform intelligent reference matching:

### **Task 1: Hierarchical Parsing and Standardization**
* **LaTeX Source Processing:** Automatic expansion of multi-file LaTeX documents by resolving `\input` and `\include` commands
* **Hierarchy Construction:** Build tree structures representing document organization (Document → Sections → Subsections → Paragraphs → Sentences/Equations/Figures)
* **Text Normalization:** Clean LaTeX formatting, standardize mathematical notation, remove boilerplate commands
* **Reference Extraction:** Parse BibTeX files and `\bibitem` entries, convert to standard BibTeX format
* **Deduplication:** Smart deduplication at two levels:
  - Reference entries across versions (merge duplicate citations)
  - Full-text content across versions (identify unchanged elements)

### **Task 2: Reference Matching Pipeline**
* **Data Preparation:** Clean and normalize bibliographic metadata for matching
* **Feature Engineering:** Design discriminative features including:
  - Title similarity (TF-IDF, Levenshtein distance, SequenceMatcher)
  - Author overlap and matching scores
  - Year difference and publication date features
  - Text length and structural features
* **Machine Learning Model:** Train supervised Logistic Regression classifier for binary matching
* **Ranking & Evaluation:** Generate top-5 ranked predictions per reference and evaluate using Mean Reciprocal Rank (MRR)

---

## II.2. Tools and Methodology

### Task 1: Hierarchical Parsing

| Function                    | Tool/Library                                  | Description                                                                                           |
| :-------------------------- | :-------------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| **LaTeX Parsing**           | `re` (Regular Expressions)                    | Pattern matching for LaTeX commands, sectioning, equations, citations                                 |
| **File Management**         | `pathlib.Path`                                | Cross-platform file and directory operations                                                          |
| **BibTeX Processing**       | `bibtexparser`                                | Parse `.bib` files and `\bibitem` blocks, normalize entries                                           |
| **Text Fingerprinting**     | `hashlib` (MD5/SHA256)                        | Generate content hashes for deduplication                                                             |
| **Data Structure**          | `json`, `dict`, `list`                        | Store hierarchy as nested JSON with unique element IDs                                                |
| **Progress Tracking**       | `tqdm`                                        | Display progress bars for batch processing                                                            |

### Task 2: Reference Matching

| Function                    | Tool/Library                                  | Description                                                                                           |
| :-------------------------- | :-------------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| **Text Similarity**         | `difflib.SequenceMatcher`, `Levenshtein`      | Compute string similarity scores                                                                      |
| **Feature Engineering**     | `pandas`, `numpy`                             | Data manipulation and numerical feature extraction                                                    |
| **TF-IDF Vectorization**    | `sklearn.TfidfVectorizer`                     | Convert text to numerical vectors for title matching                                                  |
| **Machine Learning**        | `sklearn.LogisticRegression`                  | Binary classification model for matching prediction                                                   |
| **Data Scaling**            | `sklearn.StandardScaler`                      | Normalize features for model training                                                                 |
| **Model Evaluation**        | `sklearn.metrics` (accuracy, precision, MRR)  | Measure model performance                                                                             |
| **Visualization**           | `matplotlib`                                  | Plot feature distributions and model results                                                          |

---

## II.3. Data Folder Structure

### Input Structure (from Milestone 1)

```
<student_ID>/ (e.g., 23127130)
│
├── <yymm-id>/               # Paper folder (e.g., 2310-12345)
│   ├── metadata.json        # Paper metadata (title, authors, versions)
│   ├── references.json      # Scraped reference metadata from Semantic Scholar
│   └── tex/                 # LaTeX source files
│       ├── <yymm-id>v1/     # Version 1 source files
│       │   ├── *.tex        # LaTeX files
│       │   └── *.bib        # BibTeX files
│       ├── <yymm-id>v2/     # Version 2 source files
│       └── ...
```

### Output Structure (Milestone 2)

```
output/
│
├── <yymm-id>/               # Processed paper folder
│   ├── hierarchy.json       # Hierarchical document structure
│   ├── refs.bib             # Deduplicated BibTeX references
│   ├── metadata.json        # Copy of original metadata
│   ├── references.json      # Copy of scraped references
│   └── pred.json            # Top-5 predictions per reference (Task 2)
│
└── <yymm-id>/
    └── ...
```

---

# III. Setting Environment and Execution Steps

## Step 1: Extracting Files

From the submission, extract the **Milestone2.zip** file containing:

```
Milestone2/
├── src/                      
│   ├── Milestone2_Hierarchy.ipynb        # Task 1: Hierarchical parsing
│   ├── Milestone2_ReferencesMatching.ipynb  # Task 2: Reference matching
├── requirements.txt         
├── README.md                 
└── Report.{pdf/tex/docx}         
```

Upload the notebooks to **Google Colab** or run locally in Jupyter.

---

## Step 2: Setup Environment

### 2.1 Install dependencies

Run the following in the first code cell of each notebook:

```python
!pip install -r requirements.txt
```

Or install individually:

```python
!pip install numpy pandas scipy scikit-learn matplotlib
!pip install python-Levenshtein bibtexparser tqdm jupyter ipykernel
```

### 2.2 Import libraries

Both notebooks will automatically import required libraries:

```python
# First Notebook
import re  
from pathlib import Path  
import hashlib  
import json  
import bibtexparser 
from bibtexparser.bparser import BibTexParser 

import uuid  
from copy import deepcopy  

from pathlib import Path
from tqdm.auto import tqdm
import warnings
import logging

# Suppress all warnings
warnings.filterwarnings('ignore')

# Suppress bibtexparser logging messages
logging.getLogger('bibtexparser').setLevel(logging.ERROR)

# Second Notebook
import os
import re
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import warnings
import bibtexparser
warnings.filterwarnings('ignore')

# Text cleaner for data cleaning
from typing import Any

# String similarity
from difflib import SequenceMatcher

# ML libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer

# Visualizing
import matplotlib.pyplot as plt
from scipy import stats
```

### 2.3 Configure Paths

Set the data directory path:

```python
# For Task 1 (Hierarchy)
BASE_DATA_DIR = Path("23127130")  # Input from Milestone 1
OUTPUT_DIR = Path("output")        # Output directory

# For Task 2 (Matching)
OUTPUT_DIR = Path("output")        # Input from Task 1
```

**Note:** If using Google Drive:

```python
from google.colab import drive
drive.mount('/content/drive')

BASE_DATA_DIR = Path("/content/drive/MyDrive/23127130")
OUTPUT_DIR = Path("/content/drive/MyDrive/output")
```

---

## Step 3: Execute Task 1 - Hierarchical Parsing

### 3.1 Notebook Overview

**File:** `Milestone2_Hierarchy.ipynb`

**Processing Steps:**
1. **Version Discovery:** Scan input directory for paper versions
2. **LaTeX Expansion:** Recursively resolve `\input` and `\include` commands
3. **Preprocessing:** Remove comments, clean formatting, normalize equations
4. **Reference Extraction:** Parse BibTeX files and `\bibitem` blocks
5. **Hierarchy Building:** Construct tree structure (sections → sentences → equations)
6. **Deduplication:** 
   - Merge duplicate reference entries across versions
   - Fingerprint text elements to identify unchanged content
7. **Output Generation:** Save `hierarchy.json`, `refs.bib`, copy metadata files

### 3.2 Key Parameters

The pipeline is designed to be mostly automatic, but you can adjust:

```python
# Input/Output directories
BASE_DATA_DIR = Path("23127130")  # Input directory from Milestone 1
OUTPUT_DIR = Path("output")        # Output directory for processed files

# Processing settings
REMOVE_COMMENTS = True             # Remove LaTeX comments
NORMALIZE_MATH = True              # Standardize math notation
DEDUPLICATE_REFS = True            # Merge duplicate references
FINGERPRINT_ELEMENTS = True        # Enable content fingerprinting
```

The pipeline automatically:
- Detects all LaTeX files in each version folder
- Identifies the main compilation file
- Recursively expands `\input` and `\include` commands
- Parses document structure based on sectioning commands
- Extracts references from `.bib` files and `\bibitem` blocks

### 3.3 Execution

1. **Run all cells** in `Milestone2_Hierarchy.ipynb` sequentially
2. **Progress bars** will show processing status for each paper
3. **Output** will be saved to `output/<paper_id>/` directory

### 3.4 Verification

Check the output structure:

```python
# Verify hierarchy output
with open("output/2310-12345/hierarchy.json") as f:
    hierarchy = json.load(f)
    print(f"Paper: {hierarchy['paper_id']}")
    print(f"Versions: {hierarchy['versions']}")
    print(f"Root elements: {len(hierarchy['hierarchy']['children'])}")
```

---

## Step 4: Execute Task 2 - Reference Matching

### 4.1 Notebook Overview

**File:** `Milestone2_ReferencesMatching.ipynb`

**Processing Steps:**
1. **Data Loading:** Read `refs.bib` and `references.json` from Task 1 output
2. **Text Normalization:** Clean LaTeX commands, lowercase, remove punctuation
3. **Label Generation:** Create ground truth labels (manual + automatic exact matches)
4. **Feature Extraction:**
   - Title similarity (TF-IDF cosine, Levenshtein, SequenceMatcher)
   - Author overlap (exact match, fuzzy match)
   - Year difference
   - Text length features
5. **Data Splitting:** 80% train, 20% test
6. **Model Training:** Logistic Regression with hyperparameter tuning
7. **Ranking:** Generate top-5 predictions per BibTeX entry
8. **Evaluation:** Compute MRR, accuracy, precision, recall
9. **Output:** Save `pred.json` with ranked predictions

### 4.2 Key Parameters

```python
# Feature engineering settings
TFIDF_MAX_FEATURES = 1000          # TF-IDF vocabulary size
AUTHOR_SIMILARITY_THRESHOLD = 0.8  # Fuzzy author matching threshold
USE_LEVENSHTEIN = True             # Enable Levenshtein distance features
USE_TFIDF = True                   # Enable TF-IDF similarity features

# Model training settings
TEST_SIZE = 0.2                    # Train/test split ratio (80% train, 20% test)
RANDOM_STATE = 42                  # Reproducibility seed
LOGISTIC_C = 1.0                   # Regularization strength (inverse of regularization)
LOGISTIC_MAX_ITER = 1000           # Maximum iterations for convergence

# Ranking settings
TOP_K = 5                          # Number of predictions per reference
CONFIDENCE_THRESHOLD = 0.1         # Minimum confidence for predictions
```

**Important Parameters Explained:**
- **TFIDF_MAX_FEATURES:** Controls vocabulary size - higher values capture more terms but increase memory
- **TEST_SIZE:** Fraction of data used for testing - keep at 0.2 for balanced evaluation
- **LOGISTIC_C:** Lower values = stronger regularization (prevent overfitting)
### 4.4 Model Performance

Expected performance metrics on the test set:

**Classification Metrics:**
- **Accuracy:** 85-95% (binary classification: match vs. no match)
- **Precision:** 80-90% (of predicted matches, how many are correct)
- **Recall:** 75-85% (of actual matches, how many we found)
- **F1 Score:** 78-88% (harmonic mean of precision and recall)

**Ranking Metrics:**
- **MRR (Mean Reciprocal Rank):** 0.6-0.8
  - MRR = 1.0: Correct match always ranked #1 (perfect)
  - MRR = 0.5: Correct match ranked #2 on average
  - MRR = 0.33: Correct match ranked #3 on average
  
**Feature Importance (typical results):**
1. Title TF-IDF similarity: ~40% contribution
2. Title Levenshtein distance: ~25% contribution
3. Author overlap: ~20% contribution
4. Year difference: ~10% contribution
5. Other features: ~5% contribution

**Note:** Actual performance may vary depending on:
- Quality of ground truth labels
- Diversity of reference styles
- Completeness of candidate metadata paper's output directory

### 4.4 Model Performance

Expected performance metrics:
- **Accuracy:** 85-95% (binary classification)
- **Precision:** 80-90%
- **Recall:** 75-85%
- **MRR (Mean Reciprocal Rank):** 0.6-0.8
  - MRR = 1.0 means correct match always ranked #1
  - MRR = 0.5 means correct match ranked #2 on average

---

## Step 5: Outputs and Deliverables

### 5.1 Generated Files

After completing both tasks, each paper will have:

```
output/<paper_id>/
├── hierarchy.json       # Document structure (Task 1)
├── refs.bib             # Deduplicated references (Task 1)
├── metadata.json        # Paper metadata (copied)
├── references.json      # Candidate papers (copied)
└── pred.json            # Top-5 predictions (Task 2)
```

### 5.2 pred.json Format

```json
{
  "ref_xyz": [
    {"arxiv_id": "2301.12345", "score": 0.95, "rank": 1},
    {"arxiv_id": "2302.67890", "score": 0.82, "rank": 2},
    {"arxiv_id": "2303.11111", "score": 0.71, "rank": 3},
    {"arxiv_id": "2304.22222", "score": 0.65, "rank": 4},
    {"arxiv_id": "2305.33333", "score": 0.58, "rank": 5}
  ],
  "ref_abc": [...]
}
```

### 5.3 Verification Script

```python
# Verify all outputs exist
from pathlib import Path
import json

output_dir = Path("output")
required_files = ["hierarchy.json", "refs.bib", "pred.json"]

for paper_dir in output_dir.iterdir():
    if paper_dir.is_dir():
        print(f"\n{paper_dir.name}:")
        for file in required_files:
            file_path = paper_dir / file
            if file_path.exists():
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} MISSING")
```

---

## Step 6: (Optional) Watch the Demo Video to Learn How to Run the Pipeline Properly

Alongside the source code and processed data, we also have a **YouTube demo video** (maximum **120 seconds**) that showcases how the pipeline works.

### 6.1 Video Content

The video demonstrates:
* **Pipeline in Action:** Running both Task 1 (Hierarchy) and Task 2 (Matching) notebooks
* **Data Processing Workflow:** 
  - LaTeX expansion and hierarchy construction
  - Reference extraction and deduplication
  - Feature engineering and model training
* **Output Structure:** How `hierarchy.json`, `refs.bib`, and `pred.json` files are generated
* **Intermediate Logs:** Progress bars, processing steps, and evaluation metrics

### 6.2 Explanation

The video provides:
* Clear explanation of **how the two-stage pipeline operates**
* Description of **design rationale**, including:
  - Multi-file LaTeX expansion strategy
  - Fingerprinting for deduplication
  - Feature selection for reference matching
  - Logistic Regression model for ranking

### 9.3 Video Link

* **Watch the demo:** [YouTube Demo Video](https://youtu.be/MILESTONE2_DEMO_LINK)
* **Availability:** Publicly viewable, online for at least 1 month after course completion
* **Link included in:** Final Report document

---

## Additional Resources

### Source Code
- **GitHub Repository:** [Data_Science_Project](https://github.com/AnhTtis/Data_Science_Project)
- **Milestone 2 Branch:** Access the complete source code, notebooks, and documentation
- **Issues & Discussions:** Report bugs or ask questions through GitHub Issues

### Documentation
- **arXiv API:** https://info.arxiv.org/help/api/basics.html
- **BibTeX Parser:** https://bibtexparser.readthedocs.io/
- **scikit-learn:** https://scikit-learn.org/stable/
- **Regular Expressions:** https://docs.python.org/3/library/re.html
- **TF-IDF:** https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting

### Key References
1. **BibTeX Format Specification:** http://www.bibtex.org/Format/
2. **Mean Reciprocal Rank (MRR):** Commonly used metric for evaluating ranking systems
3. **Logistic Regression for Ranking:** scikit-learn documentation on probabilistic classification

---

**© 2025 University of Science (VNU-HCMC)**  
Developed for **Introduction to Data Science – Milestone 2** under the guidance of **Huỳnh Lâm Hải Đăng**.
