import os
import json
import arxiv

class MetadataCollector:
    def __init__(self, base_dir="../data"):
        """Initialize the MetadataCollector with base directory for data storage."""
        self.base_dir = os.path.abspath(base_dir)
        self.client = arxiv.Client()

    def create_metadata(self, paper, save_path):
        """
        Create metadata dictionary from arXiv API result and save it.
        
        Args:
            paper: Result from arxiv API query
            save_path: Path where metadata should be saved
            
        Returns:
            dict: Metadata from the paper
        """
        arxiv_id = paper.get_short_id()
        version = int(arxiv_id.split('v')[1])
        base_id = arxiv_id.split('v')[0]
        
        metadata = {
            "id": arxiv_id,
            "title": paper.title.strip(),
            "authors": [author.name for author in paper.authors],
            "abstract": paper.summary.strip(),
            "categories": paper.categories,
            "submission_date": paper.published.strftime("%Y-%m-%d"),
            "revised_dates": [
                d.strftime("%Y-%m-%d") for d in sorted([paper.published, paper.updated])
                if d.strftime("%Y-%m-%d") != paper.published.strftime("%Y-%m-%d")
            ],
            "dois": [paper.doi] if paper.doi else [],
            "comments": [paper.comment] if paper.comment else [],
            "pdf_urls": [f"http://arxiv.org/pdf/{arxiv_id}"]
        }

        # Save metadata to JSON file
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        
        return metadata

    def collect_metadata(self, arxiv_id):
        """
        Collect and save metadata for all versions of a paper whose files have been downloaded.
        
        Args:
            arxiv_id (str): The arXiv ID to collect metadata for (can be with or without version)
            
        Returns:
            dict: Dictionary with version numbers as keys and metadata as values
        """
        try:
            # Remove version number if present to get base ID
            base_id = arxiv_id.split('v')[0]
            paper_dir = os.path.join(self.base_dir, base_id)
            
            if not os.path.exists(paper_dir):
                print(f"Directory not found for {base_id}. Has it been downloaded?")
                return None
                
            # Get versions from existing directories
            versions = sorted([
                int(d.replace('v', '')) 
                for d in os.listdir(paper_dir) 
                if d.startswith('v') and os.path.isdir(os.path.join(paper_dir, d))
            ])
            
            if not versions:
                print(f"No version directories found for {base_id}")
                return None
            
            print(f"\nCollecting metadata for {base_id} ({len(versions)} versions)...")
            versions_metadata = {}
            
            # Collect metadata for each version
            for version in versions:
                version_dir = os.path.join(paper_dir, f"v{version}")
                metadata_path = os.path.join(version_dir, "metadata.json")
                versioned_id = f"{base_id}v{version}"
                
                print(f"- Version {version}:", end=" ", flush=True)
                
                try:
                    # Get metadata from arXiv
                    search = arxiv.Search(id_list=[versioned_id])
                    paper = next(self.client.results(search))
                    metadata = self.create_metadata(paper, metadata_path)
                    versions_metadata[version] = metadata
                    print("✓")
                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue
            
            return versions_metadata if versions_metadata else None
            
        except Exception as e:
            print(f"Error processing {arxiv_id}: {e}")
            return None

    def collect_batch_metadata(self, arxiv_ids):
        """
        Collect metadata for a batch of downloaded papers.
        
        Args:
            arxiv_ids (list): List of arXiv IDs to collect metadata for
            
        Returns:
            dict: Dictionary mapping arXiv IDs to their metadata versions
        """
        metadata_collection = {}
        processed_count = 0
        version_count = 0
        
        print(f"Collecting metadata for {len(arxiv_ids)} papers...")
        
        for arxiv_id in arxiv_ids:
            versions_metadata = self.collect_metadata(arxiv_id)
            if versions_metadata:
                metadata_collection[arxiv_id] = versions_metadata
                processed_count += 1
                version_count += len(versions_metadata)
                
        print(f"\nCollection complete:")
        print(f"- Papers processed: {processed_count}/{len(arxiv_ids)}")
        print(f"- Total versions: {version_count}")
        if processed_count > 0:
            print(f"- Average versions per paper: {version_count/processed_count:.1f}")
        
        return metadata_collection

# Example usage
if __name__ == "__main__":
    collector = MetadataCollector()
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    papers = [
        folder for folder in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, folder)) and not folder.startswith('.')
    ]
    
    print(f"Found {len(papers)} papers in data directory")
    metadata = collector.collect_batch_metadata(papers)
