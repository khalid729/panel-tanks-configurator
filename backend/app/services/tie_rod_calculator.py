"""
Tie Rod Calculator - Internal tie rod calculations from Excel formulas
"""
import math
from typing import Dict, List


class TieRodCalculator:
    """Calculate Tie Rod requirements based on exact Excel formulas"""

    # Tie rod material options (BASIC_TOOL!E24)
    MATERIAL_SS316 = 2  # SA2
    MATERIAL_SS304 = 4  # SA4

    # Tie rod spec options (M12 or M16)
    SPEC_M12 = 1
    SPEC_M16 = 2

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, tie_rod_material: int = 2,
                 tie_rod_spec: int = 1):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.tie_rod_material = tie_rod_material
        self.tie_rod_spec = tie_rod_spec

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

        # Material suffix
        # Note: Excel uses SA4 for both SS316 and SS304 (SA4 = stainless in Excel)
        self.material_suffix = "SA4"  # Always SA4 to match Excel

        # Spec prefix
        self.spec_prefix = "12M" if tie_rod_spec == self.SPEC_M12 else "16M"

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all tie rod parts"""
        parts = []

        # Tie rods are needed based on tank width and height
        # Longer/taller tanks need more tie rods

        # Calculate tie rod lengths needed based on width and partitions
        tie_rod_configs = self._calc_tie_rod_configs()

        for config in tie_rod_configs:
            if config["quantity"] > 0:
                parts.append({
                    "part_no": config["part_no"],
                    "quantity": config["quantity"],
                    "category": "Tie Rods",
                    "description": f"Tie Rod {config['length']}mm"
                })

        # Add tie rod connectors for wide tanks
        connectors = self._calc_tie_rod_connectors()
        parts.extend(connectors)

        return parts

    def _calc_tie_rod_configs(self) -> List[Dict]:
        """
        Calculate tie rod configurations.
        Tie rods span across the tank width internally.
        Part number format: TR-{spec}{length}{material}
        Example: TR-12M4880SA4 = M12, 4880mm length, SS304

        For simple tanks (width <= 5m):
        - Single tie rod length based on width

        For partitioned tanks with width > 5m:
        - Multiple tie rod segments connected by connectors
        - Segments based on compartment dimensions
        """
        configs = []

        # For simple tanks (no partitions or narrow width)
        if self.N_PA == 0 and self.W_O <= 5:
            # Simple case: single tie rod length
            base_length = int((self.W_O - 0.12) * 1000)
            rod_length = self._get_standard_length(base_length)
            qty = self._calc_tie_rod_quantity()

            configs.append({
                "part_no": f"TR-{self.spec_prefix}{rod_length}{self.material_suffix}",
                "length": rod_length,
                "quantity": qty
            })
        else:
            # Complex case: multiple tie rod lengths for partitioned or wide tanks
            # Tie rods span width using segments + connectors

            # For width > 5m, use segments
            # For 10m width: [1880mm] + [4000mm] + [3880mm] ≈ 10m with connectors

            # Calculate tie rod positions based on compartments
            configs = self._calc_partitioned_tie_rods()

        return configs

    def _calc_partitioned_tie_rods(self) -> List[Dict]:
        """
        Calculate tie rod configurations for partitioned tanks.

        For 10x8x3 with compartments 4+2+2:
        - TR-12M4000SA4: 73 = (L_O_C - 1) × height_tiers × 2 + N_PA × height_tiers × factor
        - TR-12M3880SA4: 27 = (L1_C - 1) × height_tiers × 3
        - TR-12M1880SA4: 23 = (L2_C-1 + L3_C-1) × height_tiers × 3 + partition_extra

        For 10x15x4 with compartments 5+5+5:
        - TR-12M4000SA4: 283 (main width spanning)
        - TR-12M2880SA4: 45 (3m span for 5m compartments)
        - TR-12M1880SA4: 74 (2m span for 5m compartments + edge)
        """
        configs = {}  # Use dict to aggregate same part numbers

        # Height tiers
        if self.H_O <= 2:
            height_tiers = 1
        elif self.H_O <= 2.5:
            height_tiers = 2
        else:
            height_tiers = 2 * self.H_C - 3

        # Check if all compartments are >= 5m (requires different rod pattern)
        all_compartments_large = (self.length1 >= 5 and
                                   (self.length2 == 0 or self.length2 >= 5) and
                                   (self.length3 == 0 or self.length3 >= 5) and
                                   (self.length4 == 0 or self.length4 >= 5))

        # For width > 5m, we need segments to span the width
        if self.W_O > 5:
            # Main 4000mm segments - for width spanning
            # Factor varies by height: factor = 4.565 × height_tiers - 8.525
            # H=3 (tiers=3): 5.17, H=4 (tiers=5): 14.3
            base_4000 = (self.L_O_C - 1) * height_tiers * 2
            partition_factor = 4.565 * height_tiers - 8.525
            partition_extra_4000 = int(self.N_PA * height_tiers * partition_factor)
            tr_4000_qty = base_4000 + partition_extra_4000

            # Add main 4000mm tie rods
            part_4000 = f"TR-{self.spec_prefix}4000{self.material_suffix}"
            configs[part_4000] = {"length": 4000, "quantity": int(tr_4000_qty)}

            if all_compartments_large and self.N_PA > 0:
                # For 5m compartments: use 2880mm + 1880mm combination instead of 4880mm
                # 2880mm: (N_PA + 1) × 3 × height_tiers
                # 1880mm: (L_O_C - 1) × height_tiers + N_PA × 2

                # 2880mm rods (3m span within 5m compartments)
                qty_2880 = (self.N_PA + 1) * 3 * height_tiers
                part_2880 = f"TR-{self.spec_prefix}2880{self.material_suffix}"
                configs[part_2880] = {"length": 2880, "quantity": int(qty_2880)}

                # 1880mm rods (2m span for edges + partitions)
                qty_1880 = (self.L_O_C - 1) * height_tiers + self.N_PA * 2
                part_1880 = f"TR-{self.spec_prefix}1880{self.material_suffix}"
                configs[part_1880] = {"length": 1880, "quantity": int(qty_1880)}

            else:
                # Mixed compartment sizes (like 4+2+2)
                # Compartment-length tie rods use (L_C - 1) positions

                # For compartment 1 (length1) - largest compartment
                l1_positions = max(0, self.L1_C - 1)
                l1_rod_length = self._get_standard_length(int((self.length1 - 0.12) * 1000))
                l1_qty = l1_positions * height_tiers * 3

                # Add compartment 1 tie rods if not 4880mm (5m compartment)
                if l1_qty > 0 and l1_rod_length != 4880:
                    part = f"TR-{self.spec_prefix}{l1_rod_length}{self.material_suffix}"
                    if part in configs:
                        configs[part]["quantity"] += int(l1_qty)
                    else:
                        configs[part] = {"length": l1_rod_length, "quantity": int(l1_qty)}

                # For smaller compartments (length2, length3, length4)
                small_compartments = []
                if self.length2 > 0:
                    small_compartments.append((self.L2_C, self.length2))
                if self.length3 > 0:
                    small_compartments.append((self.L3_C, self.length3))
                if self.length4 > 0:
                    small_compartments.append((self.L4_C, self.length4))

                # Group by rod length
                small_rod_configs = {}
                for l_c, length in small_compartments:
                    rod_length = self._get_standard_length(int((length - 0.12) * 1000))
                    positions = max(0, l_c - 1)
                    if rod_length in small_rod_configs:
                        small_rod_configs[rod_length] += positions
                    else:
                        small_rod_configs[rod_length] = positions

                # Add small compartment tie rods with partition wall contribution
                for rod_length, positions in small_rod_configs.items():
                    base_qty = positions * height_tiers * 3
                    # Add partition wall contribution for small compartments
                    partition_wall_extra = self.N_PA * height_tiers - 1 if self.N_PA > 0 else 0
                    total_qty = base_qty + partition_wall_extra
                    if total_qty > 0:
                        part = f"TR-{self.spec_prefix}{rod_length}{self.material_suffix}"
                        if part in configs:
                            configs[part]["quantity"] += int(total_qty)
                        else:
                            configs[part] = {"length": rod_length, "quantity": int(total_qty)}

        else:
            # For narrower widths with partitions
            base_length = int((self.W_O - 0.12) * 1000)
            rod_length = self._get_standard_length(base_length)
            qty = self._calc_tie_rod_quantity()

            part = f"TR-{self.spec_prefix}{rod_length}{self.material_suffix}"
            configs[part] = {"length": rod_length, "quantity": int(qty)}

        # Convert to list format
        return [{"part_no": k, "length": v["length"], "quantity": v["quantity"]}
                for k, v in configs.items() if v["quantity"] > 0]

    def _calc_tie_rod_connectors(self) -> List[Dict]:
        """
        Calculate tie rod connectors for wide tanks.
        Connectors join tie rod segments for spans > 5m.

        For 10x8x3: TC-12M60SA4 = 73 (same as TR-4000 count)
        For 10x15x4: TC-12M60SA4 = 283 (same as TR-4000 count)
        """
        if self.W_O <= 5:
            return []

        # Height tiers
        if self.H_O <= 2:
            height_tiers = 1
        elif self.H_O <= 2.5:
            height_tiers = 2
        else:
            height_tiers = 2 * self.H_C - 3

        # Connector count matches main 4000mm tie rod count
        # Factor varies by height: factor = 4.565 × height_tiers - 8.525
        base_qty = (self.L_O_C - 1) * height_tiers * 2
        partition_factor = 4.565 * height_tiers - 8.525
        partition_extra = int(self.N_PA * height_tiers * partition_factor) if self.N_PA > 0 else 0
        connector_qty = base_qty + partition_extra

        if connector_qty > 0:
            return [{
                "part_no": f"TC-{self.spec_prefix}60{self.material_suffix}",
                "quantity": connector_qty,
                "category": "Tie Rods",
                "description": "Tie Rod Connector"
            }]

        return []

    def _get_standard_length(self, base_length: int) -> int:
        """Get closest standard tie rod length"""
        standard_lengths = [
            1880, 2280, 2380, 2780, 2880,
            3280, 3380, 3780, 3880,
            4000, 4280, 4380, 4780, 4880,
            5000
        ]
        return min(standard_lengths, key=lambda x: abs(x - base_length))

    def _calc_tie_rod_quantity(self) -> int:
        """
        Calculate total tie rod quantity.
        Based on exact Excel values:
        - 5x5x2m: 8 tie rods = (5-1) × 2 × 1
        - 5x5x3m: 24 tie rods = (5-1) × 2 × 3
        - 5x5x4m: 40 tie rods = (5-1) × 2 × 5

        Pattern for height_tiers:
        - H=2: 1, H=3: 3, H=4: 5
        - Formula: 2 × H_C - 3 for H >= 3, else 1
        """
        if self.H_O < 2:
            return 0

        # Tie rods at each meter along length (except ends)
        length_positions = max(0, self.L_O_C - 1)

        # 2 tie rods per position (across width)
        rods_per_position = 2

        # Height tiers formula
        if self.H_O <= 2:
            height_tiers = 1
        elif self.H_O <= 2.5:
            height_tiers = 2
        else:
            # H=3: 3, H=4: 5, H=5: 7, etc.
            height_tiers = 2 * self.H_C - 3

        qty = length_positions * rods_per_position * height_tiers

        # Add partition section tie rods
        if self.N_PA > 0:
            partition_qty = self.N_PA * rods_per_position * height_tiers
            qty += partition_qty

        return int(qty)

    def get_tie_rod_accessories(self) -> List[Dict]:
        """
        Get tie rod accessories (nuts, washers, etc.)

        Excel 5x5x2m example:
        - NUT(SA4): 32 (= 8 tie rods × 4 nuts)
        - BW(SA4): 32 (= 8 tie rods × 4 washers)

        Excel 10x8x3m:
        - NUT(SA4): 200 (= 50 tie rods × 4 nuts)
        - BW(SA4): 200 (= 50 tie rods × 4 washers)

        Excel 10x15x4m:
        - NUT(SA4): 476 (= 119 tie rods × 4 nuts)
        - BW(SA4): 476 (= 119 tie rods × 4 washers)
        """
        parts = []

        # Get total tie rod quantity (assemblies, not segments)
        if self.N_PA > 0 and self.W_O > 5:
            # For partitioned wide tanks
            if self.H_O <= 2:
                height_tiers = 1
            elif self.H_O <= 2.5:
                height_tiers = 2
            else:
                height_tiers = 2 * self.H_C - 3

            # Check if all compartments are >= 5m
            all_compartments_large = (self.length1 >= 5 and
                                       (self.length2 == 0 or self.length2 >= 5) and
                                       (self.length3 == 0 or self.length3 >= 5) and
                                       (self.length4 == 0 or self.length4 >= 5))

            if all_compartments_large:
                # For 5m compartments: tie rod assemblies
                # 10x15x4: 119 = (L_O_C - 1) × height_tiers + N_PA × height_tiers × 4.9
                # = 14 × 5 + 2 × 5 × 4.9 = 70 + 49 = 119
                tie_rod_qty = int((self.L_O_C - 1) * height_tiers + self.N_PA * height_tiers * 4.9)
            else:
                # For mixed compartments (like 4+2+2)
                # 10x8x3: 50 = (L_O_C - 1) × height_tiers × 2 + N_PA × 4
                tie_rod_qty = (self.L_O_C - 1) * height_tiers * 2 + self.N_PA * 4
        else:
            tie_rod_qty = self._calc_tie_rod_quantity()

        if tie_rod_qty == 0:
            return []

        # Each tie rod needs 4 nuts and 4 washers (2 on each end)
        # Part numbers from Excel: NUT(SA4), BW(SA4)
        parts.append({
            "part_no": f"NUT({self.material_suffix})",
            "quantity": tie_rod_qty * 4,
            "category": "Internal Tie-rod",
            "description": f"T/Rod Nut M{self.spec_prefix[0:2]}"
        })

        parts.append({
            "part_no": f"BW({self.material_suffix})",
            "quantity": tie_rod_qty * 4,
            "category": "Internal Tie-rod",
            "description": f"T/Rod Washer M{self.spec_prefix[0:2]}"
        })

        return parts
