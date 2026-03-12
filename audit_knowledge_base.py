#!/usr/bin/env python3
"""
Knowledge Base Audit Tool for Mechanic Chatbot
Check apa yang ada di Google Drive folders dan assess adequacy untuk use case bengkel
"""

import json
import sys
from pathlib import Path

def print_section(title, char="="):
    """Print formatted section header"""
    print(f"\n{char * 90}")
    print(f"  {title}")
    print(f"{char * 90}\n")

def print_checklist(items, category):
    """Print interactive checklist"""
    print(f"📋 {category}:")
    print("-" * 80)
    results = {}
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item['question']}")
        print(f"   Examples: {item['examples']}")
        answer = input("   Status (Y/N/partial/unknown): ").strip().lower()
        results[item['id']] = answer
    return results

def audit_knowledge_base():
    """Interactive knowledge base audit"""
    print_section("🔧 MECHANIC CHATBOT - KNOWLEDGE BASE AUDIT", "=")
    
    print("""
This tool helps you assess if your knowledge base is adequate for bengkel mechanics.

We'll check:
1. CONTENT COVERAGE - Do you have essential docs?
2. DEPTH QUALITY - How detailed are your docs?
3. GAPS - What's missing?
4. IMPROVEMENT PRIORITY - What to add first?

Let's start!
""")
    
    audit_results = {}
    
    # ============== SECTION 1: EBOOKS FOLDER ==============
    print_section("Section 1: EBOOKS Folder Analysis", "-")
    print("""
Location: Google Drive → EBOOKS folder
Purpose: Should contain service manuals and technical guides
""")
    
    ebooks_items = [
        {
            "id": "ebooks_suzuki",
            "question": "Do you have Suzuki Shogun/Swift service manuals?",
            "examples": "Suzuki Shogun 1.3L service manual, wiring diagram, etc"
        },
        {
            "id": "ebooks_daihatsu", 
            "question": "Do you have Daihatsu Avanza/Xenia/Taruna service manuals?",
            "examples": "Daihatsu Avanza 1.3L, mechanical overhaul guides, etc"
        },
        {
            "id": "ebooks_others",
            "question": "Other brands coverage?",
            "examples": "Toyota, Mitsubishi, Honda, etc - which ones?"
        },
        {
            "id": "ebooks_wiring",
            "question": "Do you have wiring diagrams/electrical guides?",
            "examples": "Complete wiring diagrams, electrical troubleshooting"
        },
        {
            "id": "ebooks_detail",
            "question": "How detailed are the manuals? (step-by-step or just overview?)",
            "examples": "With images/diagrams?: YES/PARTIAL/NO"
        }
    ]
    
    audit_results['ebooks'] = print_checklist(ebooks_items, "EBOOKS Content")
    
    # ============== SECTION 2: PENGETAHUAN FOLDER ==============
    print_section("Section 2: PENGETAHUAN (Knowledge) Folder Analysis", "-")
    print("""
Location: Google Drive → Pengetahuan folder
Purpose: Should contain knowledge base like maintenance intervals, troubleshooting, common issues
""")
    
    pengetahuan_items = [
        {
            "id": "peng_maintenance",
            "question": "Do you have maintenance interval schedules?",
            "examples": "Service intervals for different brands (5K, 10K, 20K KM checkpoints)"
        },
        {
            "id": "peng_common_problems",
            "question": "Common problems & solutions documented?",
            "examples": "'Engine mogok', 'Boros BBM', 'Overheating', etc with diagnosis"
        },
        {
            "id": "peng_torque_specs",
            "question": "Do you have torque specifications tables?",
            "examples": "Engine bolt torque, transmission, suspension specs - CRITICAL for quality"
        },
        {
            "id": "peng_safety",
            "question": "Safety procedures documented?",
            "examples": "Proper lifting, lockout/tagout, PPE requirements, precautions"
        },
        {
            "id": "peng_parts_compat",
            "question": "Parts compatibility/OEM specifications?",
            "examples": "OEM part numbers, compatible alternatives"
        },
        {
            "id": "peng_system_overview",
            "question": "How systems work (engine, transmission, electrical, etc)?",
            "examples": "System overview docs, principle of operation"
        }
    ]
    
    audit_results['pengetahuan'] = print_checklist(pengetahuan_items, "PENGETAHUAN Content")
    
    # ============== SECTION 3: SERVICE MANUAL FOLDERS ==============
    print_section("Section 3: Service Manual 1 & 2 Folders Analysis", "-")
    print("""
Location: Google Drive → Service_Manual_1 and Service_Manual_2
Purpose: Detailed repair procedures, diagnostic trees, technical specifications
""")
    
    service_items = [
        {
            "id": "service_diagnostic",
            "question": "Diagnostic procedures structured (decision trees)?",
            "examples": "If symptom X → Check Y → If result Z → Do this..."
        },
        {
            "id": "service_procedures",
            "question": "Step-by-step repair procedures?",
            "examples": "Complete 'how-to' with all steps numbered and detailed"
        },
        {
            "id": "service_coverage",
            "question": "System coverage - which systems documented?",
            "examples": "Engine / Transmission / Suspension / Brake / Electrical / AC"
        },
        {
            "id": "service_components",
            "question": "Component-level procedures available?",
            "examples": "How to replace: starter, alternator, fuel pump, injection system"
        },
        {
            "id": "service_specs",
            "question": "Specifications clearly listed?",
            "examples": "Clearances, gaps, torque, pressures, viscosity grades"
        }
    ]
    
    audit_results['service_manual'] = print_checklist(service_items, "SERVICE MANUAL Content")
    
    # ============== SUMMARY & SCORES ==============
    print_section("📊 AUDIT SUMMARY & SCORING", "=")
    
    # Calculate scores
    total_yes = 0
    total_items = 0
    
    for section, results in audit_results.items():
        yes_count = sum(1 for v in results.values() if v == 'y')
        total_count = len(results)
        score = (yes_count / total_count * 100) if total_count > 0 else 0
        total_yes += yes_count
        total_items += total_count
        
        print(f"\n{section.upper()}:")
        print(f"  Score: {yes_count}/{total_count} ({score:.0f}%)")
        
        # Show missing items
        missing = [k for k, v in results.items() if v != 'y']
        if missing:
            print(f"  Gaps: {', '.join(missing)}")
    
    overall_score = (total_yes / total_items * 100) if total_items > 0 else 0
    
    print(f"\n{'=' * 80}")
    print(f"OVERALL KNOWLEDGE BASE SCORE: {overall_score:.0f}%")
    print(f"{'=' * 80}\n")
    
    # ============== GRADING & RECOMMENDATIONS ==============
    if overall_score >= 80:
        grade = "🟢 EXCELLENT"
        action = "Knowledge base is solid. Focus on AI tuning & formatting."
    elif overall_score >= 60:
        grade = "🟡 GOOD"
        action = "Good foundation. Add critical gaps (diagnostic trees, specs)."
    elif overall_score >= 40:
        grade = "🟠 FAIR"
        action = "Basic content exists. Significant gaps need filling."
    else:
        grade = "🔴 NEEDS WORK"
        action = "Critical gaps. Major documentation work needed."
    
    print(f"Grade: {grade}")
    print(f"Recommendation: {action}")
    
    # ============== PRIORITIES ==============
    print_section("Priority Improvements", "-")
    
    critical_gaps = {
        'peng_torque_specs': "🔴 CRITICAL - Torque specs are essential for quality",
        'service_diagnostic': "🔴 CRITICAL - Decision trees needed for diagnosis",
        'peng_safety': "🔴 CRITICAL - Safety procedures non-negotiable",
        'service_procedures': "🟠 HIGH - Step-by-step procedures expected",
        'ebooks_wiring': "🟠 HIGH - Electrical troubleshooting relies on diagrams",
        'peng_common_problems': "🟠 HIGH - Real problem solutions valuable",
        'service_specs': "🟡 MEDIUM - Specs important but can reference generics",
        'service_components': "🟡 MEDIUM - Component knowledge builds over time",
    }
    
    print("Based on your audit, here are critical gaps:\n")
    
    gap_count = 1
    for item_id, description in critical_gaps.items():
        # Check if this item was marked as missing
        for section, results in audit_results.items():
            if item_id in results and results[item_id] != 'y':
                print(f"{gap_count}. {description}")
                gap_count += 1
    
    # ============== NEXT STEPS ==============
    print_section("Next Steps", "-")
    
    print("""
Based on this audit:

IMMEDIATE (This Week):
  1. Add missing critical content to folders
  2. Organize documents with consistent naming
  3. Verify all PDFs are searchable text (not images)

SHORT TERM (This Month):
  1. Create diagnostic decision trees (structured)
  2. Add complete torque specifications table
  3. Document safety procedures
  4. Implement search optimization for bengkel terms

THEN:
  1. Let me optimize AI responses for mechanics
  2. Add specialized searches for diagnosis
  3. Fine-tune formatting for bengkel workflow

HAVE YOU NOTICED:
  - Which document types are most accessed?
  - Which questions repeat most often?
  - Any gaps that customers/mechanics complain about?
""")
    
    return overall_score >= 60

def quick_assessment():
    """Quick version without interactive questions"""
    print_section("⚡ QUICK KNOWLEDGE BASE ASSESSMENT", "=")
    
    print("""
Answer these quickly (Y/N) to get a fast assessment:

CRITICAL ITEMS (must have):
1. Service manuals for your target brands? (Y/N)
2. Torque specifications documented? (Y/N)
3. Diagnostic procedures available? (Y/N)
4. Safety procedures documented? (Y/N)

IMPORTANT ITEMS (should have):
5. Maintenance interval schedules? (Y/N)
6. Common problems & solutions? (Y/N)
7. Wiring diagrams/electrical guides? (Y/N)

NICE TO HAVE:
8. Parts compatibility info? (Y/N)
9. System overviews/theory guides? (Y/N)
10. Component-level procedures? (Y/N)
""")
    
    score = 0
    responses = []
    
    for i in range(10):
        resp = input(f"Item {i+1}: ").strip().upper()
        if resp == 'Y':
            score += 1
        responses.append(resp)
    
    percentage = (score / 10) * 100
    
    print(f"\n{'=' * 80}")
    print(f"QUICK SCORE: {score}/10 ({percentage:.0f}%)")
    print(f"{'=' * 80}\n")
    
    if percentage >= 80:
        print("✅ Your KB looks solid! Now focus on AI optimization.")
    elif percentage >= 60:
        print("⚠️ Good base, but fill the gaps (esp: torque & diagnostics).")
    elif percentage >= 40:
        print("🔄 Need more content. Prioritize: manuals, specs, safety.")
    else:
        print("❌ KB needs significant work before AI can be effective.")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Base Audit for Mechanic Chatbot')
    parser.add_argument('--quick', action='store_true', help='Quick 10-question assessment')
    parser.add_argument('--full', action='store_true', help='Full interactive audit')
    
    args = parser.parse_args()
    
    # Default to full if no args
    if not args.quick and not args.full:
        print("\nMekanik Chatbot - Knowledge Base Audit Tool")
        print("=" * 80)
        print("Choose mode:")
        print("  1. Quick assessment (10 questions) - 5 minutes")
        print("  2. Full interactive audit (detailed) - 15 minutes")
        print("  3. Both")
        print()
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == '1':
            args.quick = True
        elif choice == '2':
            args.full = True
        elif choice == '3':
            args.quick = True
            args.full = True
        else:
            args.full = True  # Default
    
    try:
        if args.quick:
            quick_assessment()
        
        if args.full:
            audit_knowledge_base()
        
        print("\n" + "=" * 80)
        print("NEXT STEP:")
        print("  When ready, send me the results and I will:")
        print("  1. Optimize AI system prompt for mechanics")
        print("  2. Add keyword synonyms for bengkel terminology") 
        print("  3. Adjust response templates for diagnosis format")
        print("  4. Create diagnostic tools if KB supports it")
        print("=" * 80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nAudit cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
