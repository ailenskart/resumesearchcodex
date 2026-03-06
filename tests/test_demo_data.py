from pathlib import Path

from app.demo_data import seed_demo_resumes


def test_seed_demo_resumes(tmp_path: Path):
    count = seed_demo_resumes(str(tmp_path))
    assert count >= 3
    assert (tmp_path / "anita_sharma.txt").exists()
