"""Seed fictional data. Never use patient or proprietary documents in this demo."""
from app.embeddings import embed
from app.repository import insert_chunk

DOCUMENTS = [
    ("SYN-QA-001", "healthcare_org_001", "Quality Assurance",
     "Synthetic deviation review procedure: record investigation and corrective action.",
     ["qa_reviewer", "quality_manager"]),
    ("SYN-QA-002", "healthcare_org_001", "Quality Assurance",
     "Synthetic laboratory quality control checklist for batch review.",
     ["quality_manager"]),
    ("SYN-RD-001", "healthcare_org_001", "Research",
     "Synthetic research study protocol for experimental screening.",
     ["researcher"]),
    ("SYN-QA-OTHER-TENANT", "healthcare_org_002", "Quality Assurance",
     "Synthetic confidential deviation record belonging to another tenant.",
     ["qa_reviewer"]),
]

if __name__ == "__main__":
    for doc_id, tenant, dept, content, roles in DOCUMENTS:
        insert_chunk(doc_id, tenant, dept, content, roles, embed(content))
    print("Inserted synthetic records (run once per new database).")
