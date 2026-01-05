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
        # Excel: (W_C+W_F+1)*2*IF(BASIC_TOOL!D23=5,0,1)
        main_beam_qty = int((self.W_C + self.W_F + 1) * 2)
        parts.append({
            "part_no": main_connector,
            "quantity": main_beam_qty,
            "category": "Steel Skid",
            "description": "Steel Skid Connector"
        })

        # ===== Steel Skid Main-L (Long frames along length) =====
        # Excel WFF-1990: ((IF(L_O_F>0,QUOTIENT(L_O-1.5,2),L_O_C/2)))*(W_C+W_F+1)
        if self.L_O_F > 0:
            frame_1990_qty = int((self.L_O - 1.5) // 2) * int(self.W_C + self.W_F + 1)
        else:
            frame_1990_qty = int(self.L_O_C / 2) * int(self.W_C + self.W_F + 1)
        if frame_1990_qty > 0:
            parts.append({
                "part_no": f"WFF-1990{type_suffix}Z",
                "quantity": frame_1990_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-L)"
            })

        # Excel WFF-0990: ((IF(L1_F>0,MOD(L1_O-1.5,2),MOD(L1_C,2))+...))*(W_C+W_F+1)
        frame_990_qty = self._calc_frame_990_qty()
        if frame_990_qty > 0:
            parts.append({
                "part_no": f"WFF-0990{type_suffix}Z",
                "quantity": frame_990_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-L)"
            })

        # ===== Steel Skid Main-W (Width frames) =====
        # These depend on width configuration using ISEVEN/ISODD
        width_frames = self._calc_width_frames(short_suffix)
        parts.extend(width_frames)

        # ===== Steel Skid Sub (Sub frames) =====
        sub_frames = self._calc_sub_frames()
        parts.extend(sub_frames)

        # ===== Cross Beam Connector =====
        # Excel: ((SUM(M14:M27)/2)-1)*2 where M14:M27 are sub-frame quantities
        # Sum of sub-frames divided by 2, minus 1, times 2
        sub_frame_total = sum(p.get('quantity', 0) for p in sub_frames)
        cross_beam_qty = int(((sub_frame_total / 2) - 1) * 2)
        if cross_beam_qty > 0:
            parts.append({
                "part_no": cross_connector,
                "quantity": cross_beam_qty,
                "category": "Steel Skid",
                "description": "Steel Skid Connector"
            })

        # ===== Liner =====
        # Excel: (ROUNDUP((W_C+W_F+1)*(CEILING(L1_O,1)+CEILING(L2_O,1)+CEILING(L3_O,1)+CEILING(L4_O,1)+1)*4.6,0))
        liner_qty = self._calc_liner_qty()
        if liner_qty > 0:
            parts.append({
                "part_no": "LNR-3.0T",
                "quantity": liner_qty,
                "category": "Steel Skid",
                "description": "Liner"
            })

        # ===== Anchor Bracket =====
        # Excel: (IF(H_O>3,4+(W_C+W_F-1)*2+(L_O-1)*2,4+(W_C+W_F-2)+(L_O-2)))
        if self.H_O > 3:
            anchor_qty = int(4 + (self.W_C + self.W_F - 1) * 2 + (self.L_O - 1) * 2)
        else:
            anchor_qty = int(4 + (self.W_C + self.W_F - 2) + (self.L_O - 2))
        if anchor_qty > 0:
            parts.append({
                "part_no": "WBR-5010Z",
                "quantity": anchor_qty,
                "category": "Steel Skid",
                "description": "Anchor Bracket with bolt and nut set"
            })

        return [p for p in parts if p.get('quantity', 0) > 0]

    def _calc_frame_990_qty(self) -> int:
        """
        Calculate WFF-0990 quantity (1m Main-L frames).
        Excel: ((IF(L1_F>0,MOD(L1_O-1.5,2),MOD(L1_C,2))+
                 IF(L2_F>0,MOD(L2_O-1.5,2),MOD(L2_C,2))+
                 IF(L3_F>0,MOD(L3_O-1.5,2),MOD(L3_C,2))+
                 IF(L4_F>0,MOD(L4_O-1.5,2),MOD(L4_C,2)))*(W_C+W_F+1))
        """
        mod_sum = 0

        # Section 1
        if self.L1_F > 0:
            mod_sum += (self.L1_O - 1.5) % 2
        else:
            mod_sum += self.L1_C % 2

        # Section 2
        if self.L2_F > 0:
            mod_sum += (self.L2_O - 1.5) % 2
        elif self.L2_C > 0:
            mod_sum += self.L2_C % 2

        # Section 3
        if self.L3_F > 0:
            mod_sum += (self.L3_O - 1.5) % 2
        elif self.L3_C > 0:
            mod_sum += self.L3_C % 2

        # Section 4
        if self.L4_F > 0:
            mod_sum += (self.L4_O - 1.5) % 2
        elif self.L4_C > 0:
            mod_sum += self.L4_C % 2

        return int(mod_sum * (self.W_C + self.W_F + 1))

    def _calc_width_frames(self, short_suffix: str) -> List[Dict]:
        """
        Calculate width frame parts (Main-W) using exact Excel ISEVEN/ISODD formulas.

        Excel formulas:
        ISEVEN: (IF(OR(W_O=3.5),1,0)+IF(W_O>3.5,IF(W_F=0,IF(ISEVEN(W_O),2,0),0))+IF(W_O>3.5,IF(W_F=1,IF(ISEVEN(W_O-1.5),2,0),0)))
        ISODD: (IF(W_O=3,2,IF(W_O=3.5,1,0))+IF(W_F=0,IF(W_O>3.5,IF(ISODD(W_O),2,0),0),0)+IF(W_F=1,IF(W_O>3.5,IF(ISODD(W_O-1.5),2,0),0),0))
        Center: (IF(W_F=0,IF(W_O>3.5,IF(ISEVEN(W_O),(W_O-4)/2*2,(W_O-3)/2*2),0),0)+IF(W_F=1,IF(W_O>4,IF(ISEVEN(W_O-1.5),(W_O-1.5-4)/2*2,(W_O-1.5-3)/2*2),0),0))
        Half frame: IF(W_O>3.5,IF(W_F=1,2,0),0)
        """
        parts = []

        # Helper: check W_F == 0.5 (Excel uses W_F=1 for half meter)
        w_f_is_half = (self.W_F == 0.5)

        # ===== Width Frame with ISEVEN =====
        # (IF(OR(W_O=3.5),1,0)+IF(W_O>3.5,IF(W_F=0,IF(ISEVEN(W_O),2,0),0))+IF(W_O>3.5,IF(W_F=1,IF(ISEVEN(W_O-1.5),2,0),0)))
        iseven_qty = 0
        if self.W_O == 3.5:
            iseven_qty = 1
        if self.W_O > 3.5:
            if not w_f_is_half:  # W_F = 0
                if int(self.W_O) % 2 == 0:  # ISEVEN(W_O)
                    iseven_qty += 2
            else:  # W_F = 0.5 (Excel W_F=1)
                if int(self.W_O - 0.5) % 2 == 0:  # ISEVEN(W_O-1.5) -> W_O-0.5 in our terms
                    iseven_qty += 2

        # ===== Width Frame with ISODD =====
        # (IF(W_O=3,2,IF(W_O=3.5,1,0))+IF(W_F=0,IF(W_O>3.5,IF(ISODD(W_O),2,0),0),0)+IF(W_F=1,IF(W_O>3.5,IF(ISODD(W_O-1.5),2,0),0),0))
        isodd_qty = 0
        if self.W_O == 3:
            isodd_qty = 2
        elif self.W_O == 3.5:
            isodd_qty = 1
        if self.W_O > 3.5:
            if not w_f_is_half:  # W_F = 0
                if int(self.W_O) % 2 == 1:  # ISODD(W_O)
                    isodd_qty += 2
            else:  # W_F = 0.5
                if int(self.W_O - 0.5) % 2 == 1:  # ISODD(W_O-1.5)
                    isodd_qty += 2

        # ===== Center Channel Bars =====
        # (IF(W_F=0,IF(W_O>3.5,IF(ISEVEN(W_O),(W_O-4)/2*2,(W_O-3)/2*2),0),0)+
        #  IF(W_F=1,IF(W_O>4,IF(ISEVEN(W_O-1.5),(W_O-1.5-4)/2*2,(W_O-1.5-3)/2*2),0),0))
        center_qty = 0
        if not w_f_is_half:  # W_F = 0
            if self.W_O > 3.5:
                if int(self.W_O) % 2 == 0:  # ISEVEN
                    center_qty = int((self.W_O - 4) / 2 * 2)
                else:
                    center_qty = int((self.W_O - 3) / 2 * 2)
        else:  # W_F = 0.5 (Excel W_F=1)
            if self.W_O > 4:
                w_adj = self.W_O - 0.5  # W_O - 1.5 in Excel terms
                if int(w_adj) % 2 == 0:  # ISEVEN
                    center_qty = int((w_adj - 4) / 2 * 2)
                else:
                    center_qty = int((w_adj - 3) / 2 * 2)

        # ===== Half Width Frame =====
        # IF(W_O>3.5,IF(W_F=1,2,0),0)
        half_qty = 0
        if self.W_O > 3.5 and w_f_is_half:
            half_qty = 2

        # ===== Small Width Frames (W <= 3.5) =====
        # IF(W_O=1,2,0), IF(W_O=1.5,2,0), IF(W_O=2,2,0), IF(W_O=2.5,2,0)
        small_width_qty = 0
        if self.W_O == 1:
            small_width_qty = 2
        elif self.W_O == 1.5:
            small_width_qty = 2
        elif self.W_O == 2:
            small_width_qty = 2
        elif self.W_O == 2.5:
            small_width_qty = 2

        # Build parts list based on quantities
        # Frame types: ISEVEN goes to one part, ISODD to another, center to main

        # For W >= 3, add the main width frames
        if self.W_O >= 3:
            # Main center frame (2000mm)
            if isodd_qty > 0:
                parts.append({
                    "part_no": f"WFF-2000{short_suffix}Z",
                    "quantity": isodd_qty,
                    "category": "Steel Skid",
                    "description": "Steel Skid(Main-W)"
                })

            # Side frames (Right/Left) based on ISEVEN
            if iseven_qty > 0:
                # Determine side width based on skid type
                if self.actual_skid_type == "75_angle":
                    side_width = 1570
                else:
                    side_width = 1560

                parts.append({
                    "part_no": f"WFF-{side_width}{short_suffix}ZR",
                    "quantity": iseven_qty,
                    "category": "Steel Skid",
                    "description": "Steel Skid(Main-W)"
                })
                parts.append({
                    "part_no": f"WFF-{side_width}{short_suffix}ZL",
                    "quantity": iseven_qty,
                    "category": "Steel Skid",
                    "description": "Steel Skid(Main-W)"
                })

            # Center channel bars
            if center_qty > 0:
                parts.append({
                    "part_no": f"WFF-2000{short_suffix}Z",
                    "quantity": center_qty,
                    "category": "Steel Skid",
                    "description": "Steel Skid(Main-W) Center"
                })

            # Half width frame
            if half_qty > 0:
                parts.append({
                    "part_no": f"WFF-0500{short_suffix}Z",
                    "quantity": half_qty,
                    "category": "Steel Skid",
                    "description": "Steel Skid(Main-W) Half"
                })
        elif small_width_qty > 0:
            # Small tanks (W < 3)
            parts.append({
                "part_no": f"WFF-2000{short_suffix}Z",
                "quantity": small_width_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Main-W)"
            })

        return parts

    def _calc_sub_frames(self) -> List[Dict]:
        """
        Calculate sub frame parts using exact Excel formulas.

        Excel formulas (sheet12):
        - Sub-frame based on width (W>=3.5):
          (IF(W_O>=3.5,(ROUND(W_O,0)-3),0)*(CEILING(L1_O,1)+CEILING(L2_O,1)+CEILING(L3_O,1)+CEILING(L4_O,1)-1))
        - Side sub-frame (W>=2.5):
          (IF(W_O=1.5,1,IF(W_O=2,1,IF(W_O>=2.5,2,0)))*(CEILING(L1_O,1)+...)-1))
        - Corner sub-frame (W>=3, integer):
          (IF(W_O>=3,IF(INT(W_O)=W_O,1,0),0)*(CEILING(L1_O,1)+...)-1))
        """
        parts = []

        # Calculate total ceiling length (used in all sub-frame formulas)
        total_ceiling_length = (math.ceil(self.L1_O) + math.ceil(self.L2_O) +
                                math.ceil(self.L3_O) + math.ceil(self.L4_O))
        length_factor = total_ceiling_length - 1

        # Helper: check if W_O is integer
        w_is_integer = (int(self.W_O) == self.W_O)

        # ===== Main Sub-frame (W >= 3.5) =====
        # (IF(W_O>=3.5,(ROUND(W_O,0)-3),0)*(CEILING(L1_O,1)+...)-1))
        main_sub_qty = 0
        if self.W_O >= 3.5:
            main_sub_qty = int((round(self.W_O) - 3) * length_factor)

        # ===== Side Sub-frame (based on width) =====
        # (IF(W_O=1.5,1,IF(W_O=2,1,IF(W_O>=2.5,2,0)))*(CEILING(L1_O,1)+...)-1))
        side_sub_qty = 0
        if self.W_O == 1.5:
            side_sub_qty = 1 * length_factor
        elif self.W_O == 2:
            side_sub_qty = 1 * length_factor
        elif self.W_O >= 2.5:
            side_sub_qty = 2 * length_factor

        # ===== Corner Sub-frame (W >= 3, integer width) =====
        # (IF(W_O>=3,IF(INT(W_O)=W_O,1,0),0)*(CEILING(L1_O,1)+...)-1))
        corner_sub_qty = 0
        if self.W_O >= 3 and w_is_integer:
            corner_sub_qty = 1 * length_factor

        # ===== Half-width Sub-frame (non-integer W >= 2.5) =====
        # (IF(INT(W_O)=W_O,0,IF(W_O>=2.5,1,0))*(CEILING(L1_O,1)+...)-1))
        half_sub_qty = 0
        if not w_is_integer and self.W_O >= 2.5:
            half_sub_qty = 1 * length_factor

        # Sub-frame part numbers vary by skid type
        if self.actual_skid_type == "75_angle":
            side_part = "WFF-0957AMZ"
            corner_part = "WFF-1063AMZ"
        else:  # 125_channel or 150_channel
            side_part = "WFF-0962AMZ"
            corner_part = "WFF-1053AMZ"

        # Add parts to list
        if main_sub_qty > 0:
            parts.append({
                "part_no": "WFF-0994AMZ",
                "quantity": main_sub_qty,
                "category": "Steel Skid",
                "description": "Steel Skid(Sub)"
            })

        if side_sub_qty > 0:
            parts.append({
                "part_no": side_part,
                "quantity": int(side_sub_qty),
                "category": "Steel Skid",
                "description": "Steel Skid(Sub)"
            })

        if corner_sub_qty > 0:
            parts.append({
                "part_no": corner_part,
                "quantity": int(corner_sub_qty),
                "category": "Steel Skid",
                "description": "Steel Skid(Sub)"
            })

        if half_sub_qty > 0:
            parts.append({
                "part_no": "WFF-0500AMZ",
                "quantity": int(half_sub_qty),
                "category": "Steel Skid",
                "description": "Steel Skid(Sub) Half"
            })

        return parts

    def _calc_liner_qty(self) -> int:
        """
        Calculate liner quantity using exact Excel formula.

        Excel: (ROUNDUP((W_C+W_F+1)*(CEILING(L1_O,1)+CEILING(L2_O,1)+CEILING(L3_O,1)+CEILING(L4_O,1)+1)*4.6,0))

        Factor = 4.6 is constant!
        """
        # Calculate total ceiling length
        total_ceiling_length = (math.ceil(self.L1_O) + math.ceil(self.L2_O) +
                                math.ceil(self.L3_O) + math.ceil(self.L4_O))

        # Excel formula: (W_C+W_F+1) * (total_ceiling_length + 1) * 4.6
        liner_qty = math.ceil((self.W_C + self.W_F + 1) * (total_ceiling_length + 1) * 4.6)
        return liner_qty
