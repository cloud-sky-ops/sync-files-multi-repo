# Sync Files Across Repositories GitHub Action

## Overview
This GitHub Action enables seamless **file synchronization** across multiple repositories using the **GitHub API**. It allows copying an **entire directory** from the source repository to multiple target repositories **without cloning them**. The action supports both **direct commits** and **pull requests**, dynamically detecting the default branch of each repository.

**Not supporting self-hosted runners yet**

## Key Features
✅ **Sync an entire directory** across multiple repositories.  
✅ **Automatically detects the default branch** instead of assuming `main`.  
✅ **Supports direct commits or creating pull requests** as per user input.  
✅ **Preserves directory structure** in the destination repositories.  
✅ **Works with both public and private repositories.**  
✅ **Lightweight & efficient**—uses GitHub API instead of full clones.  

---

## Usage

### **Basic Workflow Example**
This example syncs files from the `root` directory to multiple repositories:

```yaml
name: Sync Files

on:
  workflow_dispatch:

jobs:
  sync-files:
    runs-on: ubuntu-latest
    steps:
      - name: Use Sync Files Action
        uses: cloud-sky-ops/sync-files-multi-repo@v1
        with:
          github_token: ${{ secrets.PAT_TOKEN }}
```

### **Available Inputs**

| Input Name            | Description  | Default |
|----------------------|--------------|---------|
| `github_token` | **Required.** GitHub PAT token with repo access. | N/A |
| `create-pull-request` | If `true`, creates a PR instead of committing directly. | `false` |
| `copy-from-directory` | Source directory to sync from. | `root-directory` |
| `copy-to-directory` | Target directory in the destination repos. | `root-directory` |

---

## **Required File: `sync-repos.txt`**
Creating the `sync-repos.txt` file is **mandatory**. This file contains a list of repositories where the files should be synced. Each repository should be listed on a new line in the format:

```
owner/repo-name-1
owner/repo-name-2
owner/repo-name-3
```

### **Example `sync-repos.txt`**
```
my-org/repo-one
my-org/repo-two
my-org/repo-three
```

---

## How It Works
1. **Reads the list of repositories** from `sync-repos.txt`.
2. **Detects the default branch** of each target repository.
3. **Copies all files from the specified source directory. If source directory isn't specified it picks all files from root directory of the source repo**.
4. **Uploads the files to the destination repositories. If target directory isn't specified it copies all files to root directory of the target repo**.
5. **Creates a pull request** (if enabled) or directly commits the files to the default branch in that repo.

---

## Example Use Cases

### **1️⃣ Sync Documentation Across Multiple Repos**
Keep README files, templates, and markdown documents updated across multiple repositories.
```yaml
copy-from-directory: "docs"
copy-to-directory: "docs"
```

### **2️⃣ Manage CI/CD Configurations for Multiple Services from one place**
- Ensure all services follow **a standardized deployment process** by creating dynamic CI/CD files which are re-useable across multiple repositories but managed in one central location.
```yaml
copy-from-directory: ".github/workflows"
copy-to-directory: ".github/workflows"
```
  **Note**: To make changes to ".github/workflows", user needs to also add "**workflow**" permission to the PAT token.
  ![image](https://github.com/user-attachments/assets/8f6c9a1f-1269-4c47-987a-54c23e675f7e)

### **3️⃣ Update Dockerfiles Across Microservices**
Keep all microservices updated with the latest **Docker base images**.
```yaml
copy-from-directory: "docker"
copy-to-directory: "docker"
```
---

## License
This project is licensed under the **MIT License**, allowing commercial and private use with minimal restrictions.

---

## Contributing
We welcome contributions! If you have ideas for new features, open an issue or submit a PR.

---

## Support
For issues or feature requests, open an [issue on GitHub](https://github.com/my-org/sync-file-action/issues).
