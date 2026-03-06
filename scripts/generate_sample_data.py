from pathlib import Path

SAMPLES = [
    (
        "anita_sharma.txt",
        """Anita Sharma
Senior Software Engineer
Location: Gurugram
Email: anita@example.com
Phone: +91-9876543210
Experience: 7 years
Skills: Python, FastAPI, AWS, Docker, SQL
Worked at: Acme Tech, Globex
""",
    ),
    (
        "rahul_verma.txt",
        """Rahul Verma
Backend Developer
Location: Bengaluru
Email: rahul@example.com
Experience: 4 years
Skills: Java, Spring, SQL, Kubernetes
""",
    ),
]


def main():
    out = Path("sample_data")
    out.mkdir(exist_ok=True)
    for filename, content in SAMPLES:
        (out / filename).write_text(content)
    print(f"Wrote {len(SAMPLES)} sample resumes to {out}")


if __name__ == "__main__":
    main()
