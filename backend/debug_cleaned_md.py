"""Debug: See what the cleaned markdown looks like after HTML stripping"""
import re
from html import unescape
from pathlib import Path
from landingai_service import LandingAIService

service = LandingAIService()
test_file = Path("uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf")

# Parse to get markdown with HTML
markdown_with_html = service.parse_document_to_markdown(test_file)

# Strip HTML (same as in regex function)
clean_markdown = re.sub(r'<[^>]+>', ' ', markdown_with_html)
clean_markdown = unescape(clean_markdown)
clean_markdown = re.sub(r'\s+', ' ', clean_markdown)

print("=" * 80)
print("CLEANED MARKDOWN (first 2000 chars):")
print("=" * 80)
print(clean_markdown[:2000])
print("\n" + "=" * 80)
print("FULL CLEANED MARKDOWN:")
print("=" * 80)
print(clean_markdown)

# Save for inspection
Path("uploads/cleaned_markdown.txt").write_text(clean_markdown)
print("\n✅ Saved to uploads/cleaned_markdown.txt")
