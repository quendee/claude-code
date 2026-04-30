#!/usr/bin/env python3
"""
Run all steps of the Tool Selection Learning Exercise
=====================================================

This script runs each step in sequence, showing the progression
from minimal to complete.
"""

import subprocess
import sys
from pathlib import Path


def run_step(step_num: int, filename: str, description: str):
    """Run a step script"""
    print("\n")
    print("=" * 70)
    print(f"RUNNING STEP {step_num}: {description}")
    print("=" * 70)
    print()
    
    script_path = Path(__file__).parent / filename
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            print(f"Error running {filename}")
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 70)
    print("Tool Selection System - Progressive Learning Exercise")
    print("=" * 70)
    print()
    print("This exercise builds up the tool selection system from minimal")
    print("to complete, matching the architecture in claude-code/")
    print()
    
    steps = [
        (1, "step1_minimal.py", "Minimal Tool Selection"),
        (2, "step2_registry.py", "Tool Registry with Metadata"),
        (3, "step4_modes.py", "Mode-Based Tool Selection"),
        (4, "step5_full_system.py", "Complete System with MCP Integration"),
    ]
    
    success_count = 0
    
    for step_num, filename, description in steps:
        if run_step(step_num, filename, description):
            success_count += 1
            
            # Pause between steps
            if step_num < len(steps):
                input("\nPress Enter to continue to the next step...")
        else:
            print(f"\nFailed to run Step {step_num}")
            break
    
    print()
    print("=" * 70)
    print("EXERCISE COMPLETE")
    print("=" * 70)
    print()
    print(f"Successfully ran {success_count}/{len(steps)} steps")
    print()
    
    if success_count == len(steps):
        print("Congratulations! You now understand:")
        print("  ✓ How tools are defined and registered")
        print("  ✓ How permissions filter tool access")
        print("  ✓ How execution modes change tool availability")
        print("  ✓ How built-in and MCP tools are assembled")
        print("  ✓ How the complete system works")
        print()
        print("You can now read src/tools.ts and understand every line!")
    
    print()
    print("Next steps:")
    print("  1. Read src/Tool.ts to see the Tool interface")
    print("  2. Read src/tools.ts to see getAllBaseTools()")
    print("  3. Read src/utils/permissions/permissions.ts for deny rules")
    print("  4. Read src/services/tools/ for execution logic")
    print()


if __name__ == "__main__":
    main()
