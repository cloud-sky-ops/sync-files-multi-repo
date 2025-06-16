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
| `bot-name` | Customizable name for the committer bot | `syncbot` |
| `bot-email` | Customizable email for the committer bot | `syncbot@github.com` |
| `configs-json-file` | Name override option for mandatory config JSON | `sync_configs.json` |

---

## Scaling with **Required File: `sync_configs.json`**

For large-scale repo management, you can use a **centralized JSON config** to define **repo-specific rules**. If the fields are present for a particular repo, it will override default behavior as passed during action call in workflow. **Please note** `bot-name, bot-email and config-json-file` are not valid fields for this file.

### **Example `sync_configs.json` File**
```json
{
    "repos": {
        "my-org/repo-one": {
            "create-pull-request": "true",
            "copy-from-directory": "source-configs",
            "copy-to-directory": "configs"
        },
        "my-org/repo-two": {
            "create-pull-request": "false",
            "copy-from-directory": "docker"
        },
        "my-org/repo-three": {}
    }
}
```

### **What Can Be Customized per Repo?**
✅ **Pull Request Mode** → Enable/disable PR creation.  
✅ **Source and Target Directory** → Specify where files should be placed in the destination repo.  

---

## Use Cases

### **1️⃣ Sync Documentation Across Multiple Repos**
Keep README files, templates, and markdown documents updated across multiple repositories.
```yaml
copy-from-directory: "docs"
copy-to-directory: "docs"
```

### **2️⃣ Manage CI/CD Configurations for Hundreds of Services**
- Sync GitHub Actions, Jenkinsfiles, and Kubernetes manifests across services.
- Ensure all services follow **a standardized deployment process**.

```yaml
copy-from-directory: ".github/workflows"
copy-to-directory: ".github/workflows"
```

### **3️⃣ Sync Security Policies and Compliance Configurations**
```yaml
copy-from-directory: "security"
copy-to-directory: "security"
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
