#!/usr/bin/env python3
"""Test script for MessageNormalizer functionality"""

from app.automation.message_normalizer import MessageNormalizer

def test_normalization():
    """Test all normalization rules"""
    
    normalizer = MessageNormalizer()
    
    # Test case 1: HEPSİ-500 -> HEPSI-500
    input1 = "HEPSİ-500"
    output1 = normalizer.normalize(input1)
    print(f"Input: {input1}")
    print(f"Output: {output1}")
    print(f"Expected: HEPSI-500")
    print(f"Match: {output1 == 'HEPSI-500'}")
    print()
    
    # Test case 2: ŞOK2026 -> SOK2026
    input2 = "ŞOK2026"
    output2 = normalizer.normalize(input2)
    print(f"Input: {input2}")
    print(f"Output: {output2}")
    print(f"Expected: SOK2026")
    print(f"Match: {output2 == 'SOK2026'}")
    print()
    
    # Test case 3: WELCOME2026 -> WELCOME2026 (no Turkish chars)
    input3 = "WELCOME2026"
    output3 = normalizer.normalize(input3)
    print(f"Input: {input3}")
    print(f"Output: {output3}")
    print(f"Expected: WELCOME2026")
    print(f"Match: {output3 == 'WELCOME2026'}")
    print()
    
    # Test case 4: Multiple spaces, CRLF, blank lines
    input4 = "Multiple spaces,\n\nCRLF,\r\n\r\nblank lines"
    output4 = normalizer.normalize(input4)
    print(f"Input: {repr(input4)}")
    print(f"Output: {repr(output4)}")
    print()
    
    # Test case 5: Unicode normalization
    input5 = "café"
    output5 = normalizer.normalize(input5)
    print(f"Input: {repr(input5)}")
    print(f"Output: {repr(output5)}")
    print()

if __name__ == "__main__":
    test_normalization()