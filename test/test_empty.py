#!/usr/bin/env python3
import sys
from pathlib import Path

src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

print("Importing empty_test...")
import empty_test
print("✓ Success")