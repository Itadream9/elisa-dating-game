"""
Memory module for IL CUSTODE DEL CAVEAU
ChromaDB-based RAG for persistent player memory ("Memoria del Rancore")
"""
import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
from typing import List, Dict

# ChromaDB persistent storage
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "data", "chroma")

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Create or get collection for player interactions
collection = client.get_or_create_collection(
    name="player_failures",
    metadata={"description": "Memoria del Rancore - Player failures and humiliations"}
)


def store_interaction(session_id: str, user_message: str, ai_response: str, failed: bool = True):
    """
    Store a player interaction in the memory database.
    
    Args:
        session_id: Unique player session identifier
        user_message: What the player said
        ai_response: How the Custode responded
        failed: Whether this was a failed attempt (always True, they never win)
    """
    timestamp = datetime.now().isoformat()
    doc_id = f"{session_id}_{timestamp}"
    
    # Create a summary of the failed attempt
    failure_summary = f"TENTATIVO FALLITO: L'utente ha detto: '{user_message}'. Il Custode ha risposto: '{ai_response}'"
    
    collection.add(
        documents=[failure_summary],
        metadatas=[{
            "session_id": session_id,
            "timestamp": timestamp,
            "user_message": user_message[:500],  # Truncate for metadata
            "failed": str(failed)
        }],
        ids=[doc_id]
    )


def get_player_failures(session_id: str, n_results: int = 3) -> List[Dict]:
    """
    Retrieve the last N failures for a specific player.
    This is used to build the "Memoria del Rancore" for context.
    
    Args:
        session_id: Unique player session identifier
        n_results: Number of past failures to retrieve
        
    Returns:
        List of failure dictionaries with document and metadata
    """
    try:
        results = collection.query(
            query_texts=[f"fallimenti di {session_id}"],
            n_results=n_results * 2,  # Get more to filter
            where={"session_id": session_id}
        )
        
        if not results or not results["documents"] or not results["documents"][0]:
            return []
        
        failures = []
        for i, doc in enumerate(results["documents"][0][:n_results]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            failures.append({
                "document": doc,
                "timestamp": metadata.get("timestamp", ""),
                "user_message": metadata.get("user_message", "")
            })
        
        return failures
        
    except Exception as e:
        print(f"Error retrieving failures: {e}")
        return []


def build_rancore_context(session_id: str) -> str:
    """
    Build the "Memoria del Rancore" context string for the AI prompt.
    
    Args:
        session_id: Unique player session identifier
        
    Returns:
        Formatted string with past failures for context injection
    """
    failures = get_player_failures(session_id)
    
    if not failures:
        return "Questo è un nuovo supplicante. Non ha ancora una storia di fallimenti... ma presto ne avrà."
    
    context_parts = ["=== MEMORIA DEL RANCORE ===", "Ecco i patetici tentativi passati di questo supplicante:"]
    
    for i, failure in enumerate(failures, 1):
        context_parts.append(f"\n{i}. {failure['document']}")
    
    context_parts.append("\nUsa questi fallimenti per umiliarlo ulteriormente.")
    
    return "\n".join(context_parts)


def get_total_interactions(session_id: str) -> int:
    """Get total number of interactions for a player."""
    try:
        results = collection.get(
            where={"session_id": session_id}
        )
        return len(results["ids"]) if results and results["ids"] else 0
    except Exception:
        return 0
