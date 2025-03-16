import os
import base64
import requests
from datetime import datetime, UTC

# GitHub Token and PR flags
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
CREATE_PR = os.getenv("CREATE_PR", "false").lower() == "true"
COPY_FROM_DIRECTORY = os.getenv("COPY_FROM_DIRECTORY", "").strip() or "."  # Default: root
COPY_TO_DIRECTORY = os.getenv("COPY_TO_DIRECTORY", "").strip() or "."  # Default: root
BOT_NAME = "syncbot"
BOT_EMAIL = "syncbot@github.com"

# GitHub API Headers
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Read repository list 
with open("sync-repos.txt", "r") as f:
    repos = [line.strip() for line in f.readlines() if line.strip()]

# Get all files in the source directory
def get_files_in_directory(directory):
    """Returns a list of files (with paths) in the given directory."""
    file_paths = []
    for root, _, files in os.walk(directory):
        # print(f"root: {root}")
        # print(f"files: {files}")
        for file in files:
            print(f"Adding file {file} to file path list")
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)  # Keep subdirectories
            print(f"Full Path: {full_path}, Relative Path: {relative_path}")
            file_paths.append((full_path, relative_path))
    print("Final file paths to copy", file_paths)
    return file_paths

# Read and encode all files
def encode_file(file_path):
    """Reads and Base64 encodes a file for GitHub API upload."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Get file SHA (needed for updates)
def get_file_sha(repo, path, branch="main"):
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        print(f"File already present at target path {path}. Updating contents...")
        return response.json().get("sha")
    print(f"File not present at target path {path}. Adding a copy now...")
    return None

# Create a new branch if needed
def create_branch(repo):
    url = f"https://api.github.com/repos/{repo}/git/ref/heads/main"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        base_sha = response.json()["object"]["sha"]
    else:
        print(f"❌ Failed to get main branch SHA for {repo}")
        return None

    TIMESTAMP = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    NEW_BRANCH = f"sync-branch-{TIMESTAMP}"
    
    url = f"https://api.github.com/repos/{repo}/git/refs"
    payload = {"ref": f"refs/heads/{NEW_BRANCH}", "sha": base_sha}
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 201:
        print(f"✅ Created new branch '{NEW_BRANCH}' in {repo}")
        return NEW_BRANCH
    elif response.status_code == 422:
        print(f"⚠️ Branch '{NEW_BRANCH}' already exists in {repo}")
        return NEW_BRANCH
    else:
        print(f"❌ Failed to create branch '{NEW_BRANCH}' in {repo}: {response.json()}")
        return None

# Upload files to the repo
def update_files_in_repo(repo, branch="main"):
    """Creates or updates multiple files in the target repository."""
    files = get_files_in_directory(COPY_FROM_DIRECTORY)

    for local_path, relative_path in files:
        if COPY_TO_DIRECTORY == ".":
            target_path = relative_path  # Copy to root directory
        else:
            target_path = f"{COPY_TO_DIRECTORY}/{relative_path}" # Preserve source directory structure
        print(f"Target path set for current file {relative_path} as {target_path}")
        url = f"https://api.github.com/repos/{repo}/contents/{target_path}"
        encoded_content = encode_file(local_path)
        sha = get_file_sha(repo, target_path, branch)

        payload = {
            "message": f"Syncing {relative_path} [Automated]",
            "content": encoded_content,
            "branch": branch,
            "committer": {"name": BOT_NAME, "email": BOT_EMAIL}
        }
        if sha:
            payload["sha"] = sha  # Needed for updates

        response = requests.put(url, json=payload, headers=HEADERS)

        if response.status_code in [200, 201]:
            print(f"✅ Successfully updated {target_path} in {repo} on branch {branch}")
        else:
            print(f"❌ Failed to update {target_path} in {repo}: {response.json()}")

def create_pull_request(repo, branch):
    url = f"https://api.github.com/repos/{repo}/pulls"
    payload = {
        "title": "Sync files [Automated]",
        "head": branch,
        "base": "main",
        "body": "This PR updates multiple files in the repository."
    }
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 201:
        print(f"✅ Created PR in {repo}: {response.json()['html_url']}")
    else:
        print(f"❌ Failed to create PR in {repo}: {response.json()}")

for repo in repos:
    print(f"Initiating files sync to repo: {repo}")
    if CREATE_PR:
        branch = create_branch(repo)
        if branch:
            update_files_in_repo(repo, branch)
            create_pull_request(repo, branch)
    else:
        update_files_in_repo(repo)
