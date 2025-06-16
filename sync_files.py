from datetime import datetime, UTC
import os
import base64
import time
import requests, json


# GitHub Token and PR flags
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BOT_NAME = "syncbot"
BOT_EMAIL = "syncbot@github.com"

# GitHub API Headers
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_default_branch(target_repo):
    url = f"https://api.github.com/repos/{target_repo}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("default_branch", None)
    else:
        print(f"❌ Failed to get default branch for {target_repo}: {response.json()}")
        return None

# Get all files in the source directory
def get_files_in_directory(directory):
    """Returns a list of files (with paths) in the given directory."""
    file_paths = []
    for root, dirnames, files in os.walk(directory):
        # print(f"root: {root}")
        # print(f"files: {files}")
        if ".git" in dirnames:   # Exclude ".git/" directory files when copying from root
            dirnames.remove(".git")
        for file in files:
            print(f"Adding file {file} to file path list")
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)  # Keep subdirectories
            print(f"Full Path: {full_path}, Relative Path: {relative_path}")
            file_paths.append((full_path, relative_path))
            print("--------------------------------------------------------------------------------------------------------------------")
    print("Final file paths to copy", file_paths)
    print("--------------------------------------------------------------------------------------------------------------------")
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
def create_feature_branch(target_repo, default_branch):
    url = f"https://api.github.com/repos/{target_repo}/git/ref/heads/{default_branch}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        base_sha = response.json()["object"]["sha"]
    else:
        print(f"❌ Failed to get {default_branch} branch SHA for {target_repo}")
        return None

    TIMESTAMP = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    NEW_BRANCH = f"sync-branch-{TIMESTAMP}"

    url = f"https://api.github.com/repos/{target_repo}/git/refs"
    payload = {"ref": f"refs/heads/{NEW_BRANCH}", "sha": base_sha}
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 201:
        print(f"✅ Created new branch '{NEW_BRANCH}' in {target_repo}")
        return NEW_BRANCH
    elif response.status_code == 422:
        print(f"⚠️ Branch '{NEW_BRANCH}' already exists in {target_repo}")
        return NEW_BRANCH
    else:
        print(f"❌ Failed to create branch '{NEW_BRANCH}' in {target_repo}: {response.json()}")
        return None

# Upload files to the repo
def update_files_in_repo(target_repo, target_branch):
    """Creates or updates multiple files in the target repository."""
    files = get_files_in_directory(COPY_FROM_DIRECTORY)

    for local_path, relative_path in files:
        if COPY_TO_DIRECTORY == ".":
            target_path = relative_path  # Copy to root directory
        else:
            target_path = f"{COPY_TO_DIRECTORY}/{relative_path}" # Preserve source directory structure
        print(f"Target path set for current file {relative_path} as {target_path}")
        url = f"https://api.github.com/repos/{target_repo}/contents/{target_path}"
        encoded_content = encode_file(local_path)
        sha = get_file_sha(target_repo, target_path, target_branch)

        payload = {
            "message": f"Syncing {relative_path} [Automated]",
            "content": encoded_content,
            "branch": target_branch,
            "committer": {"name": BOT_NAME, "email": BOT_EMAIL}
        }
        if sha:
            payload["sha"] = sha  # Needed for updates

        response = requests.put(url, json=payload, headers=HEADERS)

        if response.status_code in [200, 201]:
            print(f"✅ Successfully updated {target_path} in {target_repo} on branch {target_branch}")
        else:
            print(f"❌ Failed to update {target_path} in {target_repo}: {response.json()}")
        print("--------------------------------------------------------------------------------------------------------------------")
        time.sleep(6)

def create_pull_request(target_repo, base_branch, head_branch):
    url = f"https://api.github.com/repos/{target_repo}/pulls"
    payload = {
        "title": "Sync files [Automated]",
        "head": head_branch,
        "base": base_branch,
        "body": "This PR updates multiple files in the repository."
    }
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 201:
        print(f"✅ Created PR in {target_repo}: {response.json()['html_url']}")
    else:
        print(f"❌ Failed to create PR in {target_repo}: {response.json()}")
    print("--------------------------------------------------------------------------------------------------------------------")

# Read repo names and config from config file
with open("sync_configs.json", "r") as config_file:
    parsed_json = json.load(config_file)
    repos_config=parsed_json["repos"]

for repo,configs in repos_config.items():
    print(f"Initiating files sync to repo: {repo}")
    print("Fetch source directory")
    
    if "copy-from-directory" in configs:
        COPY_FROM_DIRECTORY = configs["copy-from-directory"]
    else:
        COPY_FROM_DIRECTORY = os.getenv("COPY_FROM_DIRECTORY", "").strip() or "."  # Default: root
    
    print(f"Source directory: {COPY_FROM_DIRECTORY}")
    print("Fetch target directory")

    if "copy-to-directory" in configs:
        COPY_TO_DIRECTORY = configs["copy-to-directory"]
    else:
        COPY_TO_DIRECTORY = os.getenv("COPY_TO_DIRECTORY", "").strip() or "."  # Default: root

    print(f"Target directory: {COPY_TO_DIRECTORY}")
    print("Set CREATE_PR flag")

    if "create-pull-request" in configs:
        CREATE_PR = (configs["create-pull-request"]).lower() == "true" # comparision with == "true" after turning to lower case will return boolean value
    else:
        CREATE_PR = os.getenv("CREATE_PR", "false").lower() == "true"

    print(f"CREATE_PR: {CREATE_PR}")

    print(f"Fetching default branch for {repo}")
    default_branch=get_default_branch(repo)

    if default_branch:   
        if CREATE_PR:
            feature_branch = create_feature_branch(repo, default_branch)
            if feature_branch:
                update_files_in_repo(repo, feature_branch)
                create_pull_request(repo, default_branch, feature_branch)
            else:
                raise Exception("Unable to create feature branch. Check logs")
        else:
            update_files_in_repo(repo, default_branch)
    else:
        raise Exception("Unable to fetch default branch. Check logs")
