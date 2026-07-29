import re
from datetime import datetime
from langchain_core.documents import Document


def parse_logs(filepath: str) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_entries = content.split("---")
    raw_entries = [e.strip() for e in raw_entries if e.strip()]

    documents = []
    for entry in raw_entries:
        metadata = _extract_metadata(entry)
        doc = Document(page_content=entry, metadata=metadata)
        documents.append(doc)

    print(f"Parsed {len(documents)} log entries")
    return documents


def _extract_metadata(entry: str) -> dict:
    metadata = {
        "source": "personal_log",
        "date": "unknown",
        "week": "unknown",
        "day_of_week": "unknown",
        "type": "unknown",
        "muscles_trained": [],
        "exercise_names": [],
        "protein_g": 0,
        "calories": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "mood": "unknown",
        "is_rest_day": False,
    }

    date_match = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", entry)
    if date_match:
        date_str = date_match.group(1)
        metadata["date"] = date_str
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            metadata["week"] = dt.strftime("%Y-W%W")
            metadata["day_of_week"] = dt.strftime("%A")
        except ValueError:
            pass

    type_match = re.search(r"Type:\s*(.+)", entry)
    if type_match:
        entry_type = type_match.group(1).strip()
        metadata["type"] = entry_type
        metadata["is_rest_day"] = "rest" in entry_type.lower()

    muscles_match = re.search(r"Muscles Trained:\s*(.+)", entry)
    if muscles_match:
        muscles_raw = muscles_match.group(1).strip()
        metadata["muscles_trained"] = [m.strip() for m in muscles_raw.split(",")]

    exercise_matches = re.findall(r"-\s+([A-Za-z\s]+):\s+[\d]", entry)
    if exercise_matches:
        metadata["exercise_names"] = [e.strip() for e in exercise_matches]

    protein_match = re.search(r"Protein:\s*(\d+)g", entry)
    if protein_match:
        metadata["protein_g"] = int(protein_match.group(1))

    calorie_match = re.search(r"Calories:\s*(\d+)", entry)
    if calorie_match:
        metadata["calories"] = int(calorie_match.group(1))

    carbs_match = re.search(r"Carbs:\s*(\d+)g", entry)
    if carbs_match:
        metadata["carbs_g"] = int(carbs_match.group(1))

    fat_match = re.search(r"Fat:\s*(\d+)g", entry)
    if fat_match:
        metadata["fat_g"] = int(fat_match.group(1))

    notes_match = re.search(r"Notes:\s*(.+)", entry, re.IGNORECASE)
    if notes_match:
        notes = notes_match.group(1).lower()
        if any(w in notes for w in ["tired", "exhausted", "fatigued"]):
            metadata["mood"] = "tired"
        elif any(w in notes for w in ["strong", "great", "good", "solid"]):
            metadata["mood"] = "strong"
        elif any(w in notes for w in ["sore", "ache", "pain"]):
            metadata["mood"] = "sore"
        else:
            metadata["mood"] = "average"

    return metadata


def preview_parsed_logs(documents: list):
    print("\n" + "="*50)
    print(f"PARSED {len(documents)} LOG ENTRIES")
    print("="*50)
    for i, doc in enumerate(documents):
        m = doc.metadata
        print(f"\n[Entry {i+1}]")
        print(f"  Date      : {m['date']} ({m['day_of_week']})")
        print(f"  Type      : {m['type']}")
        print(f"  Muscles   : {m['muscles_trained']}")
        print(f"  Exercises : {m['exercise_names']}")
        print(f"  Protein   : {m['protein_g']}g")
        print(f"  Calories  : {m['calories']}")
        print(f"  Mood      : {m['mood']}")
        print(f"  Content   : {doc.page_content[:60]}...")
