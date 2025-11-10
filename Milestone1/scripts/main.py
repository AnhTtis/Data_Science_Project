import arxiv
from arXiv_handler import get_IDs_All
from downloader import download
from reference_extractor import extract_references_for_paper
import os
import time
import re

if __name__ == "__main__":
    # ==================== CONFIGURATION ====================
    # Cấu hình thời gian và ID bắt đầu
    start_month = 3
    start_year = 2023
    start_ID = 7856
    
    # Cấu hình thời gian và ID kết thúc
    end_month = 4
    end_year = 2023
    end_ID = 4606
    # =======================================================
    
    print("="*60)
    print("DATA SCRAPING PIPELINE - MILESTONE 1")
    print("="*60)
    print(f"Start: {start_year}/{start_month:02d} - ID: {start_ID}")
    print(f"End:   {end_year}/{end_month:02d} - ID: {end_ID}")
    print("="*60)
    
    client = arxiv.Client()
    base_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "23127130"))
    
    # Tạo thư mục data nếu chưa có
    os.makedirs(base_data_dir, exist_ok=True)
    
    # Lấy danh sách tất cả arXiv IDs trong khoảng đã chỉ định
    print("\nFetching arXiv IDs in specified range...")
    list_id = get_IDs_All(start_month, start_year, start_ID, end_month, end_year, end_ID)
    print(f"Found {len(list_id)} papers to process\n")
    count = 4
    for arxiv_id in list_id:
        count -= 1
        print(f"\n{'='*60}")
        print(f"Processing {arxiv_id}")
        print('='*60)
        
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(client.results(search))
        
        version_latest = int(re.match(r"^(\d{4}\.\d{5})v(\d+)$", result.get_short_id()).groups()[1])
        list_download = []
        list_download.append(result)
        
        for v in range(1, version_latest):
            arxiv_id_v = arxiv_id + f"v{v}"
            search_v = arxiv.Search(id_list=[arxiv_id_v])
            result_v = next(client.results(search_v))
            list_download.append(result_v)
        
        # Get source tex and references.json:
        download(list_download, base_data_dir)
        extract_references_for_paper(arxiv_id, base_data_dir)
        if (count == 0):
            break
    
    # # Thống kê
    # stats = {
    #     "total": len(dict_id),
    #     "downloaded": 0,
    #     "references_extracted": 0,
    #     "failed": 0
    # }
    
    # for idx, arxiv_id in enumerate(dict_id, start=1):
    #     print(f"\n{'='*60}")
    #     print(f"[{idx}/{stats['total']}] Processing {arxiv_id}")
    #     print('='*60)
        
    #     # Step 1: Download paper and extract
    #     try:
    #         search = arxiv.Search(id_list=[arxiv_id])
    #         result = next(client.results(search))
    #         title = result.title[:80] + "..." if len(result.title) > 80 else result.title
    #         print(f"Found: {title}")
            
    #         # Download và extract source files
    #         download(result.get_short_id())
    #         stats["downloaded"] += 1
    #         print(f"✓ Downloaded successfully")
            
    #         # Step 2: Extract references for all versions
    #         match = re.match(r"^(\d{4}\.\d{5})v(\d+)$", result.get_short_id())
    #         if match:
    #             main_id, latest_v = match.groups()
    #             latest_v = int(latest_v)
                
    #             paper_folder = os.path.join(base_data_dir, main_id)
                
    #             # Extract references for each version
    #             ref_success = 0
    #             for v in range(1, latest_v + 1):
    #                 version_folder = os.path.join(paper_folder, f"v{v}")
    #                 arxiv_id_with_version = f"{main_id}v{v}"
                    
    #                 if os.path.exists(version_folder):
    #                     print(f"Extracting references for version {v}...", end=" ")
    #                     if save_references(arxiv_id_with_version, version_folder, verbose=False):
    #                         ref_success += 1
    #                         print("✓")
    #                     else:
    #                         print("✗")
    #                     time.sleep(1)  # Rate limiting cho Semantic Scholar API
                
    #             if ref_success > 0:
    #                 stats["references_extracted"] += 1
    #                 print(f"✓ References extracted for {ref_success}/{latest_v} versions")
            
    #         print(f"✓ Completed {arxiv_id}")
                    
    #     except StopIteration:
    #         print(f"✗ Paper {arxiv_id} not found in arXiv")
    #         stats["failed"] += 1
    #     except Exception as e:
    #         print(f"✗ Error processing {arxiv_id}: {e}")
    #         stats["failed"] += 1
    #         continue
    
    # # Final summary
    # print("\n" + "="*60)
    # print("PIPELINE EXECUTION COMPLETED")
    # print("="*60)
    # print(f"Total papers:              {stats['total']}")
    # print(f"Successfully downloaded:   {stats['downloaded']}")
    # print(f"References extracted:      {stats['references_extracted']}")
    # print(f"Failed:                    {stats['failed']}")
    # print(f"Success rate:              {stats['downloaded']/max(stats['total'],1)*100:.1f}%")
    # print("="*60)