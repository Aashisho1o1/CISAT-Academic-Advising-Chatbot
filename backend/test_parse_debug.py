"""Debug LandingAI parse response structure"""
import os
from pathlib import Path
from dotenv import load_dotenv
from landingai_ade import LandingAIADE

load_dotenv()

api_key = os.environ.get("VISION_AGENT_API_KEY")
if not api_key:
    raise RuntimeError("VISION_AGENT_API_KEY not set in .env")

client = LandingAIADE(apikey=api_key)

# Test with your actual PDF
test_file = Path("uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf")

if not test_file.exists():
    print(f"❌ File not found: {test_file}")
    print(f"   Current directory: {Path.cwd()}")
    print(f"   Available files in uploads:")
    for f in Path("uploads").glob("*.pdf"):
        print(f"     - {f.name}")
    exit(1)

print(f"✅ Testing with: {test_file} ({test_file.stat().st_size} bytes)")

# Parse the document
try:
    print("\n📄 Calling LandingAI parse API...")
    response = client.parse(
        document=test_file,
        model="dpt-2-latest"
    )
    
    print(f"✅ Parse succeeded!")
    print(f"\n🔍 Response type: {type(response)}")
    print(f"🔍 Response attributes: {dir(response)}")
    
    # Try to access chunks
    if hasattr(response, 'chunks'):
        print(f"\n✅ Has chunks attribute")
        print(f"   Chunks type: {type(response.chunks)}")
        print(f"   Chunks length: {len(response.chunks)}")
        
        if len(response.chunks) > 0:
            first_chunk = response.chunks[0]
            print(f"\n📦 First chunk type: {type(first_chunk)}")
            print(f"   First chunk attributes: {dir(first_chunk)}")
            
            # Try different ways to get text
            print("\n🔧 Attempting to extract text:")
            
            # Method 1: Direct attribute
            if hasattr(first_chunk, 'text'):
                print(f"   ✅ chunk.text exists: {first_chunk.text[:200]}")
            else:
                print(f"   ❌ chunk.text does NOT exist")
            
            # Method 2: model_dump()
            if hasattr(first_chunk, 'model_dump'):
                chunk_dict = first_chunk.model_dump()
                print(f"   ✅ chunk.model_dump() keys: {chunk_dict.keys()}")
                if 'text' in chunk_dict:
                    print(f"   ✅ chunk.model_dump()['text']: {chunk_dict['text'][:200]}")
                else:
                    print(f"   ❌ 'text' not in chunk.model_dump()")
                    print(f"   Full chunk data: {chunk_dict}")
            
            # Method 3: dict()
            if hasattr(first_chunk, 'dict'):
                chunk_dict = first_chunk.dict()
                print(f"   ✅ chunk.dict() keys: {chunk_dict.keys()}")
                if 'text' in chunk_dict:
                    print(f"   ✅ chunk.dict()['text']: {chunk_dict['text'][:200]}")
            
            # Method 4: Convert to string
            print(f"\n   String repr: {str(first_chunk)[:500]}")
        else:
            print(f"\n⚠️  Chunks list is empty!")
    else:
        print(f"❌ No chunks attribute")
        print(f"   Available attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
    
except Exception as e:
    print(f"❌ Parse failed: {e}")
    import traceback
    traceback.print_exc()
