import arxiv
from arXiv_handler import get_IDs_All
from downloader import download

if __name__ == "__main__":
    start_month = 3
    start_year = 2023
    start_ID = 7856
    
    end_month = 4
    end_year = 2023
    end_ID = 4606
    client = arxiv.Client()
    count = 2
    dict_id = get_IDs_All(start_month, start_year, start_ID, end_month, end_year, end_ID)
    for arxiv_id in dict_id:
        print(f"Downloading {arxiv_id}...")
        
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(client.results(search))
        print(result)
        
        download(result.get_short_id())
        count -= 1
        if count == 0:
            break