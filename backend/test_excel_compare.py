#!/usr/bin/env python3
"""
Compare Backend Calculations with Excel 5x5x2m Sample
"""
import sys
sys.path.insert(0, '.')

from app.schemas.tank import TankConfigRequest, TankDimensions, PanelOptions, SteelOptions, AccessoryOptions
from app.services.calculation_engine import calculate_tank_config

# Excel 5x5x2m expected values
EXCEL_5x5x2 = {
    # Panels
    "MF00M": 1,
    "RF00M": 24,
    "BF20M": 24,
    "DN20M": 1,
    "SL20S": 20,

    # Steel Skid
    "WBR-7575Z": 12,
    "WBR-0240Z": 4,
    "WFF-1990ALZ": 12,
    "WFF-0990ALZ": 6,
    "WFF-2000ASZ": 2,
    "WFF-1570ASZR": 2,
    "WFF-1570ASZL": 2,
    "WFF-0957AMZ": 8,
    "WFF-1063AMZ": 4,
    "WFF-0994AMZ": 8,
    "LNR-3.0T": 166,
    "WBR-5010Z": 10,

    # Bolts & Nuts
    "WBT-1440Z": 90,
    "WBT-1035Z": 128,
    "WBT-1050Z": 736,
    "WBT-1035SA4": 160,
    "WBT-1050SA4": 80,
    "WBT-1240Z": 40,
    "WBT-14120RD": 32,

    # External Reinforcing
    "WFB-0950ZP": 20,
    "WFB-1200Z": 16,
    "WCF-2000Z": 4,
    "WCP-1780Z": 16,

    # Internal Reinforcing
    "WCP-1760SA4": 16,

    # Internal Tie-Rod
    "TR-12M4880SA4": 8,
    "NUT(SA4)": 32,
    "BW(SA4)": 32,

    # ETC
    "WAV-0050A": 1,
    "WRS-2000F": 4,
    "WLD-2000FI": 1,
    "WLD-2000ZO": 1,
    "Silicon": 3,
    "WLV-2000SET(G)": 1,
    "WST-0050RO": 284,
    "WST-0120RO": 9,
}

def test_5x5x2():
    """Test 5m x 5m x 2m tank against Excel"""
    print("=" * 70)
    print("COMPARISON: Backend vs Excel 5x5x2m")
    print("=" * 70)

    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=5,
            length1=5,
            length2=0,
            length3=0,
            length4=0,
            height=2,
            quantity=1
        ),
        panel_options=PanelOptions(
            product_type="MNT",
            insulation="Non-Insulated",
            use_side_panel_1x1=False,
            use_partition_panel_1x1=False
        ),
        steel_options=SteelOptions(
            reinforcing_type="Internal",
            steel_skid="Default",
            internal_material="SS316",
            bolts_nuts="EXT:HDG/INT:SS316",
            tie_rod_material="SS316",
            tie_rod_spec="M12"
        ),
        accessory_options=AccessoryOptions(
            level_indicator="General",
            internal_ladder_material="GRP",
            internal_ladder_qty=-1,
            external_ladder_material="HDG",
            external_ladder_qty=-1
        ),
        fittings=[],
        exchange_rate=3.75
    )

    result = calculate_tank_config(request)

    # Build dict from BOM
    backend_items = {}
    for item in result.bom:
        if item.part_no in backend_items:
            backend_items[item.part_no] += item.quantity
        else:
            backend_items[item.part_no] = item.quantity

    print(f"\n{'Part No':<20} {'Backend':<10} {'Excel':<10} {'Match':<10}")
    print("-" * 50)

    all_parts = set(EXCEL_5x5x2.keys()) | set(backend_items.keys())

    matches = 0
    total = 0

    for part in sorted(all_parts):
        backend_qty = backend_items.get(part, 0)
        excel_qty = EXCEL_5x5x2.get(part, 0)

        if excel_qty == 0 and backend_qty == 0:
            continue

        total += 1

        if backend_qty == excel_qty:
            status = "✓"
            matches += 1
        elif abs(backend_qty - excel_qty) <= excel_qty * 0.1:  # Within 10%
            status = f"≈ ({excel_qty})"
        else:
            status = f"✗ (exp: {excel_qty})"

        print(f"{part:<20} {backend_qty:<10} {excel_qty:<10} {status}")

    print("-" * 50)
    print(f"\nMatches: {matches}/{total} ({100*matches/total:.1f}%)")

    return matches, total

def test_5x5x3():
    """Test 5m x 5m x 3m tank against Excel"""
    print("\n" + "=" * 70)
    print("COMPARISON: Backend vs Excel 5x5x3m")
    print("=" * 70)

    # Excel 5x5x3m expected values - COMPLETE list from PDF
    EXCEL_5x5x3 = {
        # Panels
        "MF00M": 1,
        "RF00M": 24,
        "BF30M": 24,
        "DN30M": 1,
        "SL20T": 20,
        "SF30L": 20,  # Side Low panel for 3m height

        # Tie Rods
        "TR-12M4880SA4": 24,
        "NUT(SA4)": 96,
        "BW(SA4)": 96,

        # Steel Skid (125 Channel for 3m height)
        "WBR-0120Z": 12,
        "WBR-21590Z": 4,
        "WFF-1990CLZ": 12,
        "WFF-0990CLZ": 6,
        "WFF-2000CSZ": 2,
        "WFF-1560CSZR": 2,
        "WFF-1560CSZL": 2,
        "WFF-0962AMZ": 8,
        "WFF-1053AMZ": 4,
        "WFF-0994AMZ": 8,
        "LNR-3.0T": 166,
        "WBR-5010Z": 10,

        # Bolts
        "WBT-1440Z": 122,
        "WBT-1035Z": 196,
        "WBT-1050Z": 1024,
        "WBT-1035SA4": 160,
        "WBT-1050SA4": 80,
        "WBT-1240Z": 40,
        "WBT-14120RD": 112,

        # External Reinforcing
        "WFB-0950ZP": 44,
        "WFB-0950Z": 36,
        "WFB-1200Z": 16,
        "WCF-1000Z": 4,
        "WCF-2000Z": 4,
        "WCP-1780Z": 24,
        "WCP-1616Z": 16,

        # Internal Reinforcing
        "WCP-17160SA4": 16,
        "WCP-1760SA4": 16,
        "WBR-9090SA4": 4,

        # ETC
        "WAV-0050A": 1,
        "WRS-3000F": 4,
        "WLD-3000FI": 1,
        "WLD-3000ZO": 1,
        "Silicon": 3,
        "WLV-3000SET(G)": 1,
        "WST-0050RO": 386,
        "WST-0120RO": 13,
    }

    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=5,
            length1=5,
            length2=0,
            length3=0,
            length4=0,
            height=3,
            quantity=1
        ),
        panel_options=PanelOptions(
            product_type="MNT",
            insulation="Non-Insulated",
            use_side_panel_1x1=False,
            use_partition_panel_1x1=False
        ),
        steel_options=SteelOptions(
            reinforcing_type="Internal",
            steel_skid="Default",
            internal_material="SS316",
            bolts_nuts="EXT:HDG/INT:SS316",
            tie_rod_material="SS316",
            tie_rod_spec="M12"
        ),
        accessory_options=AccessoryOptions(
            level_indicator="General",
            internal_ladder_material="GRP",
            internal_ladder_qty=-1,
            external_ladder_material="HDG",
            external_ladder_qty=-1
        ),
        fittings=[],
        exchange_rate=3.75
    )

    result = calculate_tank_config(request)

    backend_items = {}
    for item in result.bom:
        if item.part_no in backend_items:
            backend_items[item.part_no] += item.quantity
        else:
            backend_items[item.part_no] = item.quantity

    print(f"\n{'Part No':<20} {'Backend':<10} {'Excel':<10} {'Match':<10}")
    print("-" * 50)

    all_parts = set(EXCEL_5x5x3.keys()) | set(backend_items.keys())
    matches = 0
    total = 0

    for part in sorted(all_parts):
        backend_qty = backend_items.get(part, 0)
        excel_qty = EXCEL_5x5x3.get(part, 0)

        if excel_qty == 0 and backend_qty == 0:
            continue

        total += 1

        if backend_qty == excel_qty:
            status = "✓"
            matches += 1
        elif excel_qty > 0 and abs(backend_qty - excel_qty) <= excel_qty * 0.15:
            status = f"≈ ({excel_qty})"
        else:
            status = f"✗ (exp: {excel_qty})"

        print(f"{part:<20} {backend_qty:<10} {excel_qty:<10} {status}")

    print("-" * 50)
    print(f"\nMatches: {matches}/{total} ({100*matches/total:.1f}%)")
    return matches, total


def test_5x5x4():
    """Test 5m x 5m x 4m tank against Excel"""
    print("\n" + "=" * 70)
    print("COMPARISON: Backend vs Excel 5x5x4m")
    print("=" * 70)

    # Excel 5x5x4m expected values from PDF
    EXCEL_5x5x4 = {
        # Panels
        "MF00M": 1,
        "RF00M": 24,
        "BF40M": 24,
        "DN40M": 1,
        "SL20T": 20,
        "SF30M": 20,  # Side Mid for 4m
        "SF40L": 20,  # Side Low for 4m

        # Tie Rods
        "TR-12M4880SA4": 40,
        "NUT(SA4)": 160,
        "BW(SA4)": 160,

        # Steel Skid (125 Channel)
        "WBR-0120Z": 12,
        "WBR-21590Z": 4,
        "WFF-1990CLZ": 12,
        "WFF-0990CLZ": 6,
        "WFF-2000CSZ": 2,
        "WFF-1560CSZR": 2,
        "WFF-1560CSZL": 2,
        "WFF-0962AMZ": 8,
        "WFF-1053AMZ": 4,
        "WFF-0994AMZ": 8,
        "LNR-3.0T": 166,
        "WBR-5010Z": 20,

        # Bolts
        "WBT-1440Z": 132,
        "WBT-1035Z": 264,
        "WBT-1050Z": 1312,
        "WBT-1035SA4": 160,
        "WBT-1050SA4": 80,
        "WBT-1240Z": 40,
        "WBT-14120RD": 256,

        # External Reinforcing
        "WFB-0950ZL": 16,
        "WFB-0950ZP": 72,
        "WFB-0950Z": 72,
        "WFB-1200Z": 16,
        "WCF-2000Z": 8,
        "WCP-1780Z": 48,
        "WCP-1616Z": 32,

        # Internal Reinforcing
        "WCP-17160SA4": 32,
        "WCP-1760SA4": 16,
        "WBR-9090SA4": 24,

        # ETC
        "WAV-0100A": 1,
        "WRS-4000F": 4,
        "WLD-4000FI": 1,
        "WLD-4000ZO": 1,
        "Silicon": 3,
        "WLV-4000SET(G)": 1,
        "WST-0050RO": 495,
        "WST-0120RO": 17,
    }

    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=5,
            length1=5,
            length2=0,
            length3=0,
            length4=0,
            height=4,
            quantity=1
        ),
        panel_options=PanelOptions(
            product_type="MNT",
            insulation="Non-Insulated",
            use_side_panel_1x1=False,
            use_partition_panel_1x1=False
        ),
        steel_options=SteelOptions(
            reinforcing_type="Internal",
            steel_skid="Default",
            internal_material="SS316",
            bolts_nuts="EXT:HDG/INT:SS316",
            tie_rod_material="SS316",
            tie_rod_spec="M12"
        ),
        accessory_options=AccessoryOptions(
            level_indicator="General",
            internal_ladder_material="GRP",
            internal_ladder_qty=-1,
            external_ladder_material="HDG",
            external_ladder_qty=-1
        ),
        fittings=[],
        exchange_rate=3.75
    )

    result = calculate_tank_config(request)

    backend_items = {}
    for item in result.bom:
        if item.part_no in backend_items:
            backend_items[item.part_no] += item.quantity
        else:
            backend_items[item.part_no] = item.quantity

    print(f"\n{'Part No':<20} {'Backend':<10} {'Excel':<10} {'Match':<10}")
    print("-" * 50)

    all_parts = set(EXCEL_5x5x4.keys()) | set(backend_items.keys())
    matches = 0
    total = 0

    for part in sorted(all_parts):
        backend_qty = backend_items.get(part, 0)
        excel_qty = EXCEL_5x5x4.get(part, 0)

        if excel_qty == 0 and backend_qty == 0:
            continue

        total += 1

        if backend_qty == excel_qty:
            status = "✓"
            matches += 1
        elif excel_qty > 0 and abs(backend_qty - excel_qty) <= excel_qty * 0.15:
            status = f"≈ ({excel_qty})"
        else:
            status = f"✗ (exp: {excel_qty})"

        print(f"{part:<20} {backend_qty:<10} {excel_qty:<10} {status}")

    print("-" * 50)
    print(f"\nMatches: {matches}/{total} ({100*matches/total:.1f}%)")
    return matches, total


def test_10x8x3():
    """Test 10m x 8m x 3m tank (with 2 partitions) against Excel"""
    print("\n" + "=" * 70)
    print("COMPARISON: Backend vs Excel 10x8x3m (with partitions)")
    print("=" * 70)

    # Excel 10x8x3m expected values - KEY parts only
    EXCEL_10x8x3 = {
        # Panels
        "MF00M": 3,
        "RF00M": 77,
        "BF30M": 57,
        "BF30P": 20,
        "DN30M": 3,
        "SL20T": 32,
        "SL20TL": 2,
        "SL20TR": 2,
        "SF30L": 32,
        "SF30LL": 2,
        "SF30LR": 2,
        "PL20TCB": 20,
        "PF30M": 20,

        # Tie Rods (multiple lengths due to width variations)
        "TR-12M1880SA4": 23,
        "TR-12M3880SA4": 27,
        "TR-12M4000SA4": 73,
        "NUT(SA4)": 200,
        "BW(SA4)": 200,
        "TC-12M60SA4": 73,

        # Steel Skid
        "WBR-0120Z": 22,
        "WBR-21590Z": 8,
        "WFF-1990CLZ": 44,
        "WFF-2060CSZR": 2,
        "WFF-2060CSZL": 2,
        "WFF-2000CSZ": 6,
        "WFF-0962AMZ": 14,
        "WFF-1053AMZ": 7,
        "WFF-0994AMZ": 49,
        "LNR-3.0T": 456,
        "WBR-5010Z": 18,

        # Bolts
        "WBT-1440Z": 292,
        "WBT-1035Z": 196,
        "WBT-1050Z": 2480,
        "WBT-1035SA4": 488,
        "WBT-1050SA4": 1136,
        "WBT-1240Z": 72,
        "WBT-14120RD": 192,
        "WBT-14120RSA4": 216,
        "WBT-1058RSA4": 256,

        # External Reinforcing
        "WFB-0950ZP": 104,
        "WFB-0950Z": 68,
        "WFB-1200Z": 32,
        "WCF-1000Z": 4,
        "WCF-2000Z": 4,
        "WFB-0880ZP": 4,
        "WCP-1780Z": 40,
        "WCP-1616Z": 28,

        # Internal Reinforcing (SS316)
        "WFB-1200SA4": 18,
        "WFB-0880SA4": 18,
        "WFB-0880PSA4": 22,
        "WFB-0950SA4": 40,
        "WCP-1616SA4": 18,
        "WCP-1780SA4": 18,
        "WCP-17160SA4": 64,
        "WCP-1760SA4": 68,
        "WBR-9090SA4": 4,

        # ETC
        "WAV-0100A": 3,
        "WRS-3000F": 16,
        "WLD-3000FI": 3,
        "WLD-3000ZO": 1,
        "Silicon": 8,
        "WLV-3000SET(G)": 3,
        "WST-0050RO": 1020,
        "WST-0120RO": 13,
    }

    # 10m x 8m with 2 partitions = 10m x (4m + 2m + 2m) structure = 3 compartments
    # N_PA = 2 (2 partitions)
    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=10,
            length1=4,
            length2=2,
            length3=2,
            length4=0,
            height=3,
            quantity=1
        ),
        panel_options=PanelOptions(
            product_type="MNT",
            insulation="Non-Insulated",
            use_side_panel_1x1=False,
            use_partition_panel_1x1=False
        ),
        steel_options=SteelOptions(
            reinforcing_type="Internal",
            steel_skid="Default",
            internal_material="SS316",
            bolts_nuts="EXT:HDG/INT:SS316",
            tie_rod_material="SS316",
            tie_rod_spec="M12"
        ),
        accessory_options=AccessoryOptions(
            level_indicator="General",
            internal_ladder_material="GRP",
            internal_ladder_qty=-1,
            external_ladder_material="HDG",
            external_ladder_qty=-1
        ),
        fittings=[],
        exchange_rate=3.75
    )

    result = calculate_tank_config(request)

    backend_items = {}
    for item in result.bom:
        if item.part_no in backend_items:
            backend_items[item.part_no] += item.quantity
        else:
            backend_items[item.part_no] = item.quantity

    print(f"\n{'Part No':<20} {'Backend':<10} {'Excel':<10} {'Match':<10}")
    print("-" * 50)

    all_parts = set(EXCEL_10x8x3.keys()) | set(backend_items.keys())
    matches = 0
    total = 0

    for part in sorted(all_parts):
        backend_qty = backend_items.get(part, 0)
        excel_qty = EXCEL_10x8x3.get(part, 0)

        if excel_qty == 0 and backend_qty == 0:
            continue

        total += 1

        if backend_qty == excel_qty:
            status = "✓"
            matches += 1
        elif excel_qty > 0 and abs(backend_qty - excel_qty) <= excel_qty * 0.15:
            status = f"≈ ({excel_qty})"
        else:
            status = f"✗ (exp: {excel_qty})"

        print(f"{part:<20} {backend_qty:<10} {excel_qty:<10} {status}")

    print("-" * 50)
    print(f"\nMatches: {matches}/{total} ({100*matches/total:.1f}%)")
    return matches, total


def test_10x15x4():
    """Test 10m x 15m x 4m tank (with 2 partitions) against Excel"""
    print("\n" + "=" * 70)
    print("COMPARISON: Backend vs Excel 10x15x4m (with partitions)")
    print("=" * 70)

    # Excel 10x15x4m expected values from PDF
    EXCEL_10x15x4 = {
        # Panels
        "MF00M": 3,
        "RF00M": 147,
        "BF40M": 127,
        "BF40P": 20,
        "DN40M": 3,
        "SL20T": 46,
        "SL20TL": 2,
        "SL20TR": 2,
        "SF30M": 46,
        "SF30ML": 2,
        "SF30MR": 2,
        "SF40L": 46,
        "SF40LL": 2,
        "SF40LR": 2,
        "PL20TCB": 20,
        "SN30M": 20,  # Side Nozzle Mid - new panel type
        "PF40M": 20,

        # Steel Skid
        "WBR-0120Z": 22,
        "WBR-21590Z": 8,
        "WFF-1990CLZ": 77,
        "WFF-0990CLZ": 11,
        "WFF-2060CSZR": 2,
        "WFF-2060CSZL": 2,
        "WFF-2000CSZ": 6,
        "WFF-0962AMZ": 28,
        "WFF-1053AMZ": 14,
        "WFF-0994AMZ": 98,
        "LNR-3.0T": 810,
        "WBR-5010Z": 50,

        # Internal Tie-Rod
        "TR-12M1880SA4": 74,
        "TR-12M2880SA4": 45,
        "TR-12M4000SA4": 283,
        "NUT(SA4)": 476,
        "BW(SA4)": 476,
        "TC-12M60SA4": 283,

        # Bolts & Nuts
        "WBT-1440Z": 478,
        "WBT-1035Z": 264,
        "WBT-1050Z": 4872,
        "WBT-1035SA4": 1020,
        "WBT-1050SA4": 1656,
        "WBT-1240Z": 100,
        "WBT-14120RD": 636,
        "WBT-14120RSA4": 360,
        "WBT-1058RSA4": 288,

        # External Reinforcing
        "WFB-0950ZL": 46,
        "WFB-0950ZP": 194,
        "WFB-0950Z": 192,
        "WFB-1200Z": 46,
        "WCF-2000Z": 8,
        "WFB-0880ZP": 4,
        "WCP-1780Z": 108,
        "WCP-1616Z": 84,

        # Internal Reinforcing
        "WFB-1200SA4": 18,
        "WFB-0880SA4": 18,
        "WFB-0880PSA4": 22,
        "WFB-0950SA4": 98,
        "WFB-0950PSA4": 42,
        "WCP-1616SA4": 36,
        "WCP-1780SA4": 18,
        "WCP-17160SA4": 156,
        "WCP-1760SA4": 86,
        "WBR-9090SA4": 50,

        # ETC
        "WAV-0100A": 5,
        "WRS-4000F": 32,
        "WLD-4000FI": 3,
        "WLD-4000ZO": 1,
        "Silicon": 15,
        "WLV-4000SET(G)": 3,
        "WST-0050RO": 1929,
        "WST-0120RO": 17,
    }

    # 10m x 15m with 2 partitions = 10m x (5m + 5m + 5m) structure = 3 compartments
    # N_PA = 2 (2 partitions)
    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=10,
            length1=5,
            length2=5,
            length3=5,
            length4=0,
            height=4,
            quantity=1
        ),
        panel_options=PanelOptions(
            product_type="MNT",
            insulation="Non-Insulated",
            use_side_panel_1x1=False,
            use_partition_panel_1x1=False
        ),
        steel_options=SteelOptions(
            reinforcing_type="Internal",
            steel_skid="Default",
            internal_material="SS316",
            bolts_nuts="EXT:HDG/INT:SS316",
            tie_rod_material="SS316",
            tie_rod_spec="M12"
        ),
        accessory_options=AccessoryOptions(
            level_indicator="General",
            internal_ladder_material="GRP",
            internal_ladder_qty=-1,
            external_ladder_material="HDG",
            external_ladder_qty=-1
        ),
        fittings=[],
        exchange_rate=3.75
    )

    result = calculate_tank_config(request)

    backend_items = {}
    for item in result.bom:
        if item.part_no in backend_items:
            backend_items[item.part_no] += item.quantity
        else:
            backend_items[item.part_no] = item.quantity

    print(f"\n{'Part No':<20} {'Backend':<10} {'Excel':<10} {'Match':<10}")
    print("-" * 50)

    all_parts = set(EXCEL_10x15x4.keys()) | set(backend_items.keys())
    matches = 0
    total = 0

    for part in sorted(all_parts):
        backend_qty = backend_items.get(part, 0)
        excel_qty = EXCEL_10x15x4.get(part, 0)

        if excel_qty == 0 and backend_qty == 0:
            continue

        total += 1

        if backend_qty == excel_qty:
            status = "✓"
            matches += 1
        elif excel_qty > 0 and abs(backend_qty - excel_qty) <= excel_qty * 0.15:
            status = f"≈ ({excel_qty})"
        else:
            status = f"✗ (exp: {excel_qty})"

        print(f"{part:<20} {backend_qty:<10} {excel_qty:<10} {status}")

    print("-" * 50)
    print(f"\nMatches: {matches}/{total} ({100*matches/total:.1f}%)")
    return matches, total


if __name__ == "__main__":
    m1, t1 = test_5x5x2()
    m2, t2 = test_5x5x3()
    m3, t3 = test_5x5x4()
    m4, t4 = test_10x8x3()
    m5, t5 = test_10x15x4()

    total_matches = m1 + m2 + m3 + m4 + m5
    total_items = t1 + t2 + t3 + t4 + t5

    print("\n" + "=" * 70)
    print(f"OVERALL: {total_matches}/{total_items} ({100*total_matches/total_items:.1f}%)")
    print("=" * 70)

    if total_matches == total_items:
        print("\n✅ ALL ITEMS MATCH EXCEL!")
    else:
        print(f"\n⚠️  {total_items - total_matches} items need adjustment")
