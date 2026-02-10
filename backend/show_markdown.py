"""See what markdown LandingAI actually parsed"""
import os
from pathlib import Path
from dotenv import load_dotenv
from landingai_service import LandingAIService

load_dotenv()

service = LandingAIService()
test_file = Path("uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf")

# Just parse, don't extract
print("📄 Parsing PDF to markdown...")
markdown = service.parse_document_to_markdown(test_file)

print("\n" + "=" * 80)
print("FULL MARKDOWN CONTENT:")
print("=" * 80)
print(markdown)
print("\n" + "=" * 80)
print(f"Total length: {len(markdown)} characters")
print("=" * 80)

# Save to file for inspection
output_file = Path("uploads/parsed_markdown.md")
output_file.write_text(markdown)
print(f"\n✅ Saved to: {output_file}")
