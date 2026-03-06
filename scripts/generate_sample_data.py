from app.demo_data import seed_demo_resumes


def main():
    count = seed_demo_resumes("sample_data")
    print(f"Wrote {count} sample resumes to sample_data")


if __name__ == "__main__":
    main()
