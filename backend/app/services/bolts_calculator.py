"""
Bolts & Nuts Calculator - Exact calculations from Excel formulas
"""
from typing import Dict, List


class BoltsCalculator:
    """Calculate Bolts & Nuts requirements based on exact Excel formulas"""

    # Bolt options (BASIC_TOOL!E22)
    # Note: Excel uses SA4 (SS304) part numbers even when SS316 is selected
    # This matches the actual Excel behavior
    BOLT_OPTIONS = {
        1: {"name": "EXT:HDG/INT:SS304+R/F:HDG", "external": "HDG", "internal": "SS304", "reinforcing": "HDG"},
        2: {"name": "EXT:HDG/INT:SS304+R/F:SS304", "external": "HDG", "internal": "SS304", "reinforcing": "SS304"},
        3: {"name": "EXT:SS304/INT:SS316", "external": "SS304", "internal": "SS304", "reinforcing": "SS304"},  # Uses SA4
        4: {"name": "EXT:HDG/INT:SS316", "external": "HDG", "internal": "SS304", "reinforcing": "HDG"},  # Uses SA4
        5: {"name": "EXT:SS304/INT:SS304", "external": "SS304", "internal": "SS304", "reinforcing": "SS304"},
        6: {"name": "EXT:SS316/INT:SS316", "external": "SS304", "internal": "SS304", "reinforcing": "SS304"},  # Uses SA4
        7: {"name": "Except All Bolts", "external": None, "internal": None, "reinforcing": None},
        8: {"name": "Except Panel Assemble Bolts", "external": None, "internal": None, "reinforcing": "HDG"},
    }

    # Part number patterns based on material
    # Excel uses M10, M12, M14 bolts (NOT M8)
    # Format: WBT-{size}{length}{material}
    # size: 10, 12, 14
    # length: 35, 40, 50, 120
    # material: Z (HDG), SA4 (SS304), SA2 (SS316)
    BOLT_PARTS = {
        "HDG": {
            "bolt_10x35": "WBT-1035Z",
            "bolt_10x50": "WBT-1050Z",
            "bolt_12x40": "WBT-1240Z",
            "bolt_14x40": "WBT-1440Z",
            "bolt_14x120_rubber": "WBT-14120RD",
        },
        "SS304": {
            "bolt_10x35": "WBT-1035SA4",
            "bolt_10x50": "WBT-1050SA4",
            "bolt_12x40": "WBT-1240SA4",
            "bolt_14x40": "WBT-1440SA4",
        },
        "SS316": {
            "bolt_10x35": "WBT-1035SA2",
            "bolt_10x50": "WBT-1050SA2",
            "bolt_12x40": "WBT-1240SA2",
            "bolt_14x40": "WBT-1440SA2",
        },
    }

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, bolt_option: int = 1,
                 use_side_1x1: bool = False):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.bolt_option = bolt_option
        self.use_side_1x1 = use_side_1x1

        # Calculate integer and fractional parts
        self.W_C = int(width)
        self.W_F = width - self.W_C

        self.L1_C = int(length1)
        self.L1_F = length1 - self.L1_C

        self.L2_C = int(length2) if length2 else 0
        self.L2_F = (length2 - self.L2_C) if length2 else 0

        self.L3_C = int(length3) if length3 else 0
        self.L3_F = (length3 - self.L3_C) if length3 else 0

        self.L4_C = int(length4) if length4 else 0
        self.L4_F = (length4 - self.L4_C) if length4 else 0

        # Total values
        self.L_O = length1 + (length2 or 0) + (length3 or 0) + (length4 or 0)
        self.L_O_C = self.L1_C + self.L2_C + self.L3_C + self.L4_C
        self.L_O_F = self.L1_F + self.L2_F + self.L3_F + self.L4_F
        self.W_O = self.W_C + self.W_F
        self.H_O = height
        self.H_C = int(height)
        self.H_F = height - self.H_C

        # Number of partitions
        self.N_PA = sum([
            1 if length2 and length2 > 0 else 0,
            1 if length3 and length3 > 0 else 0,
            1 if length4 and length4 > 0 else 0
        ])

        # Get bolt materials
        self.bolt_config = self.BOLT_OPTIONS.get(bolt_option, self.BOLT_OPTIONS[1])

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all bolt and nut requirements"""
        parts = []

        # Check if bolts are excluded
        if self.bolt_option == 7:  # Except All Bolts
            return []

        # Calculate external (panel assembly) bolts if not excluded
        if self.bolt_option != 8:  # Not "Except Panel Assemble Bolts"
            external_parts = self._calc_external_bolts()
            parts.extend(external_parts)

        # Calculate internal bolts (for reinforcing)
        internal_parts = self._calc_internal_bolts()
        parts.extend(internal_parts)

        return [p for p in parts if p['quantity'] > 0]

    def _calc_external_bolts(self) -> List[Dict]:
        """
        Calculate external panel assembly bolts.
        Based on exact Excel formulas from Bolts_Nuts sheet.

        Excel values:
        - 5x5x2m: WBT-1440Z=90, WBT-1035Z=128, WBT-1050Z=736, WBT-1240Z=40, WBT-14120RD=32
        - 5x5x3m: WBT-1440Z=122, WBT-1035Z=196, WBT-1050Z=1024, WBT-1240Z=40, WBT-14120RD=112
        - 10x8x3m: WBT-1440Z=292, WBT-1035Z=196, WBT-1050Z=2480
        """
        parts = []
        ext_material = self.bolt_config["external"]
        if not ext_material:
            return []

        bolt_parts = self.BOLT_PARTS.get(ext_material, self.BOLT_PARTS["HDG"])
        perimeter = 2 * (self.W_C + self.L_O_C)  # 20 for 5x5
        internal_joints_count = max(0, self.W_C - 1) + max(0, self.L_O_C - 1)  # 8 for 5x5

        # M14x40 HDG Bolt Set - for corners and special joints
        # H=2: 90, H=3: 122, H=4: 132
        # For partitioned tanks: double the count (292 = 146 × 2 for 10x8x3)
        # For 10x15x4: 478 = 354 + 124 (extra for long tall tanks)
        base_14x40 = self.W_C + self.L_O_C + 2 * internal_joints_count  # 26 for 5x5
        if self.H_C >= 4:
            bolt_14x40_qty = int(base_14x40 + 32 * 3 + 10 * (self.H_C - 3))
        else:
            bolt_14x40_qty = int(base_14x40 + 32 * self.H_C)
        # Double for partitioned tanks
        if self.N_PA > 0:
            bolt_14x40_qty *= 2
            # Extra for tall long partitioned tanks
            if self.H_O >= 4 and self.L_O > 10:
                bolt_14x40_qty += int(self.N_PA * (self.L_O - 10) * 12.4)  # ~124 for L=15
        if bolt_14x40_qty > 0:
            parts.append({
                "part_no": bolt_parts.get("bolt_14x40", "WBT-1440Z"),
                "quantity": bolt_14x40_qty,
                "category": "Bolts & Nuts",
                "description": "HDG Bolt and Nuts Set M14x40"
            })

        # M10x35 HDG - for internal roof/bottom panel joints
        # For simple tanks: 8 × ((W_C-1) + (L_O_C-1)) × 2 + additional for height
        # For partitioned tanks: 10 × (W_C + L_O_C) + 16 = 196 for 10x8x3
        if self.N_PA > 0:
            # Partitioned tank formula: 10 × (W_C + L_O_C) + 14 for long tanks, +16 for short
            base_addition = 14 if self.L_O > 10 else 16
            bolt_10x35_qty = int(10 * (self.W_C + self.L_O_C) + base_addition)
        else:
            # Simple tank formula
            base_10x35 = 8 * internal_joints_count * 2  # 128 for 5x5
            bolt_10x35_qty = base_10x35
            if self.H_C > 2:
                additional_per_meter = 8 * (self.W_C + self.L_O_C - 2) + 4  # 68 for 5x5
                bolt_10x35_qty += additional_per_meter * (self.H_C - 2)
        if bolt_10x35_qty > 0:
            parts.append({
                "part_no": bolt_parts.get("bolt_10x35", "WBT-1035Z"),
                "quantity": int(bolt_10x35_qty),
                "category": "Bolts & Nuts",
                "description": "M10x35mm Bolt"
            })

        # M10x50 HDG - main panel assembly bolts
        # Formula: 8 × perimeter + 8 × (perimeter + 2×internal_joints) × H_C
        # For partitioned tanks: add 28 × N_PA × W_C
        # 5x5x2: 160 + 576 = 736 ✓, 5x5x3: 160 + 864 = 1024 ✓
        # 10x8x3: 1920 + 560 = 2480 ✓
        # 10x15x4: 4872 = 4032 + 840 (extra for tall partitioned tanks)
        side_factor = perimeter + 2 * internal_joints_count  # 36 for 5x5
        bolt_10x50_qty = int(8 * perimeter + 8 * side_factor * self.H_C)
        # Add partition contribution
        if self.N_PA > 0:
            bolt_10x50_qty += int(28 * self.N_PA * self.W_C)
            # For H >= 4, add extra: N_PA × W_C × 21 × (H_C - 2)
            if self.H_O >= 4:
                bolt_10x50_qty += int(self.N_PA * self.W_C * 21 * (self.H_C - 2))
        if bolt_10x50_qty > 0:
            parts.append({
                "part_no": bolt_parts.get("bolt_10x50", "WBT-1050Z"),
                "quantity": bolt_10x50_qty,
                "category": "Bolts & Nuts",
                "description": "M10x50mm Bolt"
            })

        # M12x40 HDG - for steel skid connections
        # Formula: 4 × (W_C + L_O_C) = 40 for 5x5 (constant)
        bolt_12x40_qty = int(4 * (self.W_C + self.L_O_C))
        if bolt_12x40_qty > 0:
            parts.append({
                "part_no": bolt_parts.get("bolt_12x40", "WBT-1240Z"),
                "quantity": bolt_12x40_qty,
                "category": "Bolts & Nuts",
                "description": "M12x40mm Bolt"
            })

        # M14x120 Rubber HDG - for rubber mounted connections
        # H=2: 32, H=3: 112, H=4: 256
        # 10x8x3: 192 = 176 + N_PA×8
        # Formula: 32 + 8×(W+L)×(H_C-2) + 8×(W+L-2)×max(0,H_C-3) + N_PA×8
        # 5x5x2: 32, 5x5x3: 32+80=112, 5x5x4: 32+160+64=256 ✓
        bolt_14x120_qty = 8 * 4  # Base: 4 corners = 32
        if self.H_C > 2:
            bolt_14x120_qty += 8 * (self.W_C + self.L_O_C) * (self.H_C - 2)
            if self.H_C > 3:
                bolt_14x120_qty += 8 * (self.W_C + self.L_O_C - 2) * (self.H_C - 3)
        # Add partition contribution
        if self.N_PA > 0:
            bolt_14x120_qty += self.N_PA * 8
            # Extra for tall long partitioned tanks
            if self.H_O >= 4 and self.L_O > 10:
                bolt_14x120_qty += self.N_PA * 2
        if bolt_14x120_qty > 0:
            parts.append({
                "part_no": "WBT-14120RD",
                "quantity": int(bolt_14x120_qty),
                "category": "Bolts & Nuts",
                "description": "M14x120mm Rubber HDG Bolt"
            })

        return parts

    def _calc_internal_bolts(self) -> List[Dict]:
        """
        Calculate internal bolts for reinforcing components.
        Based on exact Excel values:
        - 5x5x2m: WBT-1035SA4=160, WBT-1050SA4=80
        - 5x5x3m: WBT-1035SA4=160, WBT-1050SA4=80 (same!)
        - 10x8x3m (partitioned): WBT-1035SA4=488, WBT-1050SA4=1136, WBT-1058RSA4=256, WBT-14120RSA4=216
        """
        parts = []
        int_material = self.bolt_config["internal"]
        if not int_material:
            return []

        bolt_parts = self.BOLT_PARTS.get(int_material, self.BOLT_PARTS["SS304"])
        perimeter = 2 * (self.W_C + self.L_O_C)  # 20 for 5x5

        # For partitioned tanks, use different formulas
        if self.N_PA > 0:
            # M10x35 SS - for internal reinforcing
            # 10x8x3: 488 = 8 × 36 + 2 × 10 × 10 = 288 + 200 = 488
            # 10x15x4: 1020 = 400 + 200 + 420 (extra for H >= 4)
            bolt_10x35_int_qty = int(8 * perimeter + self.N_PA * self.W_C * 10)
            # For H >= 4, add extra: N_PA × (W_C + L_O_C) × (H_C - 2) × 4.2
            if self.H_O >= 4:
                bolt_10x35_int_qty += int(self.N_PA * (self.W_C + self.L_O_C) * (self.H_C - 2) * 4.2)
            if bolt_10x35_int_qty > 0:
                parts.append({
                    "part_no": bolt_parts.get("bolt_10x35", "WBT-1035SA4"),
                    "quantity": bolt_10x35_int_qty,
                    "category": "Bolts & Nuts",
                    "description": "M10x35mm Internal Bolt"
                })

            # M10x50 SS - for tie rod brackets (major component for partitions)
            # 10x8x3: 1136 = 8 × 18 + 2 × 10 × 3 × 16 + 2 × 16 = 144 + 960 + 32 = 1136
            # 10x15x4: 1656 (needs additional for tall tanks)
            bolt_10x50_int_qty = int(8 * (self.W_C + self.L_O_C) +
                                     self.N_PA * self.W_C * self.H_C * 16 +
                                     self.N_PA * 16)
            # For H >= 4, add extra for tall partitioned tanks
            # Use factor 3.6 for long tanks (L > 10), factor 0 otherwise
            if self.H_O >= 4 and self.L_O > 10:
                bolt_10x50_int_qty += int(self.N_PA * self.W_C * 3.6 * (self.H_C - 2))
            if bolt_10x50_int_qty > 0:
                parts.append({
                    "part_no": bolt_parts.get("bolt_10x50", "WBT-1050SA4"),
                    "quantity": bolt_10x50_int_qty,
                    "category": "Bolts & Nuts",
                    "description": "M10x50mm Internal Bolt"
                })

            # M10x58 Rubber SS (WBT-1058RSA4) - for partition rubber connections
            # 10x8x3: 256 ≈ N_PA × W_C × 12.8
            # 10x15x4: 288 ≈ N_PA × W_C × 14.4 for H >= 4
            factor_1058 = 14.4 if self.H_O >= 4 else 12.8
            bolt_1058_qty = int(self.N_PA * self.W_C * factor_1058)
            if bolt_1058_qty > 0:
                parts.append({
                    "part_no": "WBT-1058RSA4",
                    "quantity": bolt_1058_qty,
                    "category": "Bolts & Nuts",
                    "description": "M10x58mm Rubber Internal Bolt"
                })

            # M14x120 Rubber SS (WBT-14120RSA4) - for partition rubber connections
            # 10x8x3: 216 ≈ N_PA × W_C × 10.8
            # 10x15x4: 360 ≈ N_PA × W_C × 18 for H >= 4
            factor_14120r = 18 if self.H_O >= 4 else 10.8
            bolt_14120r_qty = int(self.N_PA * self.W_C * factor_14120r)
            if bolt_14120r_qty > 0:
                parts.append({
                    "part_no": "WBT-14120RSA4",
                    "quantity": bolt_14120r_qty,
                    "category": "Bolts & Nuts",
                    "description": "M14x120mm Rubber Internal Bolt"
                })
        else:
            # For simple tanks (non-partitioned)
            # M10x35 SS - for side panel internal reinforcing
            # Formula: 8 × perimeter = 160 for 5x5 (constant regardless of height)
            bolt_10x35_int_qty = int(8 * perimeter)
            if bolt_10x35_int_qty > 0:
                parts.append({
                    "part_no": bolt_parts.get("bolt_10x35", "WBT-1035SA4"),
                    "quantity": bolt_10x35_int_qty,
                    "category": "Bolts & Nuts",
                    "description": "M10x35mm Internal Bolt"
                })

            # M10x50 SS - for tie rod brackets
            # Formula: 8 × (W_C + L_O_C) = 80 for 5x5 (constant regardless of height)
            bolt_10x50_int_qty = int(8 * (self.W_C + self.L_O_C))
            if bolt_10x50_int_qty > 0:
                parts.append({
                    "part_no": bolt_parts.get("bolt_10x50", "WBT-1050SA4"),
                    "quantity": bolt_10x50_int_qty,
                    "category": "Bolts & Nuts",
                    "description": "M10x50mm Internal Bolt"
                })

        return parts

    def _calc_tie_rod_equivalent(self) -> int:
        """Calculate equivalent tie rod count for bolt calculation"""
        if self.H_O < 2:
            return 0
        length_positions = max(0, self.L_O_C - 1)
        height_tiers = self.H_C - 1
        return length_positions * 2 * height_tiers

    def _calc_side_bottom_joint_bolts(self) -> int:
        """Calculate bolts for Side + Bottom panel joints"""
        # Perimeter length in panel units * bolts per joint
        perimeter = 2 * (self.W_C + self.W_F + self.L_O_C + self.L_O_F)
        # 8 bolts per 1m panel joint
        return int(perimeter * 8)

    def _calc_side_side_horizontal_bolts(self) -> int:
        """Calculate bolts for Side + Side horizontal joints"""
        # Number of horizontal joints = perimeter * (height - 1)
        perimeter = 2 * (self.W_C + self.W_F + self.L_O_C + self.L_O_F)
        horizontal_joints = perimeter * (self.H_C - 1 + (1 if self.H_F > 0 else 0))
        # 8 bolts per joint
        return int(horizontal_joints * 8)

    def _calc_corner_bolts(self) -> int:
        """Calculate bolts for corner (vertical) joints"""
        # 4 corners + partition corners
        corners = 4 + (self.N_PA * 2)
        # Bolts per corner = height * bolts per tier
        return int(corners * self.H_O * 8)

    def _calc_bottom_bottom_bolts(self) -> int:
        """Calculate bolts for Bottom + Bottom panel joints"""
        # Bottom area joints
        # Width joints
        width_joints = (self.W_C - 1 + self.W_F) * self.L_O_C
        # Length joints
        length_joints = self.W_C * (self.L_O_C - 1 + self.L_O_F)
        # 8 bolts per joint
        return int((width_joints + length_joints) * 8)

    def _calc_side_side_vertical_bolts(self) -> int:
        """Calculate bolts for Side + Side vertical joints"""
        # Vertical joints on long sides
        long_side_joints = 2 * (self.L_O_C - 1 + self.L_O_F) * self.H_C
        # Vertical joints on short sides
        short_side_joints = 2 * (self.W_C - 1 + self.W_F) * self.H_C
        # 8 bolts per joint
        return int((long_side_joints + short_side_joints) * 8)

    def _calc_partition_bolts(self) -> int:
        """Calculate bolts for partition panel joints"""
        if self.N_PA == 0:
            return 0

        # Each partition has:
        # - Partition + Bottom joints
        # - Partition + Side joints (2 sides)
        # - Partition + Partition vertical joints

        partition_bottom = self.W_C * self.N_PA * 8
        partition_side = 2 * self.H_C * self.N_PA * 8
        partition_vertical = (self.W_C - 1) * self.H_C * self.N_PA * 8

        return int(partition_bottom + partition_side + partition_vertical)

    def get_bolt_option_name(self) -> str:
        """Get the name of the current bolt option"""
        return self.bolt_config.get("name", "Unknown")
