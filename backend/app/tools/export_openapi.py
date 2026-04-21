import json
from pathlib import Path

from app.main import app


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_path = repo_root / "docs" / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OpenAPI schema exported to {output_path}")


if __name__ == "__main__":
    main()
