"""
ETC Calculator - Air Vent, Ladders, Level Indicator, Sealing Tape, etc.
Based on exact Excel formulas from ETC sheet
"""
import math
from typing import Dict, List


class ETCCalculator:
    """Calculate ETC (miscellaneous) requirements based on exact Excel formulas"""

    # Level indicator options (BASIC_TOOL!B27)
    LEVEL_INDICATOR_GLASS = 1
    LEVEL_INDICATOR_SENSOR = 2
    LEVEL_INDICATOR_NONE = 0

    # Ladder material options
    LADDER_INTERNAL_SS = 1  # Stainless Steel
    LADDER_INTERNAL_FRP = 2  # FRP (Fiberglass)
    LADDER_EXTERNAL_HDG = 1  # Hot Dip Galvanized
    LADDER_EXTERNAL_SS = 2  # Stainless Steel

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, nominal_capacity: float = 0,
                 level_indicator_type: int = 1, internal_ladder_material: int = 1,
                 external_ladder_material: int = 1):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.nominal_capacity = nominal_capacity
        self.level_indicator_type = level_indicator_type
        self.internal_ladder_material = internal_ladder_material
        self.external_ladder_material = external_ladder_material

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

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all ETC parts"""
        parts = []

        # Air Vent
        air_vent = self._calc_air_vent()
        if air_vent:
            parts.append(air_vent)

        # Roof Supporter
        roof_supporter = self._calc_roof_supporter()
        if roof_supporter:
            parts.append(roof_supporter)

        # Internal Ladder
        internal_ladder = self._calc_internal_ladder()
        if internal_ladder:
            parts.append(internal_ladder)

        # External Ladder
        external_ladder = self._calc_external_ladder()
        if external_ladder:
            parts.append(external_ladder)

        # Silicon
        silicon = self._calc_silicon()
        if silicon:
            parts.append(silicon)

        # Level Indicator
        level_indicator = self._calc_level_indicator()
        if level_indicator:
            parts.append(level_indicator)

        # Sealing Tape 50mm
        tape_50mm = self._calc_sealing_tape_50mm()
        if tape_50mm:
            parts.append(tape_50mm)

        # Sealing Tape 120mm
        tape_120mm = self._calc_sealing_tape_120mm()
        if tape_120mm:
            parts.append(tape_120mm)

        return [p for p in parts if p and p.get('quantity', 0) > 0]

    def _calc_air_vent(self) -> Dict:
        """
        Air Vent calculation.
        Excel: =IF(BASIC_TOOL!H11<100,"WAV-0050A","WAV-0100A")
        Quantity: Maximum of (N_PA + 1) and (roof_area / 30)
        - For partitioned tanks: at least one per compartment (1 + N_PA)
        - For large tanks: 1 per 30m² of roof area
        - 10x8x3: max(3, 80/30) = max(3, 2.67) = 3
        - 10x15x4: max(3, 150/30) = max(3, 5) = 5
        """
        # Part number based on capacity
        if self.nominal_capacity < 100:
            part_no = "WAV-0050A"
            description = "Air Vent 50mm"
        else:
            part_no = "WAV-0100A"
            description = "Air Vent 100mm"

        # Quantity - max of compartment count and roof area based
        compartment_qty = 1 + self.N_PA
        roof_area = self.W_O * self.L_O
        area_qty = math.ceil(roof_area / 30)
        qty = max(compartment_qty, area_qty)

        return {
            "part_no": part_no,
            "quantity": int(qty),
            "category": "ETC",
            "description": description
        }

    def _calc_roof_supporter(self) -> Dict:
        """
        Roof Supporter calculation.
        Excel: ="WRS-"&H_O*1000&"F"
        Quantity: Complex formula based on sections

        For 5x5: 4 = 25/6.25 approximately
        For 10x8: 16 = 80/5 approximately
        """
        # Part number based on height
        height_mm = int(self.H_O * 1000)
        part_no = f"WRS-{height_mm}F"

        # Quantity calculation - based on roof area
        # For larger tanks (partitioned), simpler formula works better
        if self.N_PA > 0:
            # For partitioned tanks: W_C × L_O_C / 5 + adjustment for long tanks
            qty = int(self.W_C * self.L_O_C / 5)
            # Add 2 for long tanks (L > 10)
            if self.L_O > 10:
                qty += 2
        else:
            # For simple tanks: calculate per section
            qty = 0

            # Section 1
            if self.L1_C + self.L1_F > 1:
                qty += math.ceil((self.W_C + self.W_F - 1) * (self.L1_C + self.L1_F - 1) / 4)

            # Section 2
            L2_O = self.L2_C + self.L2_F
            if L2_O > 0:
                qty += math.ceil((self.W_O - 1) * (L2_O - 1) / 4)

            # Section 3
            L3_O = self.L3_C + self.L3_F
            if L3_O > 0:
                qty += math.floor((self.W_O - 2) * (L3_O - 2) / 4)

            # Section 4
            L4_O = self.L4_C + self.L4_F
            if L4_O > 0:
                qty += math.floor((self.W_O - 2) * (L4_O - 2) / 4)

        return {
            "part_no": part_no,
            "quantity": max(0, int(qty)),
            "category": "ETC",
            "description": f"Roof Supporter {height_mm}mm"
        }

    def _calc_internal_ladder(self) -> Dict:
        """
        Internal Ladder calculation.
        Excel: ="WLD-"&H_O*1000&"FI"
        Quantity: =N_PA+1
        """
        height_mm = int(self.H_O * 1000)

        # Material suffix
        if self.internal_ladder_material == self.LADDER_INTERNAL_FRP:
            suffix = "FI"  # FRP Internal
        else:
            suffix = "SI"  # Stainless Internal

        part_no = f"WLD-{height_mm}{suffix}"

        # One per section
        qty = self.N_PA + 1

        return {
            "part_no": part_no,
            "quantity": int(qty),
            "category": "ETC",
            "description": f"Internal Ladder {height_mm}mm"
        }

    def _calc_external_ladder(self) -> Dict:
        """
        External Ladder calculation.
        Excel: ="WLD-"&H_O*1000&"ZO"
        Quantity: 1
        """
        height_mm = int(self.H_O * 1000)

        # Material suffix
        if self.external_ladder_material == self.LADDER_EXTERNAL_SS:
            suffix = "SO"  # Stainless External
        else:
            suffix = "ZO"  # HDG External

        part_no = f"WLD-{height_mm}{suffix}"

        return {
            "part_no": part_no,
            "quantity": 1,
            "category": "ETC",
            "description": f"External Ladder {height_mm}mm"
        }

    def _calc_silicon(self) -> Dict:
        """
        Silicon sealant calculation.
        Excel: =ROUNDUP(0.1*(W_C+W_F)*(L_O_C+L_O_F),0)
        """
        qty = math.ceil(0.1 * (self.W_C + self.W_F) * (self.L_O_C + self.L_O_F))

        return {
            "part_no": "Silicon",
            "quantity": max(1, int(qty)),
            "category": "ETC",
            "description": "Silicon Sealant (Tubes)"
        }

    def _calc_level_indicator(self) -> Dict:
        """
        Level Indicator calculation.
        Excel: =IF(BASIC_TOOL!B27=1,"WLV-"&H_O*1000&"SET(G)",
                  IF(BASIC_TOOL!B27=2, "WLV-0000"&"SET(S)",""))
        Quantity: =N_PA+1
        """
        if self.level_indicator_type == self.LEVEL_INDICATOR_NONE:
            return None

        height_mm = int(self.H_O * 1000)

        if self.level_indicator_type == self.LEVEL_INDICATOR_GLASS:
            part_no = f"WLV-{height_mm}SET(G)"
            description = f"Level Indicator Glass Type {height_mm}mm"
        else:  # Sensor type
            part_no = "WLV-0000SET(S)"
            description = "Level Indicator Sensor Type"

        qty = self.N_PA + 1

        return {
            "part_no": part_no,
            "quantity": int(qty),
            "category": "ETC",
            "description": description
        }

    def _calc_sealing_tape_50mm(self) -> Dict:
        """
        Sealing Tape 50mm calculation.
        Based on exact Excel values:
        - 5x5x2m: 284
        - 5x5x3m: 386
        - 5x5x4m: 495
        - 10x8x3m (partitioned): 1020

        Formula for simple tanks: base + height_factor × H_C + extra_for_h4
        Formula for partitioned tanks: adjusted scaling
        """
        perimeter = self.W_C + self.L_O_C  # 10 for 5x5
        floor_area = self.W_C * self.L_O_C  # 25 for 5x5

        if self.N_PA > 0:
            # For partitioned tanks: different formula
            # 10x8x3: 1020 = 80 × 6 + 18 × 3 × 10 = 480 + 540 = 1020
            # 10x15x4: 1929 = 900 + 1000 + 29 (extra for long tanks)
            # Formula: floor_area × 6 + perimeter × H_C × 10
            tape_qty = floor_area * 6 + perimeter * self.H_C * 10
            # Add extra for long tall tanks
            if self.L_O > 10 and self.H_O >= 4:
                tape_qty += int((self.L_O - 10) * 5.8)
        else:
            # For simple tanks
            base = perimeter * 8  # 80 for 5x5
            height_factor = floor_area * 4 + 2  # 102 for 5x5

            tape_qty = base + height_factor * self.H_C

            # Extra for H >= 4 (for mid panels): (W_C + L_O_C - 3) × (H_C - 3)
            if self.H_O >= 4:
                tape_qty += (perimeter - 3) * (self.H_C - 3)

        return {
            "part_no": "WST-0050RO",
            "quantity": max(1, int(tape_qty)),
            "category": "ETC",
            "description": "Sealing Tape 50mm (Meters)"
        }

    def _calc_sealing_tape_120mm(self) -> Dict:
        """
        Sealing Tape 120mm calculation.
        Excel: =4*H_O+1
        Used for corner sealing
        """
        qty = int(4 * self.H_O + 1)

        return {
            "part_no": "WST-0120RO",
            "quantity": qty,
            "category": "ETC",
            "description": "Sealing Tape 120mm (Roll)"
        }
