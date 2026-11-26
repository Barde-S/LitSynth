#!/usr/bin/env python3
"""
Quick test to verify all imports work before starting the server
"""
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

print("=" * 60)
print("Testing LitSynth Imports...")
print("=" * 60)

try:
    print("✓ Testing main imports...")
    import main
    print("  ✓ main.py loaded successfully")
except Exception as e:
    print(f"  ✗ Error loading main.py: {e}")
    sys.exit(1)

try:
    print("✓ Testing chat module...")
    import chat
    print("  ✓ chat.py loaded successfully")
    print(f"  ✓ LLM model: {chat.llm.model}")
except Exception as e:
    print(f"  ✗ Error loading chat.py: {e}")
    sys.exit(1)

try:
    print("✓ Testing vector module...")
    import vector
    print("  ✓ vector.py loaded successfully")
    print(f"  ✓ Embedding model: {vector.EMBEDDING_MODEL}")
except Exception as e:
    print(f"  ✗ Error loading vector.py: {e}")
    sys.exit(1)

try:
    print("✓ Testing models...")
    import models
    print("  ✓ models.py loaded successfully")
except Exception as e:
    print(f"  ✗ Error loading models.py: {e}")
    sys.exit(1)

try:
    print("✓ Testing processors...")
    import processors
    print("  ✓ processors.py loaded successfully")
except Exception as e:
    print(f"  ✗ Error loading processors.py: {e}")
    sys.exit(1)

print("=" * 60)
print("✅ All imports successful!")
print("=" * 60)
print("\nYou're ready to start the server:")
print("  cd src && uvicorn main:app --reload --port 8000")
print("\nOr use the startup script:")
print("  ./start.sh")
