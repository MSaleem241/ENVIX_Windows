# Every tool entry now has a "category" key: either "language" or "tool".
#   - "language" = a programming language runtime (Python, Node, Java, Go)
#   - "tool"     = a supporting application (Git, VS Code, Docker)
# This single new key is what the GUI uses to split "Languages" and "Tools"
# into two separate tabs, without needing two separate dictionaries.
TOOLS = {
    "node": {
        "category": "language",
        "check": ["node", "-v"],
        "install": {
            "type": "winget",
            "id": "OpenJS.NodeJS"
        }
    },

    "python": {
        "category": "language",
        "check": ["python", "--version"],
        "install": {
            "type": "winget",
            "id": "Python.Python.3"
        }
    },
    "java": {
        "category": "language",
        "check": ["java", "-version"],
        "install": {
            "type": "winget",
            "id": "EclipseAdoptium.Temurin.21.JDK"
        }
    },
    "go": {
        "category": "language",
        "check": ["go", "version"],
        "install": {
            "type": "winget",
            "id": "GoLang.Go"
        }
    },

    "git": {
        "category": "tool",
        "check": ["git", "--version"],
        "install": {
            "type": "winget",
            "id": "Git.Git"
        }
    },
    "vscode": {
        "category": "tool",
        "check": ["where", "code"],
        "install": {
            "type": "winget",
            "id": "Microsoft.VisualStudioCode"
        }
    },
    "docker": {
        "category": "tool",
        "check": ["docker", "--version"],
        "install": {
            "type": "winget",
            "id": "Docker.DockerDesktop"
        }
    }
}