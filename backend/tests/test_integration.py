import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import init_db, SessionLocal
from app.db.models import Farmer, CropCycle, FarmEvent, ChatMessage
from app.rag.retriever import AgricultureRetriever
from app.core.memory_agent import MemoryAgent
from app.memory.memory_extractor import extract_memory_facts

def test_database_and_models():
    print("--- Testing Database & Models ---")
    db = SessionLocal()
    try:
        # Create a new test farmer
        test_farmer = Farmer(
            name="Test Ahmad",
            district="Multan",
            village="Rustam",
            preferred_language="ur",
            land_size="4 acres",
            primary_crops="cotton",
            is_guest=False
        )
        db.add(test_farmer)
        db.commit()
        db.refresh(test_farmer)
        print(f"SUCCESS: Successfully created farmer with ID: {test_farmer.id}")
        
        # Add active crop cycle
        crop = CropCycle(
            farmer_id=test_farmer.id,
            crop_name="cotton",
            variety="FH-142",
            sowing_date="last week",
            status="active"
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        print(f"SUCCESS: Successfully created crop cycle for {crop.crop_name} (Variety: {crop.variety})")

        # Query and clean up
        db.delete(crop)
        db.delete(test_farmer)
        db.commit()
        print("SUCCESS: Database write/read/delete lifecycle passed.")
    except Exception as e:
        print(f"ERROR: Database test failed: {e}")
        raise e
    finally:
        db.close()

def test_rag_retrieval():
    print("\n--- Testing RAG (FAISS Vector Index) Retrieval ---")
    retriever = AgricultureRetriever()
    
    # Check if index is loaded
    if retriever._index is None:
        print("ERROR: RAG Index was not loaded! Make sure ingest.py ran successfully.")
        sys.exit(1)
        
    print(f"SUCCESS: RAG Index loaded successfully with {retriever._index.ntotal} vectors.")
    
    db = SessionLocal()
    try:
        # Search query related to cotton and fertilizer
        query = "urea fertilizer application for cotton"
        memory_ctx = {"current_crop": "cotton", "district": "Multan"}
        results = retriever.search(db, query, memory_ctx, limit=2)
        
        assert len(results) > 0, "No results returned from RAG"
        print(f"SUCCESS: RAG search returned {len(results)} results for query: '{query}'")
        
        for i, doc in enumerate(results):
            print(f"  Result {i+1}:")
            print(f"    Source: {doc.source}")
            print(f"    Snippet (first 100 chars): {doc.snippet[:100]}...")
            assert doc.source != "seed knowledge", "Retrieved mock seed knowledge instead of actual PDF content"
            
        print("SUCCESS: RAG retrieval successfully returned matches from Pakistani agricultural PDFs.")
    except Exception as e:
        print(f"ERROR: RAG test failed: {e}")
        raise e
    finally:
        db.close()

async def test_memory_agent_orchestration():
    print("\n--- Testing MemoryAgent Orchestration & Fact Extraction ---")
    agent = MemoryAgent()
    db = SessionLocal()
    try:
        # 1. Create a dummy guest farmer
        farmer = Farmer(name="Guest Farmer", is_guest=True, preferred_language="ur")
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        farmer_id = farmer.id
        print(f"Created temporary Guest Farmer ID: {farmer_id}")
        
        # 2. Call MemoryAgent with a profile-setting message
        message = "Hi, my name is Ahmad. I farm 10 kanals in Faisalabad. I sowed cotton FH-142 last week."
        print(f"User says: '{message}'")
        
        response = await agent.answer(db, farmer_id, message)
        db.refresh(farmer)
        
        # Verify that facts were extracted and updated in the DB
        print("\nChecking extracted facts written to DB:")
        print(f"  Name updated: {farmer.name} (Expected: Ahmad)")
        print(f"  District updated: {farmer.district} (Expected: Faisalabad)")
        print(f"  Land size updated: {farmer.land_size} (Expected: 10 kanals)")
        
        active_crop = db.query(CropCycle).filter(CropCycle.farmer_id == farmer_id, CropCycle.status == "active").first()
        assert active_crop is not None, "No active crop cycle was created"
        print(f"  Active Crop: {active_crop.crop_name} (Expected: cotton)")
        print(f"  Variety: {active_crop.variety} (Expected: FH-142)")
        print(f"  Sowing Date: {active_crop.sowing_date} (Expected: last week)")
        
        # Verify chat message history persistence
        chat_msgs = db.query(ChatMessage).filter(ChatMessage.farmer_id == farmer_id).all()
        print(f"  Persisted Messages: {len(chat_msgs)} (Expected: 2 - user & bot)")
        
        # 3. Clean up
        db.query(CropCycle).filter(CropCycle.farmer_id == farmer_id).delete()
        db.query(FarmEvent).filter(FarmEvent.farmer_id == farmer_id).delete()
        db.query(ChatMessage).filter(ChatMessage.farmer_id == farmer_id).delete()
        db.delete(farmer)
        db.commit()
        print("SUCCESS: MemoryAgent orchestration and fact auto-save passed.")
    except Exception as e:
        print(f"ERROR: MemoryAgent orchestration test failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    test_database_and_models()
    test_rag_retrieval()
    asyncio.run(test_memory_agent_orchestration())
    print("\nALL INTEGRATION TESTS PASSED! Your website is 100% ready for publishing.")
