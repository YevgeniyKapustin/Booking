import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from scripts.generate_er import generate_mermaid  # noqa: E402


def _run_docker(project_root: Path) -> int:
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{project_root}:/work",
        "minlag/mermaid-cli:10.9.0",
        "-i",
        "/work/docs/er.mmd",
        "-o",
        "/work/docs/er.png",
    ]
    subprocess.run(docker_cmd, check=True)
    return 0


def _run_mmdc(project_root: Path) -> int:
    mmdc_cmd = [
        "npx",
        "--yes",
        "@mermaid-js/mermaid-cli",
        "-i",
        str(project_root / "docs" / "er.mmd"),
        "-o",
        str(project_root / "docs" / "er.png"),
    ]
    subprocess.run(mmdc_cmd, check=True)
    return 0


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    mermaid_path = docs_dir / "er.mmd"
    output_path = docs_dir / "er.png"
    generate_mermaid(mermaid_path)

    try:
        _run_docker(project_root)
    except FileNotFoundError:
        try:
            _run_mmdc(project_root)
        except FileNotFoundError:
            print(
                "Docker and npx not found. Install Docker or Node.js (npx) to render PNG."
            )
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"Failed to render PNG via npx mermaid-cli (exit {exc.returncode}).")
            return exc.returncode
    except subprocess.CalledProcessError as exc:
        try:
            _run_mmdc(project_root)
        except FileNotFoundError:
            print(
                "Failed to render PNG via Docker and npx is missing. Install Node.js (npx) "
                "or fix Docker image/pull."
            )
            return exc.returncode
        except subprocess.CalledProcessError as next_exc:
            print(
                "Failed to render PNG via Docker and npx mermaid-cli "
                f"(exit {next_exc.returncode})."
            )
            return next_exc.returncode

    print("ER diagram saved to docs/er.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
