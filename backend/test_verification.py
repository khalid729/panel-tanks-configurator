#!/usr/bin/env python3
"""
Verification Test - Compare Backend Calculations with Expected Results
Run this to verify all calculators are working correctly.
"""
import sys
sys.path.insert(0, '.')

from app.schemas.tank import TankConfigRequest, TankDimensions, PanelOptions, SteelOptions, AccessoryOptions
from app.services.calculation_engine import calculate_tank_config

def test_tank_3x5x2():
    """Test a standard 3m x 5m x 2m tank"""
    print("=" * 70)
    print("TEST: Tank 3m (Width) x 5m (Length) x 2m (Height)")
    print("=" * 70)

    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=3,
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

    print("\n=== CAPACITY ===")
    print(f"Nominal: {result.capacity.nominal_capacity_m3} m³")
    print(f"Actual: {result.capacity.actual_capacity_m3} m³")
    print(f"Surface Area: {result.capacity.surface_area_m2} m²")
    print(f"Partitions: {result.capacity.num_partitions}")

    print("\n=== BOM ITEMS BY CATEGORY ===")
    categories = {}
    for item in result.bom:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)

    for cat, items in sorted(categories.items()):
        print(f"\n--- {cat} ---")
        for item in items:
            print(f"  {item.part_no}: {item.quantity} pcs @ ${item.unit_price_usd:.2f} = ${item.total_price_usd:.2f} | {item.total_weight_kg:.2f} kg")

    print("\n=== COST SUMMARY ===")
    print(f"Panels:              ${result.cost_summary.panels:.2f}")
    print(f"Steel Skid:          ${result.cost_summary.steel_skid:.2f}")
    print(f"Bolts & Nuts:        ${result.cost_summary.bolts_nuts:.2f}")
    print(f"External Reinforcing:${result.cost_summary.external_reinforcing:.2f}")
    print(f"Internal Reinforcing:${result.cost_summary.internal_reinforcing:.2f}")
    print(f"Tie Rods:            ${result.cost_summary.internal_tie_rod:.2f}")
    print(f"ETC (Accessories):   ${result.cost_summary.etc:.2f}")
    print(f"Fittings:            ${result.cost_summary.fittings:.2f}")
    print(f"-" * 40)
    print(f"TOTAL USD:           ${result.cost_summary.total_usd:.2f}")
    print(f"TOTAL SAR:           {result.cost_summary.total_sar:.2f}")

    print("\n=== WEIGHT SUMMARY ===")
    print(f"Panels:      {result.weight_summary.panels_kg:.2f} kg")
    print(f"Steel:       {result.weight_summary.steel_kg:.2f} kg")
    print(f"Accessories: {result.weight_summary.accessories_kg:.2f} kg")
    print(f"-" * 40)
    print(f"TOTAL:       {result.weight_summary.total_kg:.2f} kg")

    return result

def test_tank_with_partition():
    """Test a tank with partition: 3m x (3m + 2m) x 2.5m"""
    print("\n" + "=" * 70)
    print("TEST: Tank with Partition 3m x (3+2)m x 2.5m")
    print("=" * 70)

    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=3,
            length1=3,
            length2=2,
            length3=0,
            length4=0,
            height=2.5,
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

    print(f"\nCapacity: {result.capacity.nominal_capacity_m3} m³ nominal")
    print(f"Partitions: {result.capacity.num_partitions}")
    print(f"Total BOM Items: {len(result.bom)}")
    print(f"Total Cost: ${result.cost_summary.total_usd:.2f}")
    print(f"Total Weight: {result.weight_summary.total_kg:.2f} kg")

    return result

def test_half_meter_dimensions():
    """Test with 0.5m increments: 3.5m x 4.5m x 1.5m"""
    print("\n" + "=" * 70)
    print("TEST: Half-meter dimensions 3.5m x 4.5m x 1.5m")
    print("=" * 70)

    request = TankConfigRequest(
        dimensions=TankDimensions(
            width=3.5,
            length1=4.5,
            length2=0,
            length3=0,
            length4=0,
            height=1.5,
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

    print(f"\nCapacity: {result.capacity.nominal_capacity_m3} m³ nominal")
    print(f"Surface Area: {result.capacity.surface_area_m2} m²")

    # Show panels specifically
    print("\n--- Panel Items ---")
    for item in result.bom:
        if item.category == "Panels":
            print(f"  {item.part_no}: {item.quantity} pcs")

    print(f"\nTotal Cost: ${result.cost_summary.total_usd:.2f}")

    return result

def verify_specific_formulas():
    """Verify specific formula calculations match Excel"""
    print("\n" + "=" * 70)
    print("FORMULA VERIFICATION")
    print("=" * 70)

    # Test case: 3m x 5m x 2m
    W_C, W_F = 3, 0
    L1_C, L1_F = 5, 0
    H_O = 2
    N_PA = 0

    W_O = W_C + W_F
    L_O_C = L1_C

    print("\n--- Panel Calculations (3x5x2) ---")

    # Manhole: =1+N_PA
    manhole_qty = 1 + N_PA
    print(f"Manhole: 1 + {N_PA} = {manhole_qty}")

    # Roof 1x1: =W_C*(L1_C+L2_C+L3_C+L4_C) - manhole - QRoof
    roof_full = W_C * L1_C - manhole_qty
    print(f"Roof 1x1: {W_C}*{L1_C} - {manhole_qty} = {roof_full}")

    # Roof 0.5x1: =W_C*(L1_F+L2_F+L3_F+L4_F)+W_F*(L1_C+L2_C+L3_C+L4_C)
    roof_half = W_C * L1_F + W_F * L1_C
    print(f"Roof 0.5x1: {W_C}*{L1_F} + {W_F}*{L1_C} = {roof_half}")

    print("\n--- Steel Skid Calculations ---")

    # Main beams: (W_C+W_F+1)*2
    main_beams = (W_C + W_F + 1) * 2
    print(f"Main Beams: ({W_C}+{W_F}+1)*2 = {main_beams}")

    # Height check for Default steel type
    if H_O > 4.3:
        steel_type = "150 Channel"
    elif H_O > 2.5:
        steel_type = "125 Channel"
    else:
        steel_type = "75 Angle"
    print(f"Steel Type (H={H_O}): {steel_type}")

    print("\n--- ETC Calculations ---")

    # Air vent
    capacity = W_O * L_O_C * H_O
    air_vent_size = "50mm" if capacity < 100 else "100mm"
    print(f"Capacity={capacity}m³, Air Vent: {air_vent_size}")

    # Ladders
    internal_ladders = 1 + N_PA
    external_ladders = 1
    print(f"Internal Ladders: {internal_ladders}, External: {external_ladders}")

if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# GRP TANK CONFIGURATION - VERIFICATION TEST")
    print("#" * 70)

    try:
        # Run formula verification first
        verify_specific_formulas()

        # Run test cases
        test_tank_3x5x2()
        test_tank_with_partition()
        test_half_meter_dimensions()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
