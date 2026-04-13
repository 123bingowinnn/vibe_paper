from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parents[1]
    print(f"Training code would run from: {project_root}")
    print("This example keeps the repository small and focuses on paper-writing workflow.")


if __name__ == "__main__":
    main()

