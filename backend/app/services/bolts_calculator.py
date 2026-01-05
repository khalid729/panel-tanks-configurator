"""
Bolts & Nuts Calculator - Exact calculations from Excel formulas
Based on BoltnNuts sheet (sheet13)
"""
import math
from typing import Dict, List


class BoltsCalculator:
    """Calculate Bolts & Nuts requirements based on exact Excel formulas"""

    # Bolt options (BASIC_TOOL!F23)
    BOLT_OPTIONS = {
        1: {"name": "EXT:HDG/INT:SS304+R/F:HDG", "external": "Z", "internal": "SA4", "reinforcing": "Z"},
        2: {"name": "EXT:HDG/INT:SS304+R/F:SS304", "external": "Z", "internal": "SA4", "reinforcing": "SA4"},
        3: {"name": "EXT:SS304/INT:SS316", "external": "SA4", "internal": "SA2", "reinforcing": "SA4"},
        4: {"name": "EXT:HDG/INT:SS316", "external": "Z", "internal": "SA2", "reinforcing": "Z"},
        5: {"name": "EXT:SS304/INT:SS304", "external": "SA4", "internal": "SA4", "reinforcing": "SA4"},
        6: {"name": "EXT:SS316/INT:SS316", "external": "SA2", "internal": "SA2", "reinforcing": "SA2"},
        7: {"name": "Except All Bolts", "external": None, "internal": None, "reinforcing": None},
        8: {"name": "Except Panel Assemble Bolts", "external": None, "internal": None, "reinforcing": "Z"},
    }

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, bolt_option: int = 1,
                 skid_type: int = 1, insulation_type: int = 0,
                 steel_skid_m9: int = 0, steel_skid_m36: int = 0,
                 ext_reinforcing_l22: int = 0, ext_reinforcing_l23: int = 0, ext_reinforcing_l24: int = 0,
                 int_reinforcing_p18: int = 0, int_reinforcing_p19: int = 0):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.bolt_option = bolt_option
        self.skid_type = skid_type  # BASIC_TOOL!D17
        self.insulation_type = insulation_type  # BASIC_TOOL!D15

        # Values from other sheets
        self.steel_skid_m9 = steel_skid_m9  # Steel_Skid!M9
        self.steel_skid_m36 = steel_skid_m36  # Steel_Skid!M36
        self.ext_reinforcing_l22 = ext_reinforcing_l22
        self.ext_reinforcing_l23 = ext_reinforcing_l23
        self.ext_reinforcing_l24 = ext_reinforcing_l24
        self.int_reinforcing_p18 = int_reinforcing_p18
        self.int_reinforcing_p19 = int_reinforcing_p19

        # Calculate integer and fractional parts (matching Excel)
        self.W_O = width
        self.W_C = int(width)
        self.W_F = width - self.W_C

        self.L1_O = length1
        self.L1_C = int(length1)
        self.L1_F = length1 - self.L1_C

        self.L2_O = length2 or 0
        self.L2_C = int(length2) if length2 else 0
        self.L2_F = (length2 - self.L2_C) if length2 else 0

        self.L3_O = length3 or 0
        self.L3_C = int(length3) if length3 else 0
        self.L3_F = (length3 - self.L3_C) if length3 else 0

        self.L4_O = length4 or 0
        self.L4_C = int(length4) if length4 else 0
        self.L4_F = (length4 - self.L4_C) if length4 else 0

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

        # Get bolt materials
        self.bolt_config = self.BOLT_OPTIONS.get(bolt_option, self.BOLT_OPTIONS[1])

        # Pre-calculate common sums
        self.sum_L_C = self.L1_C + self.L2_C + self.L3_C + self.L4_C
        self.sum_L_F = self.L1_F + self.L2_F + self.L3_F + self.L4_F
        self.sum_L_total = self.sum_L_C + self.sum_L_F

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all bolt and nut requirements using exact Excel formulas"""
        parts = []

        # Check if bolts are excluded
        if self.bolt_option == 7:  # Except All Bolts
            return []

        ext_material = self.bolt_config["external"]
        int_material = self.bolt_config["internal"]

        # ========================================
        # WBT-1035 (M10x35mm) - Roof & Corner bolts
        # Rows 9,10 (corners) use external material
        # Rows 5,6 (roof) use internal material
        # ========================================
        if self.bolt_option != 8:  # Not "Except Panel Assemble Bolts"
            # External bolts (corners) - use HDG/Z
            wbt_1035_ext = self._calc_wbt_1035_external()
            if wbt_1035_ext > 0 and ext_material:
                parts.append({
                    "part_no": f"WBT-1035{ext_material}",
                    "quantity": wbt_1035_ext,
                    "category": "Bolts & Nuts",
                    "description": f"M10x35mm Bolt ({ext_material})"
                })

            # Internal bolts (roof) - use SS304/SA4
            wbt_1035_int = self._calc_wbt_1035_internal()
            if wbt_1035_int > 0 and int_material:
                parts.append({
                    "part_no": f"WBT-1035{int_material}",
                    "quantity": wbt_1035_int,
                    "category": "Bolts & Nuts",
                    "description": f"M10x35mm Roof Bolt ({int_material})"
                })

        # ========================================
        # WBT-1050 (M10x50mm) - Panel assembly bolts
        # Rows 12-16 (Bottom, Side joints) use external material
        # Row 11 (Roof+Side) uses internal material
        # ========================================
        if self.bolt_option != 8:
            # External bolts (bottom, side joints)
            wbt_1050_ext = self._calc_wbt_1050_external()
            if wbt_1050_ext > 0 and ext_material:
                parts.append({
                    "part_no": f"WBT-1050{ext_material}",
                    "quantity": wbt_1050_ext,
                    "category": "Bolts & Nuts",
                    "description": f"M10x50mm Bolt ({ext_material})"
                })

            # Internal bolts (roof+side, partitions)
            wbt_1050_int = self._calc_wbt_1050_internal()
            if wbt_1050_int > 0 and int_material:
                parts.append({
                    "part_no": f"WBT-1050{int_material}",
                    "quantity": wbt_1050_int,
                    "category": "Bolts & Nuts",
                    "description": f"M10x50mm Roof/Partition Bolt ({int_material})"
                })

        # ========================================
        # WBT-1240 (M12x40mm) - Steel Skid bolts
        # ========================================
        if self.bolt_option != 8:
            wbt_1240_qty = self._calc_wbt_1240()
            if wbt_1240_qty > 0 and ext_material:
                parts.append({
                    "part_no": f"WBT-1240{ext_material}",
                    "quantity": wbt_1240_qty,
                    "category": "Bolts & Nuts",
                    "description": f"M12x40mm Bolt ({ext_material})"
                })

        # ========================================
        # WBT-1440 (M14x40mm) - Structural bolts
        # ========================================
        if self.bolt_option != 8:
            wbt_1440_qty = self._calc_wbt_1440()
            if wbt_1440_qty > 0 and ext_material:
                parts.append({
                    "part_no": f"WBT-1440{ext_material}",
                    "quantity": wbt_1440_qty,
                    "category": "Bolts & Nuts",
                    "description": f"M14x40mm Bolt ({ext_material})"
                })

        # ========================================
        # WBT-1058R (M10x58mm Rubber) - Partition bolts
        # ========================================
        if self.N_PA > 0 and int_material:
            wbt_1058r_qty = self._calc_wbt_1058r()
            if wbt_1058r_qty > 0:
                parts.append({
                    "part_no": f"WBT-1058R{int_material}",
                    "quantity": wbt_1058r_qty,
                    "category": "Bolts & Nuts",
                    "description": f"M10x58mm Rubber Bolt ({int_material})"
                })

        # ========================================
        # WBT-14120R (M14x120mm Rubber) - Reinforcing bolts
        # ========================================
        wbt_14120r_qty = self._calc_wbt_14120r()
        if wbt_14120r_qty > 0:
            # External reinforcing uses RD (HDG with rubber)
            parts.append({
                "part_no": "WBT-14120RD",
                "quantity": wbt_14120r_qty,
                "category": "Bolts & Nuts",
                "description": "M14x120mm Rubber HDG Bolt"
            })

        # Internal reinforcing (if partitions)
        if self.N_PA > 0 and int_material:
            wbt_14120r_int = self._calc_wbt_14120r_internal()
            if wbt_14120r_int > 0:
                parts.append({
                    "part_no": f"WBT-14120R{int_material}",
                    "quantity": wbt_14120r_int,
                    "category": "Bolts & Nuts",
                    "description": f"M14x120mm Rubber Internal Bolt ({int_material})"
                })

        return [p for p in parts if p['quantity'] > 0]

    def _calc_wbt_1035_external(self) -> int:
        """
        Calculate WBT-1035 (M10x35mm) EXTERNAL bolt quantity.
        Only corner and side bolts use external material (HDG/Z).

        Excel formulas (external):
        Row 9: IF(H_O=2.5,1*4,0)+IF(H_O=3,1*4,0)+IF(H_O=3.5,2*4,0)+IF(H_O=4,2*4,0)+IF(H_O=4.5,3*4,0)+IF(H_O=5,3*4,0) - Corner Frames
        Row 10: H_O*8*2*4 - Corner Angle Frame+Side PNLs
        """
        qty = 0

        # Row 9: Connecting between Corner Frames
        # Excel: IF(H_O=2.5,1*4,0)+IF(H_O=3,1*4,0)+IF(H_O=3.5,2*4,0)+IF(H_O=4,2*4,0)+IF(H_O=4.5,3*4,0)+IF(H_O=5,3*4,0)
        row9 = 0
        if self.H_O == 2.5:
            row9 += 4
        if self.H_O == 3:
            row9 += 4
        if self.H_O == 3.5:
            row9 += 8
        if self.H_O == 4:
            row9 += 8
        if self.H_O == 4.5:
            row9 += 12
        if self.H_O == 5:
            row9 += 12
        qty += row9

        # Row 10: Corner Angle Frame+Side PNLs
        # Excel: H_O*8*2*4
        row10 = int(self.H_O * 8 * 2 * 4)
        qty += row10

        return qty

    def _calc_wbt_1035_internal(self) -> int:
        """
        Calculate internal WBT-1035 for roof panels (SA4/SA2).
        Roof bolts use internal material (SS304/SA4).

        Excel formulas (internal):
        Row 5: (4*W_C+2*W_F)*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-N_PA-1) - Roof+Roof (Vertical)
        Row 6: (4*(L1_C+L2_C+L3_C+L4_C)+2*(L1_F+L2_F+L3_F+L4_F))*CEILING(W_O-1,1) - Roof+Roof (Horizontal)
        """
        qty = 0

        # Row 5: Roof+Roof (Vertical) - uses SA4
        # Excel: (4*W_C+2*W_F)*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-N_PA-1)
        row5 = (4 * self.W_C + 2 * self.W_F) * (self.sum_L_total - self.N_PA - 1)
        qty += max(0, int(row5))

        # Row 6: Roof+Roof (Horizontal) - uses SA4
        # Excel: (4*(L1_C+L2_C+L3_C+L4_C)+2*(L1_F+L2_F+L3_F+L4_F))*CEILING(W_O-1,1)
        row6 = (4 * self.sum_L_C + 2 * self.sum_L_F) * math.ceil(self.W_O - 1)
        qty += max(0, int(row6))

        return qty

    def _calc_wbt_1050_external(self) -> int:
        """
        Calculate WBT-1050 (M10x50mm) EXTERNAL bolt quantity.
        Rows 12-16 use external material (HDG/Z).

        Excel formulas (external):
        Row 12: (8*W_C+4*W_F)*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-1) - Bottom+Bottom (Vertical)
        Row 13: (8*(L1_C+L2_C+L3_C+L4_C)+4*(L1_F+L2_F+L3_F+L4_F))*CEILING(W_O-1,1) - Bottom+Bottom (Horizontal)
        Row 14: H_O*((W_C+W_F-1)+(L_O_C+L_O_F-1))*2*8 - Side+Side (Vertical)
        Row 15: IF(H_O>2,8*(W_C+L1_C+...)*2*(H_C+H_F-2)+4*(H_O-1)*(W_F+L1_F+...)*(...),0)+... - Side+Side (Horizontal)
        Row 16: ((L1_C+L2_C+L3_C+L4_C+W_C)*8+(L1_F+L2_F+L3_F+L4_F+W_F)*4)*2 - Bottom+Side
        """
        qty = 0

        # Row 12: Bottom+Bottom (Vertical)
        # Excel: (8*W_C+4*W_F)*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-1)
        row12 = (8 * self.W_C + 4 * self.W_F) * (self.sum_L_total - 1)
        qty += max(0, int(row12))

        # Row 13: Bottom+Bottom (Horizontal)
        # Excel: (8*(L1_C+L2_C+L3_C+L4_C)+4*(L1_F+L2_F+L3_F+L4_F))*CEILING(W_O-1,1)
        row13 = (8 * self.sum_L_C + 4 * self.sum_L_F) * math.ceil(self.W_O - 1)
        qty += max(0, int(row13))

        # Row 14: Side+Side (Vertical)
        # Excel: H_O*((W_C+W_F-1)+(L_O_C+L_O_F-1))*2*8
        row14 = self.H_O * ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1)) * 2 * 8
        qty += int(row14)

        # Row 15: Side+Side (Horizontal)
        # Excel: IF(H_O>2,8*(W_C+L1_C+L2_C+L3_C+L4_C)*2*(H_C+H_F-2)+4*(H_O-1)*(W_F+L1_F+L2_F+L3_F+L4_F)*(H_C+H_F-2),0)
        #        +IF(BASIC_TOOL!D15>0,8*(W_C+L1_C+L2_C+L3_C+L4_C)*2+4*(W_F+L1_F+L2_F+L3_F+L4_F),0)
        row15 = 0
        if self.H_O > 2:
            h_factor = self.H_C + self.H_F - 2
            row15 += 8 * (self.W_C + self.sum_L_C) * 2 * h_factor
            row15 += 4 * (self.H_O - 1) * (self.W_F + self.sum_L_F) * h_factor
        if self.insulation_type > 0:
            row15 += 8 * (self.W_C + self.sum_L_C) * 2
            row15 += 4 * (self.W_F + self.sum_L_F)
        qty += int(row15)

        # Row 16: Bottom+Side
        # Excel: ((L1_C+L2_C+L3_C+L4_C+W_C)*8+(L1_F+L2_F+L3_F+L4_F+W_F)*4)*2
        row16 = ((self.sum_L_C + self.W_C) * 8 + (self.sum_L_F + self.W_F) * 4) * 2
        qty += int(row16)

        return qty

    def _calc_wbt_1050_internal(self) -> int:
        """
        Calculate internal WBT-1050 (SA4/SA2).
        Row 11 (Roof+Side) uses internal material.
        Partition bolts (Rows 19, 36, 37) also use internal material.

        Excel formulas (internal):
        Row 11: (L1_C+L2_C+L3_C+L4_C+W_C)*4*2+(L1_F+L2_F+L3_F+L4_F+W_F)*2*2 - Roof+Side PNLs
        Row 19: 4*(W_C+W_F)*N_PA - Partition Top+Roof
        Row 36: IF(...)*(W_O)*8*(H_C+H_F-2)*N_PA - Partition+Partition (Horizontal)
        Row 37: ((W_C+W_F-1)*(H_O))*8*N_PA - Partition+Partition (Vertical)
        """
        qty = 0

        # Row 11: Roof+Side PNLs - uses SA4
        row11 = (self.sum_L_C + self.W_C) * 4 * 2 + (self.sum_L_F + self.W_F) * 2 * 2
        qty += int(row11)

        if self.N_PA > 0:
            # Row 19: Partition Top+Roof
            # Excel: 4*(W_C+W_F)*N_PA
            row19 = 4 * (self.W_C + self.W_F) * self.N_PA
            qty += int(row19)

            # Row 36: Partition+Partition (Horizontal)
            # Excel: IF(BASIC_TOOL!E15=2,((W_O)*8*(H_C+H_F-2))*N_PA,IF(H_O=1.5,W_F*4,((W_O)*8*(H_C+H_F-2))*N_PA)+IF(OR(H_O=2,H_O=3,H_O=4,H_O=5),(W_O)*8))*N_PA
            row36 = 0
            if self.insulation_type == 2:
                row36 = (self.W_O * 8 * (self.H_C + self.H_F - 2)) * self.N_PA
            else:
                if self.H_O == 1.5:
                    row36 = self.W_F * 4
                else:
                    row36 = (self.W_O * 8 * (self.H_C + self.H_F - 2)) * self.N_PA
                if self.H_O in [2, 3, 4, 5]:
                    row36 += self.W_O * 8
                row36 *= self.N_PA
            qty += max(0, int(row36))

            # Row 37: Partition+Partition (Vertical)
            # Excel: ((W_C+W_F-1)*(H_O))*8*N_PA
            row37 = ((self.W_C + self.W_F - 1) * self.H_O) * 8 * self.N_PA
            qty += max(0, int(row37))

        return qty

    def _calc_wbt_1240(self) -> int:
        """
        Calculate WBT-1240 (M12x40mm) bolt quantity for Steel Skid.

        Excel formula:
        Row 17: (W_C+W_F+L_O_C+L_O_F)*2*2 - Side PNLs+Steel Skid
        """
        # Row 17: Side PNLs+Steel Skid
        # Excel: (W_C+W_F+L_O_C+L_O_F)*2*2
        row17 = (self.W_C + self.W_F + self.L_O_C + self.L_O_F) * 2 * 2
        return int(row17)

    def _calc_wbt_1440(self) -> int:
        """
        Calculate WBT-1440 (M14x40mm) bolt quantity for structural connections.

        Excel formulas:
        Row 21: (W_C+W_F+1)*4+IF(OR(H_O>2,BASIC_TOOL!D17=3,BASIC_TOOL!D17=4),(W_C+W_F+1)*4,0) - Width Frame Brackets
        Row 22: 2*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-1)*(W_C+W_F+1) - Sub Beam+Main Beam
        Row 23: Steel_Skid!M36 - Anchor bracket
        Row 24: 2*Steel_Skid!$M$9+IF(OR(H_O>2.5,BASIC_TOOL!D17=2,BASIC_TOOL!D17=3),2*Steel_Skid!$M$9,0) - Other brackets
        """
        qty = 0

        # Row 21: Width Frame Brackets
        # Excel: (W_C+W_F+1)*4+IF(OR(H_O>2,BASIC_TOOL!D17=3,BASIC_TOOL!D17=4),(W_C+W_F+1)*4,0)
        row21 = (self.W_C + self.W_F + 1) * 4
        if self.H_O > 2 or self.skid_type in [3, 4]:
            row21 += (self.W_C + self.W_F + 1) * 4
        qty += int(row21)

        # Row 22: Sub Beam+Main Beam
        # Excel: 2*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-1)*(W_C+W_F+1)
        row22 = 2 * (self.sum_L_total - 1) * (self.W_C + self.W_F + 1)
        qty += max(0, int(row22))

        # Row 23: Anchor bracket
        # Excel: Steel_Skid!M36
        row23 = self.steel_skid_m36
        qty += int(row23)

        # Row 24: Other brackets
        # Excel: 2*Steel_Skid!$M$9+IF(OR(H_O>2.5,BASIC_TOOL!D17=2,BASIC_TOOL!D17=3),2*Steel_Skid!$M$9,0)
        row24 = 2 * self.steel_skid_m9
        if self.H_O > 2.5 or self.skid_type in [2, 3]:
            row24 += 2 * self.steel_skid_m9
        qty += int(row24)

        return qty

    def _calc_wbt_1058r(self) -> int:
        """
        Calculate WBT-1058R (M10x58mm Rubber) bolt quantity for partitions.

        Excel formulas:
        Row 26: H_O*8*2*N_PA - Partition PNL+Side PNL
        Row 27: W_O*8*N_PA - Partition PNL+Bottom PNL
        """
        if self.N_PA == 0:
            return 0

        qty = 0

        # Row 26: Partition PNL+Side PNL
        # Excel: H_O*8*2*N_PA
        row26 = self.H_O * 8 * 2 * self.N_PA
        qty += int(row26)

        # Row 27: Partition PNL+Bottom PNL
        # Excel: W_O*8*N_PA
        row27 = self.W_O * 8 * self.N_PA
        qty += int(row27)

        return qty

    def _calc_wbt_14120r(self) -> int:
        """
        Calculate WBT-14120RD (M14x120mm Rubber HDG) bolt quantity for external reinforcing.

        Excel formulas:
        Row 30: External_Reinforcing!L22*2+External_Reinforcing!L23*4+External_Reinforcing!L24*2 - External Brackets
        Row 39: IF(H_O>3.3,((W_C+W_F-1)+L_O_C+L_O_F-N_PA-1)*2,0)*2 - For H>3.3
        """
        qty = 0

        # Row 30: External Brackets
        # Excel: External_Reinforcing!L22*2+External_Reinforcing!L23*4+External_Reinforcing!L24*2
        row30 = self.ext_reinforcing_l22 * 2 + self.ext_reinforcing_l23 * 4 + self.ext_reinforcing_l24 * 2
        qty += int(row30)

        # Row 39: For H>3.3
        # Excel: IF(H_O>3.3,((W_C+W_F-1)+L_O_C+L_O_F-N_PA-1)*2,0)*2
        row39 = 0
        if self.H_O > 3.3:
            row39 = ((self.W_C + self.W_F - 1) + self.L_O_C + self.L_O_F - self.N_PA - 1) * 2 * 2
        qty += max(0, int(row39))

        return qty

    def _calc_wbt_14120r_internal(self) -> int:
        """
        Calculate WBT-14120R internal (M14x120mm Rubber SA4/SA2) for partitions.

        Excel formula:
        Row 33: Internal_Reinforcing!P18*4*N_PA+Internal_Reinforcing!P19*2*N_PA - Internal brackets
        """
        if self.N_PA == 0:
            return 0

        # Row 33: Internal brackets
        # Excel: Internal_Reinforcing!P18*4*N_PA+Internal_Reinforcing!P19*2*N_PA
        row33 = self.int_reinforcing_p18 * 4 * self.N_PA + self.int_reinforcing_p19 * 2 * self.N_PA
        return int(row33)

    def get_bolt_option_name(self) -> str:
        """Get the name of the current bolt option"""
        return self.bolt_config.get("name", "Unknown")
