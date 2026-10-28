#!/usr/bin/env python3
"""
BankFlow: Efficient Bank Transaction Processing System Using Data Structures and Algorithms
Entry-point launcher for the Desktop Application.
"""
import sys
import os

# Ensure the root project directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import launch


def main():
    print("=" * 70)
    print(" BankFlow: Efficient Bank Transaction Processing System (DSA)")
    print("=" * 70)
    print("Launching Desktop GUI...")
    launch()


if __name__ == "__main__":
    main()
