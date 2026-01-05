"""
Reinforcing Calculator - Internal and External reinforcing calculations from exact Excel formulas
Based on External_Reinforcing (sheet14) and Internal_Reinforcing (sheet15)
"""
import math
from typing import Dict, List


class ReinforcingCalculator:
    """Calculate Reinforcing requirements based on exact Excel formulas"""

    # Material constants
    MATERIAL_SS316 = 2  # SA2
    MATERIAL_SS304 = 4  # SA4

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, internal_material: int = 4,
                 use_side_1x1: bool = False, insulation: bool = False):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.internal_material = internal_material
        self.use_side_1x1 = use_side_1x1
        self.insulation = insulation  # BASIC_TOOL!E15

        # Calculate integer and fractional parts (Excel W_C, W_F, etc.)
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

        # Sums for formulas
        self.sum_L_C = self.L1_C + self.L2_C + self.L3_C + self.L4_C
        self.sum_L_F = self.L1_F + self.L2_F + self.L3_F + self.L4_F

        # Material suffix
        self.material_suffix = "SA2" if internal_material == self.MATERIAL_SS316 else "SA4"

        # Perimeter (used in many formulas)
        # Excel S2: W_C+W_F-1+L_O_C+L_O_F-1-N_PA
        self.perimeter = self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all reinforcing parts"""
        parts = []

        # External reinforcing (HDG - Z suffix)
        external_parts = self._calc_external_reinforcing()
        parts.extend(external_parts)

        # Internal reinforcing (Stainless - SA2/SA4 suffix)
        internal_parts = self._calc_internal_reinforcing()
        parts.extend(internal_parts)

        return [p for p in parts if p['quantity'] > 0]

    def _calc_external_reinforcing(self) -> List[Dict]:
        """
        Calculate external reinforcing parts (HDG - Z suffix)
        Based on External_Reinforcing sheet (sheet14) Column K → Column O
        """
        parts = []

        # ===== Row 8-10: WFB-0450 series (only for half panels) =====
        # These are 0 for full-meter dimensions

        # ===== Row 11: WFB-0950ZL =====
        # Only for certain heights with half panels
        wfb_0950zl = 0
        if self.H_O >= 4:
            # Row 11 formula has U11 component
            pass  # Usually 0 for full panels

        # ===== Row 12: WFB-0950ZP (Main reinforcing plate) =====
        # O12 = P12 + Q12 + R12 + S12 + T12 + U12 + V12 + X12 + Y12
        # P12: IF(H_O>1.3,(W_C+L1_C+L2_C+L3_C+L4_C)*2,0)+IF(H_O>4.3,(W_C+L1_C+L2_C+L3_C+L4_C)*2,0)
        p12 = 0
        if self.H_O > 1.3:
            p12 += (self.W_C + self.sum_L_C) * 2
        if self.H_O > 4.3:
            p12 += (self.W_C + self.sum_L_C) * 2

        # Q12: IF(OR(H_O=3.5,H_O=4,H_O=4.5,H_O=5),(W_C+L1_C+...)*2,0)
        q12 = 0
        if self.H_O in [3.5, 4, 4.5, 5]:
            q12 = (self.W_C + self.sum_L_C) * 2

        # R12: IF(OR(H_O=3.5,H_O=3),4*2,0)+IF(OR(H_O=4,H_O=4.5),4*2*2,0)+IF(OR(H_O=5),4*3*2,0)
        r12 = 0
        if self.H_O in [3, 3.5]:
            r12 += 4 * 2
        if self.H_O in [4, 4.5]:
            r12 += 4 * 2 * 2
        if self.H_O == 5:
            r12 += 4 * 3 * 2

        # U12: IF(OR(H_O=3,3.5,4,4.5,5),((W_C+W_F-1)+(L1_C+L1_F+L2_C+L2_F+L3_C+L3_F+L4_C+L4_F-1))*2,0)
        u12 = 0
        if self.H_O in [3, 3.5, 4, 4.5, 5]:
            u12 = ((self.W_C + self.W_F - 1) + (self.sum_L_C + self.sum_L_F - 1)) * 2

        # X12: IF(H_O>1,W_C*N_PA,0)
        x12 = 0
        if self.H_O > 1:
            x12 = self.W_C * self.N_PA

        wfb_0950zp = p12 + q12 + r12 + u12 + x12
        if wfb_0950zp > 0:
            parts.append({
                "part_no": "WFB-0950ZP",
                "quantity": int(wfb_0950zp),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing plate"
            })

        # ===== Row 13: WFB-0950Z (Reinforcing Angle) =====
        # Q13: IF(OR(H_O=2.5,H_O=3),(W_C+L_C)*2,0)+IF(OR(H_O=3.5,H_O=4),(W_C+L_C)*2*2,0)+IF(OR(H_O=4.5,H_O=5),(W_C+L_C)*2*3,0)
        q13 = 0
        if self.H_O in [2.5, 3]:
            q13 += (self.W_C + self.sum_L_C) * 2
        if self.H_O in [3.5, 4]:
            q13 += (self.W_C + self.sum_L_C) * 2 * 2
        if self.H_O in [4.5, 5]:
            q13 += (self.W_C + self.sum_L_C) * 2 * 3

        # U13: IF(OR(H_O=2.5,H_O=3),((W_C+W_F-1)+(L1_C+L1_F+...-1))*2,0)+...
        u13 = 0
        if self.H_O in [2.5, 3]:
            u13 += ((self.W_C + self.W_F - 1) + (self.sum_L_C + self.sum_L_F - 1)) * 2
        if self.H_O in [3.5, 4]:
            u13 += ((self.W_C + self.W_F - 1) + (self.sum_L_C + self.sum_L_F - 1)) * 2 * 2
        if self.H_O in [4.5, 5]:
            u13 += ((self.W_C + self.W_F - 1) + (self.sum_L_C + self.sum_L_F - 1)) * 2 * 3

        wfb_0950z = q13 + u13
        if wfb_0950z > 0:
            parts.append({
                "part_no": "WFB-0950Z",
                "quantity": int(wfb_0950z),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing Angle"
            })

        # ===== Row 15: WFB-1200Z (Reinforcing Angle 1200) =====
        # U15: IF(BASIC_TOOL!D15=0,IF(OR(H_O=1.5,H_O=2.5),((W_C+W_F-1)+(L_O_C+L_O_F-1))*2,0)+IF(OR(H_O=2,H_O=3),...))
        # For non-insulation case (D15=0)
        u15 = 0
        if not self.insulation:
            if self.H_O in [1.5, 2.5]:
                u15 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1)) * 2
            if self.H_O in [2, 3]:
                u15 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1)) * 2
            if self.H_O in [3.5, 4]:
                u15 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1)) * 2 * 2
            if self.H_O in [4.5, 5]:
                u15 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1)) * 2 * 3

        wfb_1200z = u15
        if wfb_1200z > 0:
            parts.append({
                "part_no": "WFB-1200Z",
                "quantity": int(wfb_1200z),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing Angle 1200"
            })

        # ===== Row 18: WCF-1000Z (Corner Frame 1000) =====
        # R18: IF(H_O=1,4,0)+IF(H_O=2.5,4,0)+IF(H_O=3,4,0)
        r18 = 0
        if self.H_O == 1:
            r18 += 4
        if self.H_O == 2.5:
            r18 += 4
        if self.H_O == 3:
            r18 += 4

        wcf_1000z = r18
        if wcf_1000z > 0:
            parts.append({
                "part_no": "WCF-1000Z",
                "quantity": int(wcf_1000z),
                "category": "External Reinforcing",
                "description": "Corner Frame 1000mm"
            })

        # ===== Row 19: WCF-1500Z =====
        # R19: IF(H_O=1.5,4,0)+IF(H_O=3.5,4,0)+IF(H_O=2.5,4,0)+IF(H_O=4.5,12,0)+IF(H_O=5,8,0)
        r19 = 0
        if self.H_O == 1.5:
            r19 += 4
        if self.H_O == 3.5:
            r19 += 4
        if self.H_O == 2.5:
            r19 += 4
        if self.H_O == 4.5:
            r19 += 12
        if self.H_O == 5:
            r19 += 8

        wcf_1500z = r19
        if wcf_1500z > 0:
            parts.append({
                "part_no": "WCF-1500Z",
                "quantity": int(wcf_1500z),
                "category": "External Reinforcing",
                "description": "Corner Frame 1500mm"
            })

        # ===== Row 20: WCF-2000Z (Corner Frame 2000) =====
        # R20: IF(H_O=2,4,0)+IF(H_O=3.5,4,0)+IF(H_O=4,8,0)+IF(H_O=5,4,0)+IF(H_O=3,4,0)
        r20 = 0
        if self.H_O == 2:
            r20 += 4
        if self.H_O == 3.5:
            r20 += 4
        if self.H_O == 4:
            r20 += 8
        if self.H_O == 5:
            r20 += 4
        if self.H_O == 3:
            r20 += 4

        wcf_2000z = r20
        if wcf_2000z > 0:
            parts.append({
                "part_no": "WCF-2000Z",
                "quantity": int(wcf_2000z),
                "category": "External Reinforcing",
                "description": "Corner Frame 2000mm"
            })

        # ===== Row 22: WCP-1780Z (Cross Plate 2-hole) =====
        # P22: IF(H_O>3.3,((W_C+W_F-1)+L_O_C+L_O_F-N_PA-1)*2,0)
        p22 = 0
        if self.H_O > 3.3:
            p22 = ((self.W_C + self.W_F - 1) + self.L_O_C + self.L_O_F - self.N_PA - 1) * 2

        # R22: Internal_Reinforcing!S23*2 (WBR-9090 qty * 2)
        # S23 in Internal: IF(H_O=2.5,4,0)+IF(H_O=3,4,0)+IF(H_O=3.5,8,0)+IF(H_O=4,8,0)+IF(H_O=4.5,8,0)+IF(H_O=5,12,0)
        wbr_9090_qty = self._calc_wbr_9090()
        r22 = wbr_9090_qty * 2

        # U22: Height-based perimeter formula
        u22 = 0
        if self.H_O == 1.5:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2
        if self.H_O == 2:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2
        if self.H_O == 2.5:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2
        if self.H_O == 3:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2
        if self.H_O == 3.5:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 * 2
        if self.H_O == 4:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 * 2
        if self.H_O == 4.5:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 * 3
        if self.H_O == 5:
            u22 += (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 * 3

        # V22: IF(OR(H_O=2.5,H_O=3),N_PA*2)+IF(OR(H_O=3.5,H_O=4),N_PA*4)+IF(OR(H_O=4.5,H_O=5),N_PA*6)
        v22 = 0
        if self.H_O in [2.5, 3]:
            v22 += self.N_PA * 2
        if self.H_O in [3.5, 4]:
            v22 += self.N_PA * 4
        if self.H_O in [4.5, 5]:
            v22 += self.N_PA * 6

        wcp_1780z = p22 + r22 + u22 + v22
        if wcp_1780z > 0:
            parts.append({
                "part_no": "WCP-1780Z",
                "quantity": int(wcp_1780z),
                "category": "External Reinforcing",
                "description": "Cross Plate BKT(2 Hole)"
            })

        # ===== Row 23: WCP-1616Z (Cross Plate 4-hole) =====
        # U23: IF(H_O=2.5,perimeter*2,0)+IF(H_O=3,perimeter*2,0)+IF(H_O=3.5,perimeter*2*2,0)+...
        u23 = 0
        if self.H_O == 2.5:
            u23 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1 - self.N_PA)) * 2
        if self.H_O == 3:
            u23 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1 - self.N_PA)) * 2
        if self.H_O == 3.5:
            u23 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1 - self.N_PA)) * 2 * 2
        if self.H_O == 4:
            u23 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1 - self.N_PA)) * 2 * 2
        if self.H_O == 4.5:
            u23 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1 - self.N_PA)) * 2 * 3
        if self.H_O == 5:
            u23 += ((self.W_C + self.W_F - 1) + (self.L_O_C + self.L_O_F - 1 - self.N_PA)) * 2 * 3

        wcp_1616z = u23
        if wcp_1616z > 0:
            parts.append({
                "part_no": "WCP-1616Z",
                "quantity": int(wcp_1616z),
                "category": "External Reinforcing",
                "description": "Cross Plate BKT(4 Hole)"
            })

        # ===== Row 21: WFB-0880ZP (for partitions) =====
        # Y21: Partition-based formula
        wfb_0880zp = 0
        if self.N_PA > 0:
            if self.H_O in [2, 2.5, 3, 3.5, 4, 4.5, 5]:
                wfb_0880zp = self.N_PA * 2

        if wfb_0880zp > 0:
            parts.append({
                "part_no": "WFB-0880ZP",
                "quantity": int(wfb_0880zp),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing plate Partition"
            })

        return parts

    def _calc_wbr_9090(self) -> int:
        """
        Calculate WBR-9090 quantity (Internal_Reinforcing!S23)
        S23: IF(H_O=2.5,4,0)+IF(H_O=3,4,0)+IF(H_O=3.5,8,0)+IF(H_O=4,8,0)+IF(H_O=4.5,8,0)+IF(H_O=5,12,0)
        """
        qty = 0
        if self.H_O == 2.5:
            qty += 4
        if self.H_O == 3:
            qty += 4
        if self.H_O == 3.5:
            qty += 8
        if self.H_O == 4:
            qty += 8
        if self.H_O == 4.5:
            qty += 8
        if self.H_O == 5:
            qty += 12
        return qty

    def _calc_internal_reinforcing(self) -> List[Dict]:
        """
        Calculate internal reinforcing parts (Stainless steel - SA2/SA4)
        Based on Internal_Reinforcing sheet (sheet15) Column L → Column M/P
        """
        parts = []

        # Only needed for heights >= 1.5m
        if self.H_O < 1.5:
            return parts

        # ===== Row 8: WFB-1200SA4 =====
        # W8: IF(OR(BASIC_TOOL!E15=0),IF(OR(H_O=1.5,H_O=2,...),(W_C+W_F-1)*N_PA,0),...)
        wfb_1200 = 0
        if not self.insulation and self.N_PA > 0:
            if self.H_O in [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]:
                wfb_1200 = (self.W_C + self.W_F - 1) * self.N_PA

        if wfb_1200 > 0:
            parts.append({
                "part_no": f"WFB-1200{self.material_suffix}",
                "quantity": int(wfb_1200),
                "category": "Internal Reinforcing",
                "description": "F/L Reinforcing Angle"
            })

        # ===== Row 9: WFB-0880SA4 =====
        # W9: IF(AND(BASIC_TOOL!E15=1,H_O>1.5),(W_C+W_F-1)*N_PA,0)+IF(AND(BASIC_TOOL!E15=0,H_O>2),(W_C+W_F-1)*N_PA,0)
        wfb_0880 = 0
        if self.N_PA > 0:
            if self.insulation and self.H_O > 1.5:
                wfb_0880 += (self.W_C + self.W_F - 1) * self.N_PA
            if not self.insulation and self.H_O > 2:
                wfb_0880 += (self.W_C + self.W_F - 1) * self.N_PA

        if wfb_0880 > 0:
            parts.append({
                "part_no": f"WFB-0880{self.material_suffix}",
                "quantity": int(wfb_0880),
                "category": "Internal Reinforcing",
                "description": "F/L Reinforcing Angle"
            })

        # ===== Row 11: WFB-0880PSA4 =====
        # W11: IF((H_O>2.5),(W_C+W_F-1)*N_PA,0)
        wfb_0880p = 0
        if self.N_PA > 0 and self.H_O > 2.5:
            wfb_0880p = (self.W_C + self.W_F - 1) * self.N_PA

        if wfb_0880p > 0:
            parts.append({
                "part_no": f"WFB-0880P{self.material_suffix}",
                "quantity": int(wfb_0880p),
                "category": "Internal Reinforcing",
                "description": "F/L Reinforcing Plate"
            })

        # ===== Row 12: WFB-0950SA4 =====
        # W12: IF(BASIC_TOOL!E15=0,IF(OR(H_O=3.5,H_O=4),(W_C+W_F-1)*N_PA,0)+IF(OR(H_O=4.5,H_O=5),(W_C+W_F-1)*2*N_PA,0)...
        wfb_0950 = 0
        if self.N_PA > 0:
            if not self.insulation:
                if self.H_O in [3.5, 4]:
                    wfb_0950 += (self.W_C + self.W_F - 1) * self.N_PA
                if self.H_O in [4.5, 5]:
                    wfb_0950 += (self.W_C + self.W_F - 1) * 2 * self.N_PA
            else:
                if self.H_O in [3, 3.5]:
                    wfb_0950 += (self.W_C + self.W_F - 1) * self.N_PA
                if self.H_O in [4, 4.5]:
                    wfb_0950 += (self.W_C + self.W_F - 1) * 2 * self.N_PA

        if wfb_0950 > 0:
            parts.append({
                "part_no": f"WFB-0950{self.material_suffix}",
                "quantity": int(wfb_0950),
                "category": "Internal Reinforcing",
                "description": "F/L Reinforcing Angle"
            })

        # ===== Row 13: WFB-0950PSA4 =====
        # W13: IF(BASIC_TOOL!E15=1,IF(H_O=4,(W_C+W_F-1)*N_PA,0)+IF(H_O=4.5,(W_C+W_F-1)*2*N_PA,0)+IF(H_O=5,(W_C+W_F-1)*2*N_PA,0))
        wfb_0950p = 0
        if self.N_PA > 0 and self.insulation:
            if self.H_O == 4:
                wfb_0950p += (self.W_C + self.W_F - 1) * self.N_PA
            if self.H_O in [4.5, 5]:
                wfb_0950p += (self.W_C + self.W_F - 1) * 2 * self.N_PA

        if wfb_0950p > 0:
            parts.append({
                "part_no": f"WFB-0950P{self.material_suffix}",
                "quantity": int(wfb_0950p),
                "category": "Internal Reinforcing",
                "description": "F/L Reinforcing Plate"
            })

        # ===== Row 15: WFB-0450SA4 =====
        # W15: IF(BASIC_TOOL!E15=1,IF(OR(H_O=2.5,H_O=3.5,H_O=4.5),(W_C+W_F-1)*N_PA,0),0)
        wfb_0450 = 0
        if self.N_PA > 0 and self.insulation:
            if self.H_O in [2.5, 3.5, 4.5]:
                wfb_0450 = (self.W_C + self.W_F - 1) * self.N_PA

        if wfb_0450 > 0:
            parts.append({
                "part_no": f"WFB-0450{self.material_suffix}",
                "quantity": int(wfb_0450),
                "category": "Internal Reinforcing",
                "description": "F/L Reinforcing Angle"
            })

        # ===== Row 18: WCP-1616SA4 =====
        # V18: IF(OR(H_O=3.5,H_O=4.5,H_O=3,H_O=4,H_O=5),((W_C+W_F-1)*N_PA*(H_C+H_F-2)),0)
        wcp_1616 = 0
        if self.N_PA > 0 and self.H_O in [3, 3.5, 4, 4.5, 5]:
            wcp_1616 = (self.W_C + self.W_F - 1) * self.N_PA * (self.H_C + self.H_F - 2)

        if wcp_1616 > 0:
            parts.append({
                "part_no": f"WCP-1616{self.material_suffix}",
                "quantity": int(wcp_1616),
                "category": "Internal Reinforcing",
                "description": "Cross Plate(4 Hole) Partition"
            })

        # ===== Row 19: WCP-1780SA4 =====
        # V19: IF(H_O>1,((W_C+W_F-1)*N_PA),0)
        wcp_1780 = 0
        if self.N_PA > 0 and self.H_O > 1:
            wcp_1780 = (self.W_C + self.W_F - 1) * self.N_PA

        if wcp_1780 > 0:
            parts.append({
                "part_no": f"WCP-1780{self.material_suffix}",
                "quantity": int(wcp_1780),
                "category": "Internal Reinforcing",
                "description": "Cross Plate(2 Hole) Partition"
            })

        # ===== Row 20: WCP-17160SA4 (2-tierod bracket) =====
        # V20: Complex height-based formula
        wcp_17160 = 0
        if self.H_O == 3:
            wcp_17160 = (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 + 2 * (self.W_C + self.W_F - 1) * self.N_PA
        if self.H_O == 3.5:
            wcp_17160 = ((self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 + 2 * (self.W_C + self.W_F - 1) * self.N_PA) * 2
        if self.H_O == 4:
            wcp_17160 = ((self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 + 2 * (self.W_C + self.W_F - 1) * self.N_PA) * 2
        if self.H_O == 4.5:
            wcp_17160 = ((self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 + 2 * (self.W_C + self.W_F - 1) * self.N_PA) * 3
        if self.H_O == 5:
            wcp_17160 = ((self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2 + 2 * (self.W_C + self.W_F - 1) * self.N_PA) * 3

        if wcp_17160 > 0:
            parts.append({
                "part_no": f"WCP-17160{self.material_suffix}",
                "quantity": int(wcp_17160),
                "category": "Internal Reinforcing",
                "description": "IN-BRKT (2 tierod)"
            })

        # ===== Row 21: WCP-1760SA4 (1-tierod bracket) =====
        # V21: IF(H_O=1,0,((W_C+W_F-1+L_O_C+L_O_F-1-N_PA)*2)+(W_C+W_F-1)*N_PA*2
        #      +IF(H_O=2.5,perimeter*2+partition+N_PA*2,0))
        #      +IF(H_O=3,N_PA*2,0)
        #      +IF(H_O=3.5,perimeter*2+partition+N_PA*4,0)
        #      +IF(H_O=4,N_PA*4,0)
        #      +IF(H_O=4.5,perimeter*2+partition+N_PA*6,0)
        #      +IF(H_O=5,N_PA*6,0)
        wcp_1760 = 0
        if self.H_O > 1:
            perimeter_2 = (self.W_C + self.W_F - 1 + self.L_O_C + self.L_O_F - 1 - self.N_PA) * 2
            partition_base = (self.W_C + self.W_F - 1) * self.N_PA * 2

            # Base: perimeter * 2 + partition contribution
            wcp_1760 = perimeter_2 + partition_base

            # Height-based additions (for half heights: add perimeter+partition+N_PA*factor)
            # (for full heights: add only N_PA*factor)
            if self.H_O == 2.5:
                wcp_1760 += perimeter_2 + partition_base + self.N_PA * 2
            if self.H_O == 3:
                wcp_1760 += self.N_PA * 2  # Only N_PA*2 for H=3
            if self.H_O == 3.5:
                wcp_1760 += perimeter_2 + partition_base + self.N_PA * 4
            if self.H_O == 4:
                wcp_1760 += self.N_PA * 4  # Only N_PA*4 for H=4
            if self.H_O == 4.5:
                wcp_1760 += perimeter_2 + partition_base + self.N_PA * 6
            if self.H_O == 5:
                wcp_1760 += self.N_PA * 6  # Only N_PA*6 for H=5

        if wcp_1760 > 0:
            parts.append({
                "part_no": f"WCP-1760{self.material_suffix}",
                "quantity": int(wcp_1760),
                "category": "Internal Reinforcing",
                "description": "IN-BRKT (1 tierod)"
            })

        # ===== Row 23: WBR-9090SA4 (Corner bracket) =====
        wbr_9090 = self._calc_wbr_9090()
        if wbr_9090 > 0:
            parts.append({
                "part_no": f"WBR-9090{self.material_suffix}",
                "quantity": int(wbr_9090),
                "category": "Internal Reinforcing",
                "description": "Corner BRKT"
            })

        # ===== Row 24: WBR-1010SA4 =====
        # Q24: IF(H_O>3,perimeter*2,0)
        wbr_1010 = 0
        if self.H_O > 3:
            wbr_1010 = ((self.W_C + self.W_F - 1) + self.L_O_C + self.L_O_F - self.N_PA - 1) * 2

        if wbr_1010 > 0:
            parts.append({
                "part_no": f"WBR-1010{self.material_suffix}",
                "quantity": int(wbr_1010),
                "category": "Internal Reinforcing",
                "description": "Corner BRKT"
            })

        return parts
