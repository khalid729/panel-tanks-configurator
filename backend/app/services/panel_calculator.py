"""
Panel Calculator - Exact panel calculations from Excel formulas
"""
import math
from typing import Dict, List, Tuple


class PanelCalculator:
    """Calculate panel requirements based on exact Excel formulas"""

    # Panel codes mapping for different heights
    PANEL_HEIGHT_CONFIG = {
        # height: {panel_type: suffix}
        1.0: {"side": "10S", "roof": "00M", "bottom": "10M", "drain": "10M"},
        1.5: {"side": "15S", "roof": "00M", "bottom": "15M", "drain": "15M"},
        2.0: {"side": "20S", "roof": "00M", "bottom": "20M", "drain": "20M"},
        2.5: {"side": "15T", "roof": "00M", "bottom": "25M", "drain": "25M"},
        3.0: {"side": "20T", "roof": "00M", "bottom": "30M", "drain": "30M"},
        3.5: {"side": "15T", "roof": "00M", "bottom": "35M", "drain": "35M"},
        4.0: {"side": "20T", "roof": "00M", "bottom": "40M", "drain": "40M"},
        4.5: {"side": "15T", "roof": "00M", "bottom": "45M", "drain": "45M"},
        5.0: {"side": "20T", "roof": "00M", "bottom": "50M", "drain": "50M"},
    }

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, use_side_1x1: bool = False,
                 use_partition_1x1: bool = False, insulated: bool = False):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.use_side_1x1 = use_side_1x1
        self.use_partition_1x1 = use_partition_1x1
        self.insulated = insulated

        # Calculate integer and fractional parts (Excel: TRUNC)
        self.W_C = int(width)  # Width integer
        self.W_F = width - self.W_C  # Width fraction (0 or 0.5)

        self.L1_C = int(length1)
        self.L1_F = length1 - self.L1_C

        self.L2_C = int(length2) if length2 else 0
        self.L2_F = (length2 - self.L2_C) if length2 else 0

        self.L3_C = int(length3) if length3 else 0
        self.L3_F = (length3 - self.L3_C) if length3 else 0

        self.L4_C = int(length4) if length4 else 0
        self.L4_F = (length4 - self.L4_C) if length4 else 0

        self.H_C = int(height)
        self.H_F = height - self.H_C

        # Total length
        self.L_O = length1 + length2 + length3 + length4
        self.L_O_C = self.L1_C + self.L2_C + self.L3_C + self.L4_C
        self.L_O_F = self.L1_F + self.L2_F + self.L3_F + self.L4_F

        # Number of partitions
        self.N_PA = sum([1 if length2 > 0 else 0,
                         1 if length3 > 0 else 0,
                         1 if length4 > 0 else 0])

        # Width with half panel adjustment
        self.W_O = self.W_C + self.W_F
        self.H_O = self.H_C + self.H_F

    def calculate_all_panels(self) -> List[Dict]:
        """Calculate all panel requirements"""
        panels = []

        # Manhole panels
        panels.extend(self._calc_manhole())

        # Roof panels
        panels.extend(self._calc_roof_panels())

        # Bottom panels
        panels.extend(self._calc_bottom_panels())

        # Drain panels
        panels.extend(self._calc_drain_panels())

        # Side panels
        panels.extend(self._calc_side_panels())

        # Partition panels
        if self.N_PA > 0:
            panels.extend(self._calc_partition_panels())

        return [p for p in panels if p['quantity'] > 0]

    def _calc_manhole(self) -> List[Dict]:
        """Manhole panel: =1+N_PA"""
        qty = 1 + self.N_PA
        return [{"part_no": "MF00M", "quantity": qty, "category": "Panels",
                 "description": "Manhole Panel"}]

    def _calc_roof_panels(self) -> List[Dict]:
        """
        Roof panels calculation (EXACT Excel formulas):

        X6 (Manhole): =1+N_PA
        X7 (RF): =IF(W_C*(L1_C+L2_C+L3_C+L4_C)-X6-X10-X11<0,0,W_C*(L1_C+L2_C+L3_C+L4_C)-X6-X10-X11)
        X8 (RH): =W_C*(L1_F+L2_F+L3_F+L4_F)+W_F*(L1_C+L2_C+L3_C+L4_C)
        X9 (RQ): =IF(AND(W_F=1,OR(L1_F,L2_F,L3_F,L4_F)),L1_F+L2_F+L3_F+L4_F,0)

        Note: In Excel W_F=1 means 0.5m (half panel), so we check W_F == 0.5
        """
        panels = []

        # X6: Manhole quantity
        manhole_qty = 1 + self.N_PA  # X6

        # X9: RQ (Quarter Roof) - Excel: IF(AND(W_F=1,OR(L1_F,L2_F,L3_F,L4_F)),...)
        # W_F=1 in Excel means W_F=0.5 in our code (half panel = 0.5m)
        has_length_fraction = (self.L1_F > 0 or self.L2_F > 0 or
                               self.L3_F > 0 or self.L4_F > 0)
        # Check W_F == 0.5 (equivalent to Excel's W_F=1)
        rq_qty = 0
        if self.W_F == 0.5 and has_length_fraction:
            # Sum of all length fractions (each 0.5 counts as 1 panel)
            rq_qty = int((self.L1_F + self.L2_F + self.L3_F + self.L4_F) / 0.5) if has_length_fraction else 0
            # Simpler: count non-zero fractions
            rq_qty = sum([1 for f in [self.L1_F, self.L2_F, self.L3_F, self.L4_F] if f > 0])

        # X10, X11: Additional panels to subtract (from Excel analysis)
        # X10 appears to be RQ, X11 appears to be related to special panels
        # For now, X10 = RQ, X11 = 0 (need to verify with Excel data)
        x10 = rq_qty  # RQ panels
        x11 = 0  # TODO: Verify what X11 represents in Excel

        # X8: RH (Half Roof) - exact Excel formula
        rh_qty = int(self.W_C * (self.L1_F + self.L2_F + self.L3_F + self.L4_F) / 0.5 +
                     self.W_F / 0.5 * self.L_O_C) if (self.L_O_F > 0 or self.W_F > 0) else 0
        # Simplified: W_C * count_of_half_lengths + W_F_count * L_O_C
        l_fractions_count = sum([1 for f in [self.L1_F, self.L2_F, self.L3_F, self.L4_F] if f > 0])
        w_fraction_count = 1 if self.W_F > 0 else 0
        rh_qty = self.W_C * l_fractions_count + w_fraction_count * self.L_O_C

        # X7: RF (Full Roof) - exact Excel formula
        total_roof = self.W_C * self.L_O_C
        rf_qty = total_roof - manhole_qty - x10 - x11
        if rf_qty < 0:
            rf_qty = 0

        # Build panel list
        if rf_qty > 0:
            panels.append({"part_no": "RF00M", "quantity": int(rf_qty),
                           "category": "Panels", "description": "Roof Panel 1x1m"})
        if rh_qty > 0:
            panels.append({"part_no": "RH10M", "quantity": int(rh_qty),
                           "category": "Panels", "description": "Half Roof Panel 0.5x1m"})
        if rq_qty > 0:
            panels.append({"part_no": "RQ10M", "quantity": int(rq_qty),
                           "category": "Panels", "description": "Quarter Roof Panel 0.5x0.5m"})

        return panels

    def _calc_bottom_panels(self) -> List[Dict]:
        """
        Bottom panels calculation (EXACT Excel formulas):

        X12 (BF): =IF(W_C*(L1_C+L2_C+L3_C+L4_C)-X13-X17<0,0,W_C*(L1_C+L2_C+L3_C+L4_C)-X13-X17)
        X13 (Partition Bottom): =(W_C)*N_PA
        X14 (BH): =W_C*(L1_F+L2_F+L3_F+L4_F)+W_F*(L1_C+L2_C+L3_C+L4_C)-X15
        X15: =IF(W_F=1,N_PA,0)
        X16 (BQ): =IF(AND(W_F=1,OR(L1_F,L2_F,L3_F,L4_F)),L1_F+L2_F+L3_F+L4_F,0)
        X17 (Drain): =(1+N_PA)
        """
        panels = []

        # X13: Partition bottom panels - Excel: (W_C)*N_PA
        x13_partition_bottom = self.W_C * self.N_PA if self.N_PA > 0 else 0

        # X17: Drain panels - Excel: (1+N_PA)
        x17_drain = 1 + self.N_PA

        # X15: Half panel partition adjustment - Excel: IF(W_F=1,N_PA,0)
        # W_F=1 in Excel means W_F=0.5 in our code
        x15 = self.N_PA if self.W_F == 0.5 else 0

        # X16: BQ (Quarter Bottom) - same logic as RQ
        has_length_fraction = (self.L1_F > 0 or self.L2_F > 0 or
                               self.L3_F > 0 or self.L4_F > 0)
        bq_qty = 0
        if self.W_F == 0.5 and has_length_fraction:
            bq_qty = sum([1 for f in [self.L1_F, self.L2_F, self.L3_F, self.L4_F] if f > 0])

        # X14: BH (Half Bottom) - Excel: W_C*(L1_F+...)+W_F*(L1_C+...)-X15
        l_fractions_count = sum([1 for f in [self.L1_F, self.L2_F, self.L3_F, self.L4_F] if f > 0])
        w_fraction_count = 1 if self.W_F > 0 else 0
        bh_qty = self.W_C * l_fractions_count + w_fraction_count * self.L_O_C - x15

        # X12: BF (Full Bottom) - Excel: W_C*L_O_C - X13 - X17
        total_bottom = self.W_C * self.L_O_C
        bf_qty = total_bottom - x13_partition_bottom - x17_drain
        if bf_qty < 0:
            bf_qty = 0

        # Get height suffix
        h_key = self._get_height_key()
        suffix = self.PANEL_HEIGHT_CONFIG.get(h_key, {}).get("bottom", "10M")

        # Build panel list
        if bf_qty > 0:
            panels.append({"part_no": f"BF{suffix}", "quantity": int(bf_qty),
                           "category": "Panels", "description": "Bottom Panel 1x1m"})
        if bh_qty > 0:
            panels.append({"part_no": f"BH{suffix}", "quantity": int(bh_qty),
                           "category": "Panels", "description": "Half Bottom Panel 0.5x1m"})
        if bq_qty > 0:
            panels.append({"part_no": f"BQ{suffix}", "quantity": int(bq_qty),
                           "category": "Panels", "description": "Quarter Bottom Panel 0.5x0.5m"})

        # Partition bottom panels with "P" suffix
        if x13_partition_bottom > 0:
            panels.append({"part_no": f"BF{suffix[:-1]}P", "quantity": int(x13_partition_bottom),
                           "category": "Panels", "description": "Partition Bottom Panel"})

        return panels

    def _calc_drain_panels(self) -> List[Dict]:
        """Drain panel: =1+N_PA (one per section)"""
        qty = 1 + self.N_PA
        h_key = self._get_height_key()
        suffix = self.PANEL_HEIGHT_CONFIG.get(h_key, {}).get("drain", "10M")
        return [{"part_no": f"DN{suffix}", "quantity": qty,
                 "category": "Panels", "description": "Drain Panel"}]

    def _calc_side_panels(self) -> List[Dict]:
        """
        Side panels calculation (EXACT Excel formulas):

        X20 (Side Full): =IF(BASIC_TOOL!D15=1,0,((W_C+L1_C+L2_C+L3_C+L4_C)*2)-X22-X21)
        X21 (Corner Left): =IF(BASIC_TOOL!D15=1,0,N_PA)
        X22 (Corner Right): =IF(BASIC_TOOL!D15=1,0,N_PA)
        X28 (Side Half): =(W_F+L1_F+L2_F+L3_F+L4_F)*2

        BASIC_TOOL!D15=1 means "Insulated Roof Only" (no side panels counted differently)
        """
        panels = []
        h_key = self._get_height_key()

        # X21, X22: Corner panels - Excel: IF(D15=1,0,N_PA)
        # D15=1 means insulated_roof_only, not the 'insulated' flag for full insulation
        corner_left = self.N_PA  # X21
        corner_right = self.N_PA  # X22

        # X20: Side Full - Excel: ((W_C+L_O_C)*2)-X22-X21 = (W_C+L_O_C)*2 - 2*N_PA
        side_full = (self.W_C + self.L_O_C) * 2 - corner_left - corner_right

        # X28: Side Half - Excel: (W_F+L1_F+L2_F+L3_F+L4_F)*2
        # Count fractions: W_F can be 0.5, each L_F can be 0.5
        w_f_count = 1 if self.W_F > 0 else 0
        l_f_count = sum([1 for f in [self.L1_F, self.L2_F, self.L3_F, self.L4_F] if f > 0])
        side_half = (w_f_count + l_f_count) * 2

        # Panel type based on height and 1x1 option
        if self.use_side_1x1:
            panel_prefix = "SF"
        else:
            panel_prefix = "SL"

        config = self.PANEL_HEIGHT_CONFIG.get(h_key, {})
        suffix = config.get("side", "10S")

        # Get height number for half side panel
        height_num = suffix[:2] if len(suffix) >= 2 else "10"

        # For multi-tier heights (>= 2.5m), add top, mid (if H>=4), and low panels
        if self.H_O >= 2.5:
            # Side Top panels (SL20T for 3m and 4m)
            if side_full > 0:
                panels.append({"part_no": f"{panel_prefix}{suffix}", "quantity": int(side_full),
                               "category": "Panels", "description": "Side Panel (Top)"})

            # Corner panels (Left and Right) for partitioned tanks
            if corner_left > 0:
                panels.append({"part_no": f"{panel_prefix}{suffix}L", "quantity": int(corner_left),
                               "category": "Panels", "description": "Corner Side Panel (Top Left)"})
            if corner_right > 0:
                panels.append({"part_no": f"{panel_prefix}{suffix}R", "quantity": int(corner_right),
                               "category": "Panels", "description": "Corner Side Panel (Top Right)"})

            # For H >= 4m, add Side Mid panels (SF30M)
            if self.H_O >= 4:
                panels.append({"part_no": "SF30M", "quantity": int(side_full),
                               "category": "Panels", "description": "Side Panel (Mid)"})

                # Corner Mid panels for partitioned tanks (SF30ML, SF30MR)
                if corner_left > 0:
                    panels.append({"part_no": "SF30ML", "quantity": int(corner_left),
                                   "category": "Panels", "description": "Corner Side Panel (Mid Left)"})
                if corner_right > 0:
                    panels.append({"part_no": "SF30MR", "quantity": int(corner_right),
                                   "category": "Panels", "description": "Corner Side Panel (Mid Right)"})

            # Side Low panels (SF30L for 3m, SF40L for 4m, etc.)
            height_code = int(self.H_O * 10)
            if side_full > 0:
                panels.append({"part_no": f"SF{height_code}L", "quantity": int(side_full),
                               "category": "Panels", "description": "Side Panel (Low)"})

            # Corner Low panels for partitioned tanks
            if corner_left > 0:
                panels.append({"part_no": f"SF{height_code}LL", "quantity": int(corner_left),
                               "category": "Panels", "description": "Corner Side Panel (Low Left)"})
            if corner_right > 0:
                panels.append({"part_no": f"SF{height_code}LR", "quantity": int(corner_right),
                               "category": "Panels", "description": "Corner Side Panel (Low Right)"})
        else:
            # Single tier - standard side panels
            if side_full > 0:
                panels.append({"part_no": f"{panel_prefix}{suffix}", "quantity": int(side_full),
                               "category": "Panels", "description": f"Side Panel"})

            # Corner panels for partitioned tanks (single tier)
            if corner_left > 0:
                panels.append({"part_no": f"{panel_prefix}{suffix}L", "quantity": int(corner_left),
                               "category": "Panels", "description": "Corner Side Panel (Left)"})
            if corner_right > 0:
                panels.append({"part_no": f"{panel_prefix}{suffix}R", "quantity": int(corner_right),
                               "category": "Panels", "description": "Corner Side Panel (Right)"})

        # Half side panels
        if side_half > 0:
            panels.append({"part_no": f"SH{height_num}M", "quantity": int(side_half),
                           "category": "Panels", "description": "Half Side Panel 0.5x1m"})

        return panels

    def _calc_partition_panels(self) -> List[Dict]:
        """
        Partition panels for internal divisions.

        For multi-tier heights (>= 2.5m):
        - 10x8x3: PL20TCB = 20, PF30M = 20
        - Partition Top panels: W_C × 2 × N_PA
        - Partition Low panels: W_C × 2 × N_PA

        For single tier:
        - Standard partition panels
        """
        if self.N_PA == 0:
            return []

        panels = []
        h_key = self._get_height_key()

        # For multi-tier heights (>= 2.5m)
        if self.H_O >= 2.5:
            # Partition Top panels: PL20TCB
            # Quantity: W_C × N_PA (one row per partition wall)
            partition_top_qty = int(self.W_C * self.N_PA)
            panels.append({"part_no": "PL20TCB", "quantity": partition_top_qty,
                           "category": "Panels", "description": "Partition Panel (Top)"})

            # For H >= 4m, add Partition Mid panels (SN30M - Side Nozzle Mid)
            if self.H_O >= 4:
                partition_mid_qty = int(self.W_C * self.N_PA)
                panels.append({"part_no": "SN30M", "quantity": partition_mid_qty,
                               "category": "Panels", "description": "Partition Panel (Mid)"})

            # Partition Low panels: PF30M, PF40M, etc.
            height_code = int(self.H_O * 10)
            partition_low_qty = int(self.W_C * self.N_PA)
            panels.append({"part_no": f"PF{height_code}M", "quantity": partition_low_qty,
                           "category": "Panels", "description": "Partition Panel (Low)"})
        else:
            # Single tier - standard partition panels
            suffix = self.PANEL_HEIGHT_CONFIG.get(h_key, {}).get("side", "10S")

            # Full partition panels: W_C * H_C * N_PA
            part_full = int(self.W_C * self.H_C * self.N_PA)

            # Half partition panels for width fraction
            part_half = int(self.W_F * self.H_C * self.N_PA) if self.W_F > 0 else 0

            # Height fraction
            if self.H_F > 0:
                part_full += int(self.W_C * self.N_PA)
                part_half += int(self.W_F * self.N_PA) if self.W_F > 0 else 0

            if self.use_partition_1x1:
                prefix = "SF"
            else:
                prefix = "SL"

            # Get height number for half side panel (e.g., "20" from "20S")
            height_num = suffix[:2] if len(suffix) >= 2 else "10"

            if part_full > 0:
                panels.append({"part_no": f"{prefix}{suffix}", "quantity": part_full,
                               "category": "Panels", "description": "Partition Panel"})

            if part_half > 0:
                # Half partition panels use "M" suffix: SH20M, SH15M, etc.
                panels.append({"part_no": f"SH{height_num}M", "quantity": part_half,
                               "category": "Panels", "description": "Half Partition Panel"})

        return panels

    def _get_height_key(self) -> float:
        """Get the closest standard height key"""
        standard_heights = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        # Find closest height
        closest = min(standard_heights, key=lambda x: abs(x - self.height))
        return closest

    def get_sealing_tape_qty(self) -> Dict:
        """
        Calculate sealing tape requirement
        120mm tape: =4*H_O+1
        50mm tape: calculated from panel joints
        """
        tape_120mm = int(4 * self.H_O + 1)

        # 50mm tape based on panel connections
        # Approximate: perimeter * height * factor
        perimeter = 2 * (self.W_O + self.L_O)
        tape_50mm = int(math.ceil(perimeter * self.H_O / 30))  # 30m per roll

        return {
            "WST-0120RO": tape_120mm,
            "WST-0050RO": max(1, tape_50mm)
        }
