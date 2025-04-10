import requests

def get_orcid_works(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/vnd.orcid+json"}
    resp = requests.get(url, headers=headers)
    return resp.json().get("group", [])

def get_work_detail(orcid_id, put_code):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    headers = {"Accept": "application/vnd.orcid+json"}
    resp = requests.get(url, headers=headers)
    return resp.json()

# Map ORCID work types to RIS types
ORCID_TO_RIS_TYPE = {
    "journal-article": "JOUR",
    "book": "BOOK",
    "book-chapter": "CHAP",
    "conference-paper": "CONF",
    "report": "RPRT",
    "dissertation": "THES",
    "other": "GEN"
}

def format_ris(work, put_code):
    title = (
        work.get("title", {})
        .get("title", {})
        .get("value", "No Title")
    )

    # print(work)
    pub_date = work.get("publication-date", {})

    year = ""

    if pub_date is not None:
        year_info = pub_date.get("year")
        year = year_info.get("value", "") if isinstance(year_info, dict) else ""

    # Defensive handling of missing journal title
    journal = (
        work.get("journal-title", {}) or {}
    ).get("value", "")

    # Handle work type and fallback to generic RIS type
    work_type = work.get("type", "other")
    ris_type = ORCID_TO_RIS_TYPE.get(work_type.lower(), "GEN")

    # Defensive extraction of contributors
    contributors = work.get("contributors", {}).get("contributor", [])
    authors = []
    for contributor in contributors:
        credit_name = contributor.get("credit-name")
        if isinstance(credit_name, dict):
            name = credit_name.get("value")
            if name:
                authors.append(name)


    doi = ""
    external_ids = work.get("external-ids", {})
    external_id_list = external_ids.get("external-id") or []
    for ext_id in external_id_list:
        if ext_id.get("external-id-type") == "doi":
            doi = ext_id.get("external-id-value", "")
            break

    ris = []
    ris.append(f"TY  - {ris_type}")
    for author in authors:
        ris.append(f"AU  - {author}")
    ris.append(f"TI  - {title}")
    if journal:
        ris.append(f"JO  - {journal}")
    if year:
        ris.append(f"PY  - {year}")
    if doi:
        ris.append(f"DO  - {doi}")
    ris.append(f"ID  - {put_code}")
    ris.append("ER  -\n")
    return "\n".join(ris)

def export_orcid_to_ris(orcid_id):
    groups = get_orcid_works(orcid_id)
    ris_entries = []

    for group in groups:
        summary = group["work-summary"][0]
        put_code = summary["put-code"]
        work = get_work_detail(orcid_id, put_code)
        ris = format_ris(work, put_code)
        ris_entries.append(ris)

    return "\n".join(ris_entries)

# === Replace with your ORCID iD ===
orcid_id = "0000-0002-1774-5530"  # replace with your ORCID iD
ris_output = export_orcid_to_ris(orcid_id)

with open("orcid_export.ris", "w", encoding="utf-8") as f:
    f.write(ris_output)

print("RIS file saved as 'orcid_export.ris'")