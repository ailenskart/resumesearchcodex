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
    (
        "neha_kapoor.txt",
        """Neha Kapoor
Engineering Manager
Location: Gurgaon
Email: neha@example.com
Experience: 10 years
Skills: Python, AWS, Kubernetes, Leadership, SQL
Worked at: Innotech Labs
""",
    ),
]


def seed_demo_resumes(folder: str = "sample_data") -> int:
    out = Path(folder)
    out.mkdir(exist_ok=True)
    for filename, content in SAMPLES:
        (out / filename).write_text(content)
    return len(SAMPLES)
