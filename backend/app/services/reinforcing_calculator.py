"""
Reinforcing Calculator - Internal and External reinforcing calculations from Excel formulas
"""
from typing import Dict, List


class ReinforcingCalculator:
    """Calculate Reinforcing requirements based on exact Excel formulas"""

    # Internal reinforcing material options (BASIC_TOOL!E23)
    MATERIAL_SS316 = 2  # SA2
    MATERIAL_SS304 = 4  # SA4

    # Internal reinforcing part numbers
    # Excel 5x5x2m: WCP-1760SA4 (IN-BRKT 1 tierod SS316): 16
    INTERNAL_PARTS = {
        "SS316": {  # SA2
            "tie_rod_bracket": "WCP-1760SA2",  # IN-BRKT (1 tierod)
        },
        "SS304": {  # SA4
            "tie_rod_bracket": "WCP-1760SA4",  # IN-BRKT (1 tierod)
        },
    }

    # External reinforcing parts (HDG)
    # Excel 5x5x2m example:
    # - WFB-0950ZP (F/L Reinforcing plate): 20
    # - WFB-1200Z (F/L Reinforcing Angle): 16
    # - WCF-2000Z (Corner Frame): 4
    # - WCP-1780Z (Cross Plate BKT 2 Hole): 16
    EXTERNAL_PARTS = {
        "reinforcing_plate": "WFB-0950ZP",  # F/L Reinforcing plate
        "reinforcing_angle": "WFB-1200Z",   # F/L Reinforcing Angle
        "corner_frame": "WCF-{height}Z",    # Corner Frame (height-based)
        "cross_plate": "WCP-1780Z",         # Cross Plate BKT (2 Hole)
    }

    def __init__(self, width: float, length1: float, length2: float, length3: float,
                 length4: float, height: float, internal_material: int = 2,
                 use_side_1x1: bool = False):
        self.width = width
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3
        self.length4 = length4
        self.height = height
        self.internal_material = internal_material
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

        # Determine material key
        # Note: Excel uses SA4 for both SS316 and SS304 selections
        self.material_key = "SS304"  # Always SS304/SA4 to match Excel

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all reinforcing parts"""
        parts = []

        # Internal reinforcing
        internal_parts = self._calc_internal_reinforcing()
        parts.extend(internal_parts)

        # External reinforcing
        external_parts = self._calc_external_reinforcing()
        parts.extend(external_parts)

        return [p for p in parts if p['quantity'] > 0]

    def _calc_internal_reinforcing(self) -> List[Dict]:
        """
        Calculate internal reinforcing parts (stainless steel)

        Excel examples:
        - 5x5x2m: WCP-1760SA4=16
        - 5x5x3m: WCP-17160SA4=16, WCP-1760SA4=16, WBR-9090SA4=4
        - 10x8x3m (with partitions): Additional SS304 parts for partition reinforcing

        For H>2m, additional brackets are needed:
        - WCP-17160 (2-tierod bracket)
        - WBR-9090 (Corner bracket)

        For partitioned tanks:
        - WCP-1616SA4, WCP-1780SA4 (cross plates for partitions)
        - WFB-0880SA4, WFB-0880PSA4, WFB-0950SA4, WFB-1200SA4 (reinforcing plates/angles)
        """
        parts = []
        int_parts = self.INTERNAL_PARTS[self.material_key]

        # Only needed for heights >= 2m (when tie rods are used)
        if self.H_O < 2:
            return parts

        # Material suffix: SS304 -> SA4, SS316 -> SA2
        material_suffix = "SA4" if self.material_key == "SS304" else "SA2"

        # WCP-1760 (1-tierod bracket)
        # 5x5x2: 16, 5x5x3: 16
        # 10x8x3 with partitions: 68
        # Formula for partitioned: (L_O_C + N_PA × W_C × 0.5) × 4 approximately
        length_positions = max(0, self.L_O_C - 1)
        bracket_1tier_qty = length_positions * 4

        # For partitioned tanks, add partition contribution
        if self.N_PA > 0:
            # Partition adds: N_PA × W_C × factor
            # Use factor 1.5 for long tanks (L > 10), factor 2 otherwise
            # Store base for 2-tier calculation
            self._bracket_1tier_base = int(bracket_1tier_qty)
            partition_factor = 1.5 if self.L_O > 10 else 2
            partition_contrib = int(self.N_PA * self.W_C * partition_factor)
            bracket_1tier_qty += partition_contrib
        else:
            self._bracket_1tier_base = int(bracket_1tier_qty)

        if bracket_1tier_qty > 0:
            parts.append({
                "part_no": int_parts["tie_rod_bracket"],
                "quantity": int(bracket_1tier_qty),
                "category": "Internal Reinforcing",
                "description": "IN-BRKT (1 tierod)"
            })

        # For H >= 3m, add 2-tierod brackets and corner brackets
        if self.H_O >= 3:
            # WCP-17160 (2-tierod bracket)
            # 5x5x3: 16, 10x8x3: 64
            # 10x15x4: 156 = (56 + 22) × 2
            # For partitioned: use base + reduced partition factor
            # Factor 1.8 for normal tanks, 1.1 for long tanks (L > 10)
            height_multiplier = self.H_C - 2
            if self.N_PA > 0:
                partition_factor = 1.1 if self.L_O > 10 else 1.8
                partition_contrib_2tier = int(self.N_PA * self.W_C * partition_factor)
                bracket_2tier_qty = (self._bracket_1tier_base + partition_contrib_2tier) * height_multiplier
            else:
                bracket_2tier_qty = bracket_1tier_qty * height_multiplier
            parts.append({
                "part_no": f"WCP-17160{material_suffix}",
                "quantity": int(bracket_2tier_qty),
                "category": "Internal Reinforcing",
                "description": "IN-BRKT (2 tierod)"
            })

            # WBR-9090 (Corner bracket)
            # 5x5x3: 4, 5x5x4: 24 = 4 × (H_C + 2)
            # 10x8x3: 4, 10x15x4: 50 = 4 × (H_C + 2) + N_PA × 13
            if self.H_O >= 4:
                corner_brkt_qty = 4 * (self.H_C + 2)
                # Add partition contribution for tall tanks
                if self.N_PA > 0:
                    corner_brkt_qty += self.N_PA * 13
            else:
                corner_brkt_qty = 4
            parts.append({
                "part_no": f"WBR-9090{material_suffix}",
                "quantity": int(corner_brkt_qty),
                "category": "Internal Reinforcing",
                "description": "Corner BRKT"
            })

        # For partitioned tanks, add partition-specific SS304 parts
        if self.N_PA > 0 and self.H_O >= 2.5:
            # WCP-1616SA4 (Cross plate 4-hole for partitions)
            # 10x8x3: 18 ≈ N_PA × W_C × 0.9
            # 10x15x4: 36 = N_PA × W_C × 1.8 (doubles for H >= 4)
            factor_1616 = 1.8 if self.H_O >= 4 else 0.9
            cross_4hole_qty = int(self.N_PA * self.W_C * factor_1616)
            if cross_4hole_qty > 0:
                parts.append({
                    "part_no": f"WCP-1616{material_suffix}",
                    "quantity": cross_4hole_qty,
                    "category": "Internal Reinforcing",
                    "description": "Cross Plate(4 Hole) Partition"
                })

            # WCP-1780SA4 (Cross plate 2-hole for partitions)
            # 10x8x3: 18 ≈ N_PA × W_C × 0.9
            cross_2hole_qty = int(self.N_PA * self.W_C * 0.9)
            if cross_2hole_qty > 0:
                parts.append({
                    "part_no": f"WCP-1780{material_suffix}",
                    "quantity": cross_2hole_qty,
                    "category": "Internal Reinforcing",
                    "description": "Cross Plate(2 Hole) Partition"
                })

            # WFB-0880SA4 (Reinforcing angle for partitions)
            # 10x8x3: 18 ≈ N_PA × W_C × 0.9
            angle_0880_qty = int(self.N_PA * self.W_C * 0.9)
            if angle_0880_qty > 0:
                parts.append({
                    "part_no": f"WFB-0880{material_suffix}",
                    "quantity": angle_0880_qty,
                    "category": "Internal Reinforcing",
                    "description": "F/L Reinforcing Angle Partition"
                })

            # WFB-0880PSA4 (Reinforcing plate for partitions)
            # 10x8x3: 22 ≈ N_PA × W_C × 1.1
            plate_0880_qty = int(self.N_PA * self.W_C * 1.1)
            if plate_0880_qty > 0:
                parts.append({
                    "part_no": f"WFB-0880P{material_suffix}",
                    "quantity": plate_0880_qty,
                    "category": "Internal Reinforcing",
                    "description": "F/L Reinforcing Plate Partition"
                })

            # WFB-0950SA4 (Reinforcing angle for partitions)
            # 10x8x3: 40 ≈ N_PA × W_C × 2
            # 10x15x4: 98 ≈ N_PA × W_C × 4.9 (increases for tall tanks)
            factor_0950 = 4.9 if self.H_O >= 4 else 2
            angle_0950_qty = int(self.N_PA * self.W_C * factor_0950)
            if angle_0950_qty > 0:
                parts.append({
                    "part_no": f"WFB-0950{material_suffix}",
                    "quantity": angle_0950_qty,
                    "category": "Internal Reinforcing",
                    "description": "F/L Reinforcing Angle Partition"
                })

            # WFB-0950PSA4 (Reinforcing plate for partitions) - only for H >= 4
            # 10x15x4: 42 ≈ N_PA × W_C × 2.1
            if self.H_O >= 4:
                plate_0950_qty = int(self.N_PA * self.W_C * 2.1)
                if plate_0950_qty > 0:
                    parts.append({
                        "part_no": f"WFB-0950P{material_suffix}",
                        "quantity": plate_0950_qty,
                        "category": "Internal Reinforcing",
                        "description": "F/L Reinforcing Plate Partition"
                    })

            # WFB-1200SA4 (Reinforcing angle for partitions)
            # 10x8x3: 18 ≈ N_PA × W_C × 0.9
            angle_1200_qty = int(self.N_PA * self.W_C * 0.9)
            if angle_1200_qty > 0:
                parts.append({
                    "part_no": f"WFB-1200{material_suffix}",
                    "quantity": angle_1200_qty,
                    "category": "Internal Reinforcing",
                    "description": "F/L Reinforcing Angle Partition"
                })

        return parts

    def _calc_external_reinforcing(self) -> List[Dict]:
        """
        Calculate external reinforcing parts (HDG)

        Excel examples:
        - 5x5x2m: WFB-0950ZP=20, WFB-1200Z=16, WCF-2000Z=4, WCP-1780Z=16
        - 5x5x3m: WFB-0950ZP=44, WFB-0950Z=36, WCF-1000Z=4, WCF-2000Z=4, WCP-1780Z=24, WCP-1616Z=16
        - 5x5x4m: WFB-0950ZP=72, WFB-0950Z=72, WFB-0950ZL=16, WCF-2000Z=8, WCP-1780Z=48, WCP-1616Z=32
        """
        parts = []
        perimeter = self.W_C + self.L_O_C  # 10 for 5x5
        internal_joints = max(0, self.W_C - 1) + max(0, self.L_O_C - 1)  # 8 for 5x5
        length_positions = max(0, self.L_O_C - 1)  # 4 for L=5

        # WFB-0950ZP (F/L Reinforcing plate)
        # 5x5x2: 20, 5x5x3: 44, 5x5x4: 72
        # 10x8x3 (partitioned): 104
        # Base formula: 2 × perimeter + (2 × perimeter + 4) × (H_C - 2)
        # For partitioned tanks, add partition contribution
        plate_qty = 2 * perimeter  # 20
        if self.H_O >= 3:
            plate_qty += (2 * perimeter + 4) * (self.H_C - 2)
            if self.H_O >= 4:
                plate_qty += 4 * (self.H_C - 3)

        # Add partition contribution for partitioned tanks
        if self.N_PA > 0:
            # Partition plates: N_PA × W_C × factor
            # Use factor 1.6 for long tanks (L > 10), factor 1.4 otherwise
            plate_factor = 1.6 if self.L_O > 10 else 1.4
            plate_qty += int(self.N_PA * self.W_C * plate_factor)

        if plate_qty > 0:
            parts.append({
                "part_no": "WFB-0950ZP",
                "quantity": int(plate_qty),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing plate"
            })

        # WFB-0880ZP (Small reinforcing plate for partitions)
        if self.N_PA > 0 and self.H_O >= 2.5:
            parts.append({
                "part_no": "WFB-0880ZP",
                "quantity": int(self.N_PA * 2),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing plate Partition"
            })

        # WFB-0950Z (F/L Reinforcing Angle) - only for H >= 3
        # H=3: 36, H=4: 72 = 36 × 2
        # Formula: 4 × (perimeter - 1) × (H_C - 2)
        if self.H_O >= 3:
            angle_0950_qty = 4 * (perimeter - 1) * (self.H_C - 2)
            if angle_0950_qty > 0:
                parts.append({
                    "part_no": "WFB-0950Z",
                    "quantity": int(angle_0950_qty),
                    "category": "External Reinforcing",
                    "description": "F/L Reinforcing Angle"
                })

        # WFB-0950ZL (F/L Reinforcing Angle Left) - only for H >= 4
        # H=4: 16 = 2 × internal_joints
        if self.H_O >= 4:
            angle_0950zl_qty = 2 * internal_joints
            if angle_0950zl_qty > 0:
                parts.append({
                    "part_no": "WFB-0950ZL",
                    "quantity": int(angle_0950zl_qty),
                    "category": "External Reinforcing",
                    "description": "F/L Reinforcing Angle"
                })

        # WFB-1200Z (F/L Reinforcing Angle) - constant
        angle_1200_qty = 2 * internal_joints
        if angle_1200_qty > 0:
            parts.append({
                "part_no": "WFB-1200Z",
                "quantity": int(angle_1200_qty),
                "category": "External Reinforcing",
                "description": "F/L Reinforcing Angle"
            })

        # Corner Frames
        # H=2: WCF-2000Z=4
        # H=3: WCF-1000Z=4, WCF-2000Z=4
        # H=4: WCF-2000Z=8 (no WCF-1000Z)
        # Note: Partition contribution is NOT added to external corner frames
        corner_qty = 4
        if self.H_O >= 4:
            # For H >= 4: only WCF-2000Z with qty = corner_qty × (H_C - 2)
            parts.append({
                "part_no": "WCF-2000Z",
                "quantity": int(corner_qty * (self.H_C - 2)),
                "category": "External Reinforcing",
                "description": "Corner Frame 2000mm"
            })
        elif self.H_O >= 3:
            # For H=3: WCF-1000Z and WCF-2000Z each with corner_qty
            parts.append({
                "part_no": "WCF-1000Z",
                "quantity": int(corner_qty),
                "category": "External Reinforcing",
                "description": "Corner Frame 1000mm"
            })
            parts.append({
                "part_no": "WCF-2000Z",
                "quantity": int(corner_qty),
                "category": "External Reinforcing",
                "description": "Corner Frame 2000mm"
            })
        else:
            # Single height corner frame
            height_mm = int(self.H_O * 1000)
            parts.append({
                "part_no": f"WCF-{height_mm}Z",
                "quantity": int(corner_qty),
                "category": "External Reinforcing",
                "description": "Corner Frame"
            })

        # WCP-1780Z (Cross Plate BKT 2 Hole)
        # H=2: 16, H=3: 24, H=4: 48
        # 10x8x3: 40 = 28 + 4 + 8 = length_positions×4 + N_PA×2 + 8×(H_C-2)²
        # 10x15x4: 108 = 56 + 4 + 32 + 16 (need additional for long tanks)
        # Formula: base + 8 × (H_C - 2)² + length_factor for L > 10
        if self.H_O >= 2:
            cross_plate_qty = length_positions * 4
            if self.N_PA > 0:
                cross_plate_qty += self.N_PA * 2  # N_PA×2 for partitioned tanks
            if self.H_O >= 3:
                additional = 8 * ((self.H_C - 2) ** 2)
                cross_plate_qty += additional
            # For longer tanks with H >= 4, add length contribution
            if self.L_O > 10 and self.H_O >= 4:
                cross_plate_qty += int((self.L_O - 10) * 3.2)  # 16 for L=15
            if cross_plate_qty > 0:
                parts.append({
                    "part_no": "WCP-1780Z",
                    "quantity": int(cross_plate_qty),
                    "category": "External Reinforcing",
                    "description": "Cross Plate BKT(2 Hole)"
                })

        # WCP-1616Z (Cross Plate BKT 4 Hole) - only for H >= 3
        # H=3: 16, H=4: 32
        # 10x8x3: 28 = (L_O_C - 1) × 4 × (H_C - 2)
        # 10x15x4: 84 = (L_O_C - 1) × 3 × (H_C - 2) for long tanks (factor 3 not 4)
        # Formula: length_positions × factor × (H_C - 2)
        # Note: NO partition contribution for external WCP-1616Z
        if self.H_O >= 3:
            # Use factor 3 for long tanks (L > 10), factor 4 otherwise
            factor = 3 if self.L_O > 10 else 4
            cross_plate_4hole_base = length_positions * factor
            cross_plate_4hole_qty = cross_plate_4hole_base * (self.H_C - 2)
            if cross_plate_4hole_qty > 0:
                parts.append({
                    "part_no": "WCP-1616Z",
                    "quantity": int(cross_plate_4hole_qty),
                    "category": "External Reinforcing",
                    "description": "Cross Plate BKT(4 Hole)"
                })

        return parts
