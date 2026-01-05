"""
Tie Rod Calculator - Internal tie rod calculations from exact Excel formulas
Based on Internal_Tie_rod1 sheet (sheet17)
"""
import math
from typing import Dict, List


class TieRodCalculator:
    """Calculate Tie Rod requirements based on exact Excel formulas"""

    # Height Multiplier table (from Excel AG11:AH19)
    HEIGHT_MULTIPLIER = {
        1.0: 0,
        1.5: 1,
        2.0: 1,
        2.5: 2,
        3.0: 3,
        3.5: 4,
        4.0: 5,
        4.5: 6,
        5.0: 7
    }

    # Tie Rod Length table (from Excel AG24:BF123)
    # Maps dimension (m) to {rod_length_mm: quantity}
    TIE_ROD_LENGTH_TABLE = {
        1.0: {880: 1},
        1.5: {1380: 1},
        2.0: {1880: 1},
        2.5: {2380: 1},
        3.0: {2880: 1},
        3.5: {3380: 1},
        4.0: {3880: 1},
        4.5: {4380: 1},
        5.0: {4880: 1},
        5.5: {1380: 1, 4000: 1},
        6.0: {1880: 1, 4000: 1},
        6.5: {2380: 1, 4000: 1},
        7.0: {2880: 1, 4000: 1},
        7.5: {3380: 1, 4000: 1},
        8.0: {3880: 1, 4000: 1},
        8.5: {4000: 1, 4380: 1},
        9.0: {4000: 1, 4880: 1},
        9.5: {1380: 1, 4000: 2},
        10.0: {1880: 1, 4000: 2},
        10.5: {2380: 1, 4000: 2},
        11.0: {2880: 1, 4000: 2},
        11.5: {3380: 1, 4000: 2},
        12.0: {3880: 1, 4000: 2},
        12.5: {4000: 2, 4380: 1},
        13.0: {4000: 2, 4880: 1},
        13.5: {1380: 1, 4000: 3},
        14.0: {1880: 1, 4000: 3},
        14.5: {2380: 1, 4000: 3},
        15.0: {2880: 1, 4000: 3},
        15.5: {3380: 1, 4000: 3},
        16.0: {3880: 1, 4000: 3},
        16.5: {4000: 3, 4380: 1},
        17.0: {4000: 3, 4880: 1},
        17.5: {1380: 1, 4000: 4},
        18.0: {1880: 1, 4000: 4},
        18.5: {2380: 1, 4000: 4},
        19.0: {2880: 1, 4000: 4},
        19.5: {3380: 1, 4000: 4},
        20.0: {3880: 1, 4000: 4},
    }

    # Tie rod material options (BASIC_TOOL!E23)
    MATERIAL_SS316 = 2  # SA2
    MATERIAL_SS304 = 4  # SA4

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, tie_rod_material: int = 4):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.tie_rod_material = tie_rod_material

        # Calculate integer and fractional parts
        self.W_C = int(width)
        self.W_F = width - self.W_C
        self.W_O = width

        self.L1_C = int(length1)
        self.L1_F = length1 - self.L1_C
        self.L1_O = length1

        self.L2_C = int(length2) if length2 else 0
        self.L2_F = (length2 - self.L2_C) if length2 else 0
        self.L2_O = length2 or 0

        self.L3_C = int(length3) if length3 else 0
        self.L3_F = (length3 - self.L3_C) if length3 else 0
        self.L3_O = length3 or 0

        self.L4_C = int(length4) if length4 else 0
        self.L4_F = (length4 - self.L4_C) if length4 else 0
        self.L4_O = length4 or 0

        # Total values
        self.L_O = length1 + (length2 or 0) + (length3 or 0) + (length4 or 0)
        self.L_O_C = self.L1_C + self.L2_C + self.L3_C + self.L4_C
        self.L_O_F = self.L1_F + self.L2_F + self.L3_F + self.L4_F
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
        self.material_suffix = "SA2" if tie_rod_material == self.MATERIAL_SS316 else "SA4"

    def _get_height_multiplier(self) -> int:
        """
        Get height multiplier from lookup table.
        Excel: LOOKUP(H_O,AG11:AG19,AH11:AH19)
        """
        # Find closest height in table
        closest_height = min(self.HEIGHT_MULTIPLIER.keys(),
                             key=lambda x: abs(x - self.H_O) if x <= self.H_O else float('inf'))
        return self.HEIGHT_MULTIPLIER.get(closest_height, 0)

    def _get_tie_rod_config(self, dimension: float) -> Dict[int, int]:
        """
        Get tie rod configuration for a given dimension.
        Returns dict of {rod_length_mm: quantity}
        """
        # Find closest dimension in table (round to nearest 0.5)
        rounded_dim = round(dimension * 2) / 2

        if rounded_dim in self.TIE_ROD_LENGTH_TABLE:
            return self.TIE_ROD_LENGTH_TABLE[rounded_dim].copy()

        # For dimensions not in table, calculate based on pattern
        # Pattern: For dim > 5m, use 4000mm segments + remainder
        if rounded_dim <= 5.0:
            # Single rod: (dim - 0.12) * 1000 rounded to standard
            rod_length = int((rounded_dim - 0.12) * 1000)
            return {self._round_to_standard(rod_length): 1}
        else:
            # Multiple rods: X * 4000mm + remainder
            num_4000 = int((rounded_dim - 1.5) / 4)
            remainder = rounded_dim - (num_4000 * 4)
            remainder_length = int((remainder - 0.12) * 1000)
            result = {4000: num_4000}
            std_remainder = self._round_to_standard(remainder_length)
            if std_remainder in result:
                result[std_remainder] += 1
            else:
                result[std_remainder] = 1
            return result

    def _round_to_standard(self, length: int) -> int:
        """Round to nearest standard tie rod length."""
        standard_lengths = [
            280, 380, 780, 880, 1000, 1280, 1380, 1780, 1880, 2000,
            2280, 2380, 2780, 2880, 3000, 3280, 3380, 3780, 3880,
            4000, 4280, 4380, 4780, 4880, 5000
        ]
        return min(standard_lengths, key=lambda x: abs(x - length))

    def calculate_all_parts(self) -> List[Dict]:
        """
        Calculate all tie rod parts using exact Excel formulas.

        Excel formulas:
        Width tie rods: LOOKUP(H_O,AG11:AH19)*(W_C+W_F-1)
        Length tie rods: LOOKUP(H_O,...)*((L1_C+L1_F-1)+IF(L2_O>1,(L2_C+L2_F-1),0)+...)+IF(H_O>2,(H_F+H_C-2)*N_PA,0)
        """
        parts = []
        height_mult = self._get_height_multiplier()

        if height_mult == 0:
            return parts  # No tie rods needed for H <= 1.0m

        # ===== Width Direction Tie Rods =====
        # Excel: LOOKUP(H_O,AG11:AG19,AH11:AH19)*(W_C+W_F-1)
        width_qty = height_mult * (self.W_C + self.W_F - 1)
        if width_qty > 0:
            width_rods = self._get_tie_rod_config(self.W_O)
            for rod_length, rod_count in width_rods.items():
                part_no = f"TR-12M{rod_length:04d}{self.material_suffix}"
                parts.append({
                    "part_no": part_no,
                    "quantity": int(width_qty * rod_count),
                    "category": "Internal Tie-rod",
                    "description": f"Tie Rod {rod_length}mm (Width)"
                })

        # ===== Length Direction Tie Rods =====
        # For each section (L1, L2, L3, L4)

        # Section 1 (L1)
        # Excel: LOOKUP(H_O,...)*((L1_C+L1_F-1)+...)
        l1_positions = self.L1_C + self.L1_F - 1
        if l1_positions > 0:
            l1_qty = height_mult * l1_positions
            l1_rods = self._get_tie_rod_config(self.L1_O)
            for rod_length, rod_count in l1_rods.items():
                part_no = f"TR-12M{rod_length:04d}{self.material_suffix}"
                self._add_or_update_part(parts, part_no, int(l1_qty * rod_count),
                                         f"Tie Rod {rod_length}mm (L1)")

        # Section 2 (L2) - only if L2_O > 1
        if self.L2_O > 1:
            l2_positions = self.L2_C + self.L2_F - 1
            if l2_positions > 0:
                l2_qty = height_mult * l2_positions
                l2_rods = self._get_tie_rod_config(self.L2_O)
                for rod_length, rod_count in l2_rods.items():
                    part_no = f"TR-12M{rod_length:04d}{self.material_suffix}"
                    self._add_or_update_part(parts, part_no, int(l2_qty * rod_count),
                                             f"Tie Rod {rod_length}mm (L2)")

        # Section 3 (L3) - only if L3_O > 1
        if self.L3_O > 1:
            l3_positions = self.L3_C + self.L3_F - 1
            if l3_positions > 0:
                l3_qty = height_mult * l3_positions
                l3_rods = self._get_tie_rod_config(self.L3_O)
                for rod_length, rod_count in l3_rods.items():
                    part_no = f"TR-12M{rod_length:04d}{self.material_suffix}"
                    self._add_or_update_part(parts, part_no, int(l3_qty * rod_count),
                                             f"Tie Rod {rod_length}mm (L3)")

        # Section 4 (L4) - only if L4_O > 1
        if self.L4_O > 1:
            l4_positions = self.L4_C + self.L4_F - 1
            if l4_positions > 0:
                l4_qty = height_mult * l4_positions
                l4_rods = self._get_tie_rod_config(self.L4_O)
                for rod_length, rod_count in l4_rods.items():
                    part_no = f"TR-12M{rod_length:04d}{self.material_suffix}"
                    self._add_or_update_part(parts, part_no, int(l4_qty * rod_count),
                                             f"Tie Rod {rod_length}mm (L4)")

        # ===== Partition Tie Rods =====
        # Excel: IF(H_O>2,(H_F+H_C-2)*N_PA,0)
        if self.H_O > 2 and self.N_PA > 0:
            partition_positions = (self.H_F + self.H_C - 2) * self.N_PA
            if partition_positions > 0:
                # Partition tie rods use width dimension
                partition_rods = self._get_tie_rod_config(self.W_O)
                for rod_length, rod_count in partition_rods.items():
                    part_no = f"TR-12M{rod_length:04d}{self.material_suffix}"
                    self._add_or_update_part(parts, part_no, int(partition_positions * rod_count),
                                             f"Tie Rod {rod_length}mm (Partition)")

        # ===== Tie Rod Connectors =====
        # Connectors are needed when tie rod spans > 5m (uses multiple segments)
        connectors = self._calc_connectors(parts)
        parts.extend(connectors)

        return [p for p in parts if p.get('quantity', 0) > 0]

    def _add_or_update_part(self, parts: List[Dict], part_no: str, qty: int, desc: str):
        """Add quantity to existing part or create new entry."""
        for part in parts:
            if part["part_no"] == part_no:
                part["quantity"] += qty
                return
        parts.append({
            "part_no": part_no,
            "quantity": qty,
            "category": "Internal Tie-rod",
            "description": desc
        })

    def _calc_connectors(self, parts: List[Dict]) -> List[Dict]:
        """
        Calculate tie rod connectors.
        Connectors join tie rod segments (4000mm rods).
        """
        # Count 4000mm tie rods
        tr_4000_qty = 0
        for part in parts:
            if "4000" in part["part_no"]:
                tr_4000_qty += part["quantity"]

        if tr_4000_qty > 0:
            return [{
                "part_no": f"TC-12M0060{self.material_suffix}",
                "quantity": tr_4000_qty,
                "category": "Internal Tie-rod",
                "description": "Tie Rod Connector"
            }]
        return []

    def get_tie_rod_accessories(self) -> List[Dict]:
        """
        Get tie rod accessories (nuts, washers).
        Each tie rod assembly needs 4 nuts and 4 washers.
        """
        # Calculate total tie rod assemblies
        height_mult = self._get_height_multiplier()
        if height_mult == 0:
            return []

        # Width assemblies
        width_assemblies = height_mult * (self.W_C + self.W_F - 1)

        # Length assemblies
        length_positions = (self.L1_C + self.L1_F - 1)
        if self.L2_O > 1:
            length_positions += (self.L2_C + self.L2_F - 1)
        if self.L3_O > 1:
            length_positions += (self.L3_C + self.L3_F - 1)
        if self.L4_O > 1:
            length_positions += (self.L4_C + self.L4_F - 1)
        length_assemblies = height_mult * length_positions

        # Partition assemblies
        partition_assemblies = 0
        if self.H_O > 2 and self.N_PA > 0:
            partition_assemblies = (self.H_F + self.H_C - 2) * self.N_PA

        total_assemblies = int(width_assemblies + length_assemblies + partition_assemblies)

        if total_assemblies == 0:
            return []

        # Each assembly needs 4 nuts and 4 washers
        return [
            {
                "part_no": f"NUT({self.material_suffix})",
                "quantity": total_assemblies * 4,
                "category": "Internal Tie-rod",
                "description": "T/Rod Nut M12"
            },
            {
                "part_no": f"BW({self.material_suffix})",
                "quantity": total_assemblies * 4,
                "category": "Internal Tie-rod",
                "description": "T/Rod Washer M12"
            }
        ]
