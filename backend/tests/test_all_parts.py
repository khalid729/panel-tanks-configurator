"""
Complete Parts Test - Test ALL parts from ALL calculators
Compare with Excel values for 10x5x3m tank
"""
import sys
sys.path.insert(0, '/home/khalid/dev/panel_tank_config/backend')

from app.services.panel_calculator import PanelCalculator
from app.services.steel_skid_calculator import SteelSkidCalculator
from app.services.tie_rod_calculator import TieRodCalculator
from app.services.bolts_calculator import BoltsCalculator
from app.services.reinforcing_calculator import ReinforcingCalculator
from app.services.etc_calculator import ETCCalculator


def get_all_parts(width, length1, length2, length3, length4, height,
                  skid_type=1, tie_rod_material=4, bolt_option=1):
    """Get all parts from all calculators"""
    results = {}

    # Panel Calculator
    panel_calc = PanelCalculator(width, length1, length2, length3, length4, height)
    for p in panel_calc.calculate_all_panels():
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']

    # Steel Skid Calculator
    skid_calc = SteelSkidCalculator(width, length1, length2, length3, length4, height, skid_type)
    for p in skid_calc.calculate_all_parts():
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']

    # Tie Rod Calculator
    tie_calc = TieRodCalculator(width, length1, length2, length3, length4, height, tie_rod_material)
    for p in tie_calc.calculate_all_parts():
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']
    for p in tie_calc.get_tie_rod_accessories():
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']

    # Reinforcing Calculator
    reinf_calc = ReinforcingCalculator(width, length1, length2, length3, length4, height)
    reinf_parts = reinf_calc.calculate_all_parts()
    for p in reinf_parts:
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']

    # Extract values for bolts
    ext_l22 = ext_l23 = ext_l24 = int_p18 = int_p19 = 0
    for p in reinf_parts:
        pn = p.get('part_no', '')
        qty = p.get('quantity', 0)
        if 'WCP-1780Z' in pn: ext_l22 = qty
        elif 'WCP-1616Z' in pn: ext_l23 = qty
        elif 'WCP-17120Z' in pn: ext_l24 = qty
        elif 'WCP-1616SA' in pn: int_p18 = qty
        elif 'WCP-1780SA' in pn: int_p19 = qty

    # Bolts Calculator
    bolts_calc = BoltsCalculator(
        width, length1, length2, length3, length4, height,
        bolt_option=bolt_option,
        ext_reinforcing_l22=ext_l22, ext_reinforcing_l23=ext_l23, ext_reinforcing_l24=ext_l24,
        int_reinforcing_p18=int_p18, int_reinforcing_p19=int_p19
    )
    for p in bolts_calc.calculate_all_parts():
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']

    # ETC Calculator
    capacity = width * length1 * height
    etc_calc = ETCCalculator(
        width, length1, length2, length3, length4, height,
        nominal_capacity=capacity,
        level_indicator_type=1,
        internal_ladder_material=2,
        external_ladder_material=1
    )
    for p in etc_calc.calculate_all_parts():
        if p.get('quantity', 0) > 0:
            results[p['part_no']] = p['quantity']

    return results


def compare_results(actual, expected, tank_name):
    """Compare actual vs expected and print results"""
    print(f"\n{'='*70}")
    print(f"TESTING: {tank_name}")
    print(f"{'='*70}")

    all_pass = True
    matched = 0
    mismatched = 0
    missing_in_actual = 0
    extra_in_actual = 0

    # Check expected values
    print(f"\n{'Part No':<25} {'Actual':>8} {'Expected':>8} {'Status':>10}")
    print("-" * 55)

    for part_no, exp_qty in sorted(expected.items()):
        act_qty = actual.get(part_no, 0)
        if act_qty == exp_qty:
            status = "OK"
            matched += 1
        elif act_qty == 0:
            status = "MISSING"
            missing_in_actual += 1
            all_pass = False
        else:
            status = "DIFF"
            mismatched += 1
            all_pass = False
        print(f"{part_no:<25} {act_qty:>8} {exp_qty:>8} {status:>10}")

    # Check for extra parts in actual (not in expected)
    print(f"\n--- Parts in calculator but not in expected ---")
    for part_no, act_qty in sorted(actual.items()):
        if part_no not in expected:
            print(f"{part_no:<25} {act_qty:>8} {'N/A':>8} {'EXTRA':>10}")
            extra_in_actual += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY: {tank_name}")
    print(f"  Matched:    {matched}")
    print(f"  Mismatched: {mismatched}")
    print(f"  Missing:    {missing_in_actual}")
    print(f"  Extra:      {extra_in_actual}")
    print(f"  RESULT:     {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*70}")

    return all_pass, matched, mismatched, missing_in_actual, extra_in_actual


def test_10x5x3m_complete():
    """Test 10x5x3m tank with ALL expected values from Excel"""

    # Expected values from Excel for 10x5x3m tank
    # These are based on the formulas we extracted and verified
    expected = {
        # PANELS (from Panel sheet)
        'MF00M': 1,           # Manhole
        'RF00M': 49,          # Roof Full (W_C × L_O_C - MF - RQ)
        'BF30M': 49,          # Bottom Full
        'DN30M': 1,           # Drain
        'SL20T': 30,          # Side Length (H_C × L_O_C × 2)
        'SF30L': 30,          # Side Full Length

        # STEEL SKID (from Steel_Skid sheet)
        'WBR-0120Z': 22,      # Bracket 120
        'WFF-1990CLZ': 22,    # Main-L 2m
        'WFF-0990CLZ': 11,    # Main-L 1m
        'WFF-1560CSZR': 2,    # Width frame R
        'WFF-1560CSZL': 2,    # Width frame L
        'WFF-2000CSZ': 6,     # Center channel
        'WFF-0994AMZ': 28,    # Sub frame A
        'WFF-0962AMZ': 8,     # Sub frame B
        'WFF-1053AMZ': 4,     # Sub frame C
        'WBR-21590Z': 38,     # Cross beam
        'LNR-3.0T': 304,      # Liner
        'WBR-5010Z': 15,      # Anchor bracket

        # TIE RODS (from Internal_Tie_rod1 sheet)
        'TR-12M1880SA4': 27,  # Width assemblies
        'TR-12M4000SA4': 54,  # 4000mm rods
        'TR-12M4880SA4': 12,  # Length assemblies
        'TC-12M0060SA4': 54,  # Connectors
        'NUT(SA4)': 156,      # Nuts (39 assemblies × 4)
        'BW(SA4)': 156,       # Washers

        # BOLTS (from BoltnNuts sheet)
        'WBT-1035Z': 196,     # M10x35 External
        'WBT-1035SA4': 340,   # M10x35 Internal
        'WBT-1050Z': 1784,    # M10x50 External
        'WBT-1050SA4': 120,   # M10x50 Internal
        'WBT-1240Z': 60,      # M12x40
        'WBT-1440Z': 176,     # M14x40
        'WBT-14120RD': 172,   # M14x120 Rubber

        # EXTERNAL REINFORCING (from External_Reinforcing sheet)
        'WFB-0950ZP': 64,     # Flat bar perforated
        'WFB-0950Z': 56,      # Flat bar
        'WFB-1200Z': 26,      # Angle 1200
        'WCF-1000Z': 4,       # Corner frame 1000
        'WCF-2000Z': 4,       # Corner frame 2000
        'WCP-1780Z': 34,      # Cross plate 2-hole
        'WCP-1616Z': 26,      # Cross plate 4-hole

        # INTERNAL REINFORCING (from Internal_Reinforcing sheet)
        'WCP-17160SA4': 26,   # 2-tierod bracket
        'WCP-1760SA4': 26,    # 1-tierod bracket
        'WBR-9090SA4': 4,     # Corner bracket

        # ETC (from ETC sheet)
        'WAV-0100A': 2,       # Air vent 100A
        'WRS-3000F': 9,       # Roof supporter
        'WLD-3000FI': 1,      # Internal ladder
        'WLD-3000ZO': 1,      # External ladder
        'Silicon': 5,         # Silicon
        'WLV-3000SET(G)': 1,  # Level indicator
        'WST-0050RO': 659,    # Sealing tape 50mm
        'WST-0120RO': 13,     # Sealing tape 120mm
    }

    actual = get_all_parts(10, 5, 0, 0, 0, 3)
    return compare_results(actual, expected, "10x5x3m Tank - Complete")


def test_5x5x3m_complete():
    """Test 5x5x3m tank - ALL parts"""
    expected = {
        # PANELS
        'MF00M': 1,
        'RF00M': 24,
        'BF30M': 24,
        'DN30M': 1,
        'SL20T': 20,
        'SF30L': 20,

        # STEEL SKID
        'WBR-0120Z': 12,
        'WFF-1990CLZ': 12,
        'WFF-0990CLZ': 6,
        'WFF-2000CSZ': 2,
        'WFF-0994AMZ': 8,
        'WFF-0962AMZ': 8,
        'WFF-1053AMZ': 4,
        'WBR-21590Z': 18,
        'LNR-3.0T': 166,
        'WBR-5010Z': 10,

        # TIE RODS
        'TR-12M4880SA4': 24,
        'NUT(SA4)': 96,
        'BW(SA4)': 96,

        # BOLTS
        'WBT-1035Z': 196,
        'WBT-1035SA4': 160,
        'WBT-1050Z': 1024,
        'WBT-1050SA4': 80,
        'WBT-1240Z': 40,
        'WBT-1440Z': 96,
        'WBT-14120RD': 112,

        # EXTERNAL REINFORCING
        'WFB-0950ZP': 44,
        'WFB-0950Z': 36,
        'WFB-1200Z': 16,
        'WCF-1000Z': 4,
        'WCF-2000Z': 4,
        'WCP-1780Z': 24,
        'WCP-1616Z': 16,

        # INTERNAL REINFORCING
        'WCP-17160SA4': 16,
        'WCP-1760SA4': 16,
        'WBR-9090SA4': 4,

        # ETC
        'WAV-0050A': 1,
        'WRS-3000F': 4,
        'WLD-3000FI': 1,
        'WLD-3000ZO': 1,
        'Silicon': 3,
        'WLV-3000SET(G)': 1,
        'WST-0050RO': 336,
        'WST-0120RO': 13,
    }

    actual = get_all_parts(5, 5, 0, 0, 0, 3)
    return compare_results(actual, expected, "5x5x3m Tank - Complete")


def test_10x8x3m_partitioned():
    """Test 10x(4+4)x3m partitioned tank - ALL parts"""
    expected = {
        # PANELS (partitioned)
        'MF00M': 2,           # 2 manholes (one per compartment)
        'RF00M': 78,          # Roof panels
        'BF30M': 68,          # Bottom panels
        'BF30P': 10,          # Partition bottom panels
        'DN30M': 2,           # 2 drains
        'PF30M': 10,          # Partition panels
        'PL20TCB': 10,        # Partition panels corner
        'SL20T': 34,          # Side length
        'SL20TL': 1,          # Side corner L
        'SL20TR': 1,          # Side corner R
        'SF30L': 34,          # Side full length
        'SF30LL': 1,          # Side corner LL
        'SF30LR': 1,          # Side corner LR

        # STEEL SKID
        'WBR-0120Z': 22,
        'WFF-1990CLZ': 44,
        'WFF-2000CSZ': 6,
        'WFF-1560CSZR': 2,
        'WFF-1560CSZL': 2,
        'WFF-0994AMZ': 49,
        'WFF-0962AMZ': 14,
        'WFF-1053AMZ': 7,
        'WBR-21590Z': 68,
        'LNR-3.0T': 456,
        'WBR-5010Z': 18,

        # TIE RODS
        'TR-12M1880SA4': 28,
        'TR-12M3880SA4': 18,
        'TR-12M4000SA4': 56,
        'TC-12M0060SA4': 56,
        'NUT(SA4)': 184,
        'BW(SA4)': 184,

        # BOLTS
        'WBT-1035Z': 196,
        'WBT-1035SA4': 528,
        'WBT-1050Z': 2480,
        'WBT-1050SA4': 560,
        'WBT-1058RSA4': 128,   # Partition rubber bolts
        'WBT-1240Z': 72,
        'WBT-1440Z': 242,
        'WBT-14120RD': 200,
        'WBT-14120RSA4': 54,   # Internal reinforcing bolts

        # EXTERNAL REINFORCING
        'WFB-0950ZP': 86,
        'WFB-0950Z': 68,
        'WFB-0880ZP': 2,
        'WFB-1200Z': 32,
        'WCF-1000Z': 4,
        'WCF-2000Z': 4,
        'WCP-1780Z': 40,
        'WCP-1616Z': 30,

        # INTERNAL REINFORCING (with partition)
        'WFB-1200SA4': 9,     # Partition angle
        'WFB-0880SA4': 9,     # Partition flat bar
        'WFB-0880PSA4': 9,    # Partition flat bar P
        'WCP-1616SA4': 9,     # Partition cross plate 4-hole
        'WCP-1780SA4': 9,     # Partition cross plate 2-hole
        'WCP-17160SA4': 48,
        'WCP-1760SA4': 50,
        'WBR-9090SA4': 4,

        # ETC (partitioned)
        'WAV-0100A': 4,
        'WRS-3000F': 14,
        'WLD-3000FI': 2,
        'WLD-3000ZO': 1,
        'Silicon': 8,
        'WLV-3000SET(G)': 2,
        'WST-0050RO': 1282,
        'WST-0120RO': 13,
    }

    actual = get_all_parts(10, 4, 4, 0, 0, 3)
    return compare_results(actual, expected, "10x8x3m Partitioned Tank - Complete")


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# COMPLETE PARTS TEST - ALL CALCULATORS")
    print("#"*70)

    results = []

    # Run all tests
    results.append(test_10x5x3m_complete())
    results.append(test_5x5x3m_complete())
    results.append(test_10x8x3m_partitioned())

    # Final summary
    print("\n" + "#"*70)
    print("# FINAL SUMMARY")
    print("#"*70)

    total_matched = sum(r[1] for r in results)
    total_mismatched = sum(r[2] for r in results)
    total_missing = sum(r[3] for r in results)
    total_extra = sum(r[4] for r in results)

    print(f"\nTotal Matched:    {total_matched}")
    print(f"Total Mismatched: {total_mismatched}")
    print(f"Total Missing:    {total_missing}")
    print(f"Total Extra:      {total_extra}")

    all_pass = all(r[0] for r in results)
    print(f"\nOVERALL RESULT: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
