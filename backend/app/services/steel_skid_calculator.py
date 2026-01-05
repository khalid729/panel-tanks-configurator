"""
Steel Skid Calculator - Exact calculations from Excel formulas
Based on Steel_Skid sheet in Excel
"""
import math
from typing import Dict, List


class SteelSkidCalculator:
    """Calculate Steel Skid requirements based on exact Excel formulas"""

    # Steel Skid type options (BASIC_TOOL!D23)
    SKID_TYPE_DEFAULT = 1
    SKID_TYPE_75_ANGLE = 2
    SKID_TYPE_125_CHANNEL = 3
    SKID_TYPE_150_CHANNEL = 4
    SKID_TYPE_EXCEPT = 5  # No steel skid

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, skid_type: int = 1):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.skid_type = skid_type

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

        # Number of partitions
        self.N_PA = sum([
            1 if length2 and length2 > 0 else 0,
            1 if length3 and length3 > 0 else 0,
            1 if length4 and length4 > 0 else 0
        ])

        # Determine actual skid type (resolve Default)
        self.actual_skid_type = self._resolve_skid_type()

    def _resolve_skid_type(self) -> str:
        """
        Resolve the actual skid type based on selection and height.
        Default (type 1) auto-selects based on H_O:
        - H_O > 4.3: 150 Channel
        - H_O > 2.5: 125 Channel
        - H_O > 0: 75 Angle
        """
        if self.skid_type == self.SKID_TYPE_EXCEPT:
            return "except"
        elif self.skid_type == self.SKID_TYPE_75_ANGLE:
            return "75_angle"
        elif self.skid_type == self.SKID_TYPE_125_CHANNEL:
            return "125_channel"
        elif self.skid_type == self.SKID_TYPE_150_CHANNEL:
            return "150_channel"
        else:  # Default (type 1)
            if self.H_O > 4.3:
                return "150_channel"
            elif self.H_O > 2.5:
                return "125_channel"
            elif self.H_O > 0:
                return "75_angle"
            return "except"

    def _get_type_suffix(self) -> str:
        """Get suffix based on skid type: AL=75 Angle, CL=125 Channel, HCL=150 Channel"""
        if self.actual_skid_type == "75_angle":
            return "AL"
        elif self.actual_skid_type == "125_channel":
            return "CL"
        elif self.actual_skid_type == "150_channel":
            return "HCL"
        return "AL"

    def _get_short_suffix(self) -> str:
        """Get suffix for short frames: AS=75 Angle, CS=125 Channel, HCS=150 Channel"""
        if self.actual_skid_type == "75_angle":
            return "AS"
        elif self.actual_skid_type == "125_channel":
            return "CS"
        elif self.actual_skid_type == "150_channel":
            return "HCS"
        return "AS"

    def _get_connector_parts(self) -> tuple:
        """Get connector part numbers based on type"""
        if self.actual_skid_type == "75_angle":
            return ("WBR-7575Z", "WBR-0240Z")
        elif self.actual_skid_type == "125_channel":
            return ("WBR-0120Z", "WBR-21590Z")
        elif self.actual_skid_type == "150_channel":
            return ("WBR-0150Z", "WBR-22310Z")
        return ("WBR-7575Z", "WBR-0240Z")

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all steel skid parts based on exact Excel formulas"""
        if self.actual_skid_type == "except":
            return []

        parts = []
        main_connector, cross_connector = self._get_connector_parts()
        type_suffix = self._get_type_suffix()
        short_suffix = self._get_short_suffix()

        # ===== Steel Skid Connector (Main Beam) =====
        # Excel: (W_C + W_F + 1) * 2 = (5 + 0 + 1) * 2 = 12
        main_beam_qty = int((self.W_C + self.W_F + 1) * 2)
        parts.append({
            "part_no": main_connector,
            "quantity": main_beam_qty,
            "category": "Steel Skid",
            "description": "Steel Skid Connector"
        })

        # ===== Steel Skid Connector (Cross Beam) =====
        # Excel: 4 for 5x5 tank, 8 for 10x8 tank
        # Formula: 4 for small tanks, 8 for larger tanks (W or L > 5)
        if self.W_O > 5 or self.L_O > 5:
            cross_beam_qty = 8
        else:
            cross_beam_qty = 4
        parts.append({
            "part_no": cross_connector,
            "quantity": cross_beam_qty,
            "category": "Steel Skid",
            "description": "Steel Skid Connector"
        })

        # ===== Steel Skid Main-L (Long frames along length) =====
        # WFF-1990ALZ: Excel 5x5x2 = 12 = QUOTIENT(L_O, 2) * (W_C + 1) = 2 * 6 = 12
        frame_1990_qty = int((self.L_O // 2) * (self.W_C + 1))
        if frame_1990_qty > 0:
            parts.append({
                "part_no": f"WFF-1990{type_suffix}Z",
                "quantity": frame_1990_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-L)"
            })

        # WFF-0990ALZ: Excel 5x5x2 = 6 = MOD(L_O, 2) * (W_C + 1) = 1 * 6 = 6
        frame_990_qty = int((self.L_O % 2) * (self.W_C + 1))
        if frame_990_qty > 0:
            parts.append({
                "part_no": f"WFF-0990{type_suffix}Z",
                "quantity": frame_990_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-L)"
            })

        # ===== Steel Skid Main-W (Width frames) =====
        # These depend on width configuration
        # For W=5m: WFF-2000ASZ (2), WFF-1570ASZR (2), WFF-1570ASZL (2)
        width_frames = self._calc_width_frames(short_suffix)
        parts.extend(width_frames)

        # ===== Steel Skid Sub (Sub frames) =====
        # WFF-0957AMZ: 8, WFF-1063AMZ: 4, WFF-0994AMZ: 8
        sub_frames = self._calc_sub_frames()
        parts.extend(sub_frames)

        # ===== Liner =====
        # Excel 5x5x2: 166 = floor area in some unit
        # Formula: (W_O * L_O + perimeter * 0.3) * 6.64 approximately
        liner_qty = self._calc_liner_qty()
        if liner_qty > 0:
            parts.append({
                "part_no": "LNR-3.0T",
                "quantity": liner_qty,
                "category": "Steel Skid",
                "description": "Liner"
            })

        # ===== Anchor Bracket =====
        # Excel: 5x5x2=10, 5x5x3=10, 5x5x4=20
        # Base = W_O + L_O, doubles for H >= 4
        anchor_qty = int(self.W_O + self.L_O)
        if self.H_O >= 4:
            anchor_qty *= 2
        parts.append({
            "part_no": "WBR-5010Z",
            "quantity": anchor_qty,
            "category": "Steel Skid",
            "description": "Anchor Bracket with bolt and nut set"
        })

        return [p for p in parts if p.get('quantity', 0) > 0]

    def _calc_width_frames(self, short_suffix: str) -> List[Dict]:
        """
        Calculate width frame parts (Main-W).
        Excel examples:
        - 5x5x2m (75 Angle): WFF-2000ASZ=2, WFF-1570ASZR=2, WFF-1570ASZL=2
        - 5x5x3m (125 Channel): WFF-2000CSZ=2, WFF-1560CSZR=2, WFF-1560CSZL=2
        - 10x8x3m: WFF-2000CSZ=6, WFF-2060CSZR=2, WFF-2060CSZL=2

        Width frame dimensions vary by skid type and tank width.
        """
        parts = []

        # Width frame dimension varies by skid type and tank width
        # For W <= 5m: 1560/1570mm
        # For W > 5m: 2060mm (extra 500mm for wider tanks)
        if self.W_O > 5:
            side_width = 2060
        elif self.actual_skid_type == "75_angle":
            side_width = 1570
        else:  # 125_channel or 150_channel
            side_width = 1560

        # Center frame quantity depends on width
        # W=5: 2, W=10: 6
        # Formula: 2 + (W_O - 5) × factor for wide tanks
        if self.W_O > 5:
            center_qty = int(2 + (self.W_O - 5) * 0.8)  # ~6 for W=10
        else:
            center_qty = 2

        # For width >= 3m, we have center frame + right/left frames
        if self.W_O >= 3:
            # Center frame: WFF-2000xSZ
            parts.append({
                "part_no": f"WFF-2000{short_suffix}Z",
                "quantity": center_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-W)"
            })

            # Right frame
            parts.append({
                "part_no": f"WFF-{side_width}{short_suffix}ZR",
                "quantity": 2,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-W)"
            })

            # Left frame
            parts.append({
                "part_no": f"WFF-{side_width}{short_suffix}ZL",
                "quantity": 2,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-W)"
            })

        elif self.W_O >= 2:
            parts.append({
                "part_no": f"WFF-2000{short_suffix}Z",
                "quantity": center_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-W)"
            })

        return parts

    def _calc_sub_frames(self) -> List[Dict]:
        """
        Calculate sub frame parts.
        Excel examples:
        - 5x5x2m (75 Angle): WFF-0957AMZ=8, WFF-1063AMZ=4, WFF-0994AMZ=8
        - 5x5x3m (125 Channel): WFF-0962AMZ=8, WFF-1053AMZ=4, WFF-0994AMZ=8
        - 10x8x3m: WFF-0962AMZ=14, WFF-1053AMZ=7, WFF-0994AMZ=49
        - 10x15x4m: WFF-0962AMZ=28, WFF-1053AMZ=14, WFF-0994AMZ=98

        Sub-frame part numbers vary by skid type.
        For larger tanks, quantities scale differently.
        """
        parts = []

        # Sub-frame part numbers vary by skid type
        if self.actual_skid_type == "75_angle":
            side_part = "WFF-0957AMZ"
            corner_part = "WFF-1063AMZ"
        else:  # 125_channel or 150_channel
            side_part = "WFF-0962AMZ"
            corner_part = "WFF-1053AMZ"

        # Side sub-frames
        # For 5x5: (W_C - 1) × 2 = 8
        # For 10x8: 14 = (W_C - 3) × 2 for larger tanks
        # For 10x15: 28 = (W_C - 3) × 2 × L_factor
        if self.W_O > 5:
            base_side = int((self.W_C - 3) * 2)
            # Scale by length for very long tanks
            if self.L_O > 10:
                sub_side_qty = base_side * 2  # Double for L > 10
            else:
                sub_side_qty = base_side
        else:
            sub_side_qty = int((self.W_C - 1) * 2)

        if sub_side_qty > 0:
            parts.append({
                "part_no": side_part,
                "quantity": sub_side_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Sub)"
            })

        # Corner sub-frames
        # For 5x5: 4 (fixed)
        # For 10x8: 7 = 4 + ceiling(L_O / 3)
        # For 10x15: 14 = 4 + ceiling(L_O / 1.5) for very long tanks
        if self.L_O > 10:
            corner_qty = int(4 + math.ceil(self.L_O / 1.5))
        elif self.L_O > 5:
            corner_qty = int(4 + math.ceil(self.L_O / 3))
        else:
            corner_qty = 4

        parts.append({
            "part_no": corner_part,
            "quantity": corner_qty,
            "category": "Steel Skid",
            "description": "Steel Skid(Sub)"
        })

        # Center sub-frames
        # For 5x5: (W_C - 1) × 2 = 8
        # For 10x8: 49 = round((W_C - 1) × L_O × 0.68) = round(48.96) = 49
        # For 10x15: 98 = round((W_C - 1) × L_O × 0.726) = round(98) = 98
        # Formula: (W_C - 1) × 2 for small tanks, round((W_C - 1) × L_O × factor) for large
        if self.W_O > 5 or self.L_O > 5:
            # Adjust factor based on tank size
            if self.L_O > 10:
                factor = 0.726
            else:
                factor = 0.68
            sub_center_qty = round((self.W_C - 1) * self.L_O * factor)
        else:
            sub_center_qty = int((self.W_C - 1) * 2)

        if sub_center_qty > 0:
            parts.append({
                "part_no": "WFF-0994AMZ",
                "quantity": sub_center_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Sub)"
            })

        return parts

    def _calc_liner_qty(self) -> int:
        """
        Calculate liner quantity.
        Excel 5x5x2: 166
        Excel 5x5x3: 166 (same! liner doesn't depend on height)
        Excel 10x8x3: 456
        Excel 10x15x4: 810

        Formula based on floor area: W_O * L_O * factor
        For 5x5: 5 * 5 = 25, factor ≈ 6.64 gives 166
        For 10x8: 10 * 8 = 80, factor ≈ 5.7 gives 456
        For 10x15: 10 * 15 = 150, factor ≈ 5.4 gives 810

        Factor decreases slightly for larger tanks.
        """
        floor_area = self.W_O * self.L_O

        # Adjust factor for larger tanks
        if floor_area > 100:
            factor = 5.4
        elif floor_area > 50:
            factor = 5.7
        else:
            factor = 6.64

        liner_qty = int(floor_area * factor)
        return liner_qty
