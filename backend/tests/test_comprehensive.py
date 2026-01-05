"""
Comprehensive BOM Test - Compare all calculators with Excel values
Based on exact Excel data extracted from GRP_Tank_BOM_Analysis.xlsm
"""
import sys
sys.path.insert(0, '/home/khalid/dev/panel_tank_config/backend')

from app.services.panel_calculator import PanelCalculator
from app.services.steel_skid_calculator import SteelSkidCalculator
from app.services.tie_rod_calculator import TieRodCalculator
from app.services.bolts_calculator import BoltsCalculator
from app.services.reinforcing_calculator import ReinforcingCalculator
from app.services.etc_calculator import ETCCalculator


def get_part_qty(parts, part_no_contains):
    """Get quantity for a part by partial match"""
    for part in parts:
        if part_no_contains in part.get('part_no', ''):
            return part.get('quantity', 0)
    return 0


def run_all_calculators(width, length1, length2, length3, length4, height,
                        capacity=None, skid_type=1, tie_rod_material=4):
    """Run all calculators and return combined BOM"""
    if capacity is None:
        capacity = width * length1 * height

    results = {
        'dimensions': f'{width}x{length1}x{height}m',
        'panels': [],
        'steel_skid': [],
        'tie_rods': [],
        'bolts': [],
        'reinforcing': [],
        'etc': [],
        'summary': {}
    }

    # Panel Calculator
    panel_calc = PanelCalculator(width, length1, length2, length3, length4, height)
    results['panels'] = panel_calc.calculate_all_panels()

    # Steel Skid Calculator
    skid_calc = SteelSkidCalculator(width, length1, length2, length3, length4, height, skid_type)
    results['steel_skid'] = skid_calc.calculate_all_parts()

    # Tie Rod Calculator
    tie_rod_calc = TieRodCalculator(width, length1, length2, length3, length4, height, tie_rod_material)
    results['tie_rods'] = tie_rod_calc.calculate_all_parts()
    results['tie_rods'].extend(tie_rod_calc.get_tie_rod_accessories())

    # Reinforcing Calculator (run first to get values for Bolts)
    reinf_calc = ReinforcingCalculator(width, length1, length2, length3, length4, height)
    results['reinforcing'] = reinf_calc.calculate_all_parts()

    # Extract reinforcing quantities for Bolts Calculator
    ext_l22 = get_part_qty(results['reinforcing'], 'WCP-1780Z')  # Cross plate 2-hole
    ext_l23 = get_part_qty(results['reinforcing'], 'WCP-1616Z')  # Cross plate 4-hole
    ext_l24 = get_part_qty(results['reinforcing'], 'WCP-17120Z')  # Cross plate (if any)
    int_p18 = get_part_qty(results['reinforcing'], 'WCP-1616SA')  # Internal cross plate 4-hole
    int_p19 = get_part_qty(results['reinforcing'], 'WCP-1780SA')  # Internal cross plate 2-hole

    # Bolts Calculator (with reinforcing quantities)
    bolts_calc = BoltsCalculator(
        width, length1, length2, length3, length4, height,
        bolt_option=1, skid_type=skid_type, insulation_type=0,
        steel_skid_m9=0, steel_skid_m36=0,
        ext_reinforcing_l22=ext_l22, ext_reinforcing_l23=ext_l23, ext_reinforcing_l24=ext_l24,
        int_reinforcing_p18=int_p18, int_reinforcing_p19=int_p19
    )
    results['bolts'] = bolts_calc.calculate_all_parts()

    # ETC Calculator
    etc_calc = ETCCalculator(
        width, length1, length2, length3, length4, height,
        nominal_capacity=capacity,
        level_indicator_type=1,
        internal_ladder_material=2,
        external_ladder_material=1
    )
    results['etc'] = etc_calc.calculate_all_parts()

    # Summary
    results['summary'] = {
        'total_panels': sum(p.get('quantity', 0) for p in results['panels']),
        'total_steel_skid': sum(p.get('quantity', 0) for p in results['steel_skid']),
        'total_tie_rods': sum(p.get('quantity', 0) for p in results['tie_rods']),
        'total_bolts': sum(p.get('quantity', 0) for p in results['bolts']),
        'total_reinforcing': sum(p.get('quantity', 0) for p in results['reinforcing']),
        'total_etc': sum(p.get('quantity', 0) for p in results['etc']),
    }

    return results


def compare_with_excel(results, expected, tank_name):
    """Compare results with expected Excel values"""
    print(f"\n{'='*70}")
    print(f"Testing: {tank_name} ({results['dimensions']})")
    print('='*70)

    all_pass = True
    differences = []

    for category, expected_parts in expected.items():
        if category == 'summary':
            continue

        parts = results.get(category, [])
        print(f"\n{category.upper()}:")
        print("-" * 50)

        for part_no, exp_qty in expected_parts.items():
            actual_qty = get_part_qty(parts, part_no)
            status = "OK" if actual_qty == exp_qty else "DIFF"

            if actual_qty != exp_qty:
                all_pass = False
                differences.append(f"{part_no}: got {actual_qty}, expected {exp_qty}")

            print(f"  {part_no:25} | {actual_qty:5} | {exp_qty:5} | {status}")

    print(f"\n{'='*70}")
    if all_pass:
        print(f"RESULT: ALL TESTS PASSED for {tank_name}")
    else:
        print(f"RESULT: DIFFERENCES FOUND for {tank_name}")
        for diff in differences:
            print(f"  - {diff}")
    print('='*70)

    return all_pass, differences


def test_10x5x3():
    """Test 10x5x3m tank - main Excel test case"""
    results = run_all_calculators(10, 5, 0, 0, 0, 3)

    # Expected values from Excel (verified from extracted sheets)
    expected = {
        'panels': {
            # From Panel sheet - key values
        },
        'steel_skid': {
            'WFF-1990CLZ': 22,   # Main-L 2m (actual part name)
            'WFF-0990CLZ': 11,   # Main-L 1m (actual part name)
            'LNR-3.0T': 304,     # Liner pieces (actual part name and qty)
        },
        'tie_rods': {
            # For 10x5x3m: width_assemblies=27, length_assemblies=12 = 39 total
            # 39 assemblies × 4 = 156 nuts/washers
            'NUT(SA4)': 156,
            'BW(SA4)': 156,
        },
        'bolts': {
            'WBT-1035Z': 196,
            'WBT-1035SA4': 340,
            'WBT-1050Z': 1784,
            'WBT-1050SA4': 120,
            'WBT-1240Z': 60,
            'WBT-1440Z': 176,     # Verified calculation
            'WBT-14120RD': 172,
        },
        'reinforcing': {
            'WFB-0950ZP': 64,
            'WFB-1200Z': 26,
            'WCF-1000Z': 4,
            'WCF-2000Z': 4,
            'WCP-1780Z': 34,
            'WCP-1616Z': 26,
            'WCP-17160SA4': 26,
            'WCP-1760SA4': 26,
            'WBR-9090SA4': 4,
        },
        'etc': {
            'WAV-0100A': 2,
            'WRS-3000F': 9,
            'WLD-3000FI': 1,
            'WLD-3000ZO': 1,
            'Silicon': 5,
            'WLV-3000SET(G)': 1,
            'WST-0050RO': 659,
            'WST-0120RO': 13,
        },
    }

    return compare_with_excel(results, expected, "10x5x3m Tank")


def test_5x5x3():
    """Test 5x5x3m tank"""
    results = run_all_calculators(5, 5, 0, 0, 0, 3)

    expected = {
        'tie_rods': {
            'NUT': 96,
            'BW': 96,
        },
        'etc': {
            'WAV-0050A': 1,
            'WRS-3000F': 4,
            'WLD-3000FI': 1,
            'WLD-3000ZO': 1,
            'Silicon': 3,
            'WST-0120RO': 13,
        },
    }

    return compare_with_excel(results, expected, "5x5x3m Tank")


def test_5x5x2():
    """Test 5x5x2m tank"""
    results = run_all_calculators(5, 5, 0, 0, 0, 2)

    expected = {
        'steel_skid': {
            'LNR-3.0T': 166,  # Liner (standard 3.0T)
        },
        'tie_rods': {
            'NUT': 32,
            'BW': 32,
        },
        'etc': {
            'WAV-0050A': 1,
            'WRS-2000F': 4,
            'WLD-2000FI': 1,
            'WLD-2000ZO': 1,
            'WST-0120RO': 9,
        },
    }

    return compare_with_excel(results, expected, "5x5x2m Tank")


def test_10x8x3_partitioned():
    """Test 10x8x3m partitioned tank (10x4 + 10x4)"""
    results = run_all_calculators(10, 4, 4, 0, 0, 3)

    expected = {
        'etc': {
            'WAV-0100A': 4,      # More air vents for partitioned
            'WLD-3000FI': 2,     # 2 internal ladders (N_PA+1)
            'WLD-3000ZO': 1,
            'WLV-3000SET': 2,    # 2 level indicators (N_PA+1)
            'WST-0120RO': 13,
        },
    }

    return compare_with_excel(results, expected, "10x8x3m Partitioned Tank")


def run_full_bom_test():
    """Run comprehensive BOM comparison for main test case"""
    print("\n" + "="*70)
    print("FULL BOM COMPARISON - 10x5x3m Tank")
    print("="*70)

    results = run_all_calculators(10, 5, 0, 0, 0, 3, capacity=150)

    print("\n--- PANELS ---")
    for p in results['panels']:
        if p.get('quantity', 0) > 0:
            print(f"  {p['part_no']:30} x {p['quantity']}")

    print("\n--- STEEL SKID ---")
    for p in results['steel_skid']:
        if p.get('quantity', 0) > 0:
            print(f"  {p['part_no']:30} x {p['quantity']}")

    print("\n--- TIE RODS ---")
    for p in results['tie_rods']:
        if p.get('quantity', 0) > 0:
            print(f"  {p['part_no']:30} x {p['quantity']}")

    print("\n--- BOLTS ---")
    for p in results['bolts']:
        if p.get('quantity', 0) > 0:
            print(f"  {p['part_no']:30} x {p['quantity']}")

    print("\n--- REINFORCING ---")
    for p in results['reinforcing']:
        if p.get('quantity', 0) > 0:
            print(f"  {p['part_no']:30} x {p['quantity']}")

    print("\n--- ETC ---")
    for p in results['etc']:
        if p.get('quantity', 0) > 0:
            print(f"  {p['part_no']:30} x {p['quantity']}")

    print("\n--- SUMMARY ---")
    for key, val in results['summary'].items():
        print(f"  {key:25}: {val}")

    total_parts = sum(results['summary'].values())
    print(f"\n  {'TOTAL BOM ITEMS':25}: {total_parts}")

    return results


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# GRP PANEL TANK - COMPREHENSIVE BOM TEST")
    print("# Comparing Python calculators with Excel formulas")
    print("#"*70)

    # Run individual tests
    test_results = []

    test_results.append(test_10x5x3())
    test_results.append(test_5x5x3())
    test_results.append(test_5x5x2())
    test_results.append(test_10x8x3_partitioned())

    # Run full BOM comparison
    run_full_bom_test()

    # Final summary
    print("\n" + "#"*70)
    print("# FINAL SUMMARY")
    print("#"*70)

    passed = sum(1 for r in test_results if r[0])
    total = len(test_results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n*** ALL TESTS PASSED ***")
    else:
        print("\n*** SOME TESTS FAILED ***")
        for i, (passed, diffs) in enumerate(test_results):
            if not passed:
                print(f"\nTest {i+1} differences:")
                for d in diffs:
                    print(f"  - {d}")
