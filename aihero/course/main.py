 

import io
import zipfile
import requests
import frontmatter  

def main():
    print("Hello from course!")

    with open('example.md', 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    # Access metadata
    print(f"title=={post.metadata['title']}")  # "Getting Started with AI"
    print(f"tags=={post.metadata['tags']}")   # ["ai", "machine-learning", "tutorial"]

    # Access content
    print(post.content)  # The markdown content without frontmatter    

def main2():
    url = 'https://codeload.github.com/DataTalksClub/faq/zip/refs/heads/main'
    resp = requests.get(url)   

    repository_data = []

    # Create a ZipFile object from the downloaded content
    zf = zipfile.ZipFile(io.BytesIO(resp.content))

    for file_info in zf.infolist():
        filename = file_info.filename.lower()

        # Only process markdown files
        if not (filename.endswith('.md') or filename.endswith('.mdx')):
            continue

        # Read and parse each file
        with zf.open(file_info) as f_in:
            content = f_in.read()
            post = frontmatter.loads(content)
            data = post.to_dict()
            data['filename'] = filename
            repository_data.append(data)

    zf.close()  
    
    print(repository_data[1])  



def read_repo_data(repo_owner, repo_name):
    """
    Download and parse all markdown files from a GitHub repository.
    
    Args:
        repo_owner: GitHub username or organization
        repo_name: Repository name
    
    Returns:
        List of dictionaries containing file content and metadata
    """
    prefix = 'https://codeload.github.com' 
    url = f'{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main'
    resp = requests.get(url)
    
    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")

    repository_data = []
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    for file_info in zf.infolist():
        filename = file_info.filename
        filename_lower = filename.lower()

        if not (filename_lower.endswith('.md') 
            or filename_lower.endswith('.mdx')):
            continue
    
        try:
            with zf.open(file_info) as f_in:
                content = f_in.read().decode('utf-8', errors='ignore')
                post = frontmatter.loads(content)
                data = post.to_dict()
                data['filename'] = filename
                repository_data.append(data)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    zf.close()
    return repository_data

if __name__ == "__main__":
    #main2()
    dtc_faq = read_repo_data('DataTalksClub', 'faq')
    evidently_docs = read_repo_data('evidentlyai', 'docs')

    print(f"FAQ documents: {len(dtc_faq)}")
    print(f"Evidently documents: {len(evidently_docs)}")
