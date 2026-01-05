"""
Fittings Calculator - Drain, Overflow, Inlet/Outlet fittings
Based on exact Excel data from Fittings sheet (sheet18)

Fitting Types from Excel:
- WSF (Slant Flange): 065A, 080A, 100A, 125A, 150A
- WFL (Flat Flange): 065A, 080A, 100A, 125A, 150A, 200A
- WSD (Suction/Drain): Various sizes
- Socket (Brass): 20A, 25A, 40A, 50A
"""
from typing import Dict, List, Tuple


class FittingsCalculator:
    """Calculate Fittings requirements based on exact Excel data"""

    # Standard fitting sizes (mm) - from Excel
    FITTING_SIZES = [20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200]

    # Fitting types - matching Excel structure
    FITTING_TYPES = {
        # Slant Flange (WSF) - from Excel
        "SF": {"prefix": "WSF", "description": "Slant Flange", "sizes": [65, 80, 100, 125, 150]},
        # Flat Flange (WFL) - from Excel
        "FL": {"prefix": "WFL", "description": "Flat Flange", "sizes": [65, 80, 100, 125, 150, 200]},
        # Suction/Drain (WSD)
        "SD": {"prefix": "WSD", "description": "Suction/Drain", "sizes": [50, 65, 80, 100, 125, 150]},
        # Overflow
        "OF": {"prefix": "WOF", "description": "Overflow", "sizes": [50, 65, 80, 100, 125, 150]},
        # Socket Brass
        "SB": {"prefix": "WSB", "description": "Socket Brass", "sizes": [20, 25, 40, 50]},
        # Inlet
        "IN": {"prefix": "WIN", "description": "Inlet", "sizes": [50, 65, 80, 100, 125, 150]},
        # Outlet
        "OUT": {"prefix": "WOT", "description": "Outlet", "sizes": [50, 65, 80, 100, 125, 150]},
    }

    def __init__(self, fittings_config: List[Dict] = None):
        """
        Initialize with fittings configuration.

        fittings_config format:
        [
            {"type": "SD", "size": 50, "quantity": 2},
            {"type": "FL", "size": 100, "quantity": 1},
            ...
        ]
        """
        self.fittings_config = fittings_config or []

    def calculate_all_parts(self) -> List[Dict]:
        """Calculate all fittings based on configuration"""
        parts = []

        # Group fittings by part number
        fitting_counts = {}

        for fitting in self.fittings_config:
            fitting_type = fitting.get("type", "SD")
            size = fitting.get("size", 50)
            qty = fitting.get("quantity", 1)

            if qty <= 0:
                continue

            part_no = self._get_part_number(fitting_type, size)
            if part_no:
                if part_no in fitting_counts:
                    fitting_counts[part_no]["quantity"] += qty
                else:
                    fitting_counts[part_no] = {
                        "part_no": part_no,
                        "quantity": qty,
                        "category": "Fittings",
                        "description": self._get_description(fitting_type, size)
                    }

        parts = list(fitting_counts.values())
        return [p for p in parts if p['quantity'] > 0]

    def _get_part_number(self, fitting_type: str, size: int) -> str:
        """
        Get part number for a fitting.
        Format: W{type}-{size}A
        Examples: WSD-050A, WFL-100A, WSF-065A
        """
        type_info = self.FITTING_TYPES.get(fitting_type, self.FITTING_TYPES["SD"])
        prefix = type_info["prefix"]

        # Format size with leading zeros (3 digits)
        size_str = f"{size:03d}"

        return f"{prefix}-{size_str}A"

    def _get_description(self, fitting_type: str, size: int) -> str:
        """Get description for a fitting"""
        type_info = self.FITTING_TYPES.get(fitting_type, self.FITTING_TYPES["SD"])
        return f"{type_info['description']} {size}mm"

    @classmethod
    def get_available_fittings(cls) -> List[Dict]:
        """Get list of all available fitting options (matching Excel)"""
        fittings = []

        for fitting_type, type_info in cls.FITTING_TYPES.items():
            # Use type-specific sizes if available, otherwise use default
            sizes = type_info.get("sizes", cls.FITTING_SIZES)
            for size in sizes:
                fittings.append({
                    "type": fitting_type,
                    "size": size,
                    "part_no": f"{type_info['prefix']}-{size:03d}A",
                    "description": f"{type_info['description']} {size}mm"
                })

        return fittings

    @classmethod
    def parse_fittings_input(cls, fittings_input: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Parse fittings input from frontend.

        Input format: [(type, size, quantity), ...]
        Example: [("SD", 50, 2), ("FL", 100, 1)]

        Returns list of fitting configs
        """
        configs = []

        for item in fittings_input:
            if len(item) >= 3:
                fitting_type, size, qty = item[0], item[1], item[2]
                if qty > 0:
                    configs.append({
                        "type": fitting_type,
                        "size": size,
                        "quantity": qty
                    })

        return configs


class StandardFittingsGenerator:
    """Generate standard fittings based on tank specifications"""

    def __init__(self, width: float, length: float, height: float, num_partitions: int = 0):
        self.width = width
        self.length = length
        self.height = height
        self.num_partitions = num_partitions
        self.num_sections = num_partitions + 1

    def get_recommended_fittings(self) -> List[Dict]:
        """
        Get recommended fittings based on tank size.
        Returns list of recommended fittings with suggested quantities.
        """
        fittings = []

        # Calculate tank capacity
        capacity = self.width * self.length * self.height

        # Drain fitting - one per section
        drain_size = self._get_drain_size(capacity)
        fittings.append({
            "type": "SD",
            "size": drain_size,
            "quantity": self.num_sections,
            "description": f"Drain {drain_size}mm",
            "recommended": True
        })

        # Overflow fitting - one per section
        overflow_size = self._get_overflow_size(capacity)
        fittings.append({
            "type": "SF",
            "size": overflow_size,
            "quantity": self.num_sections,
            "description": f"Overflow {overflow_size}mm",
            "recommended": True
        })

        # Inlet/Outlet flanges
        flange_size = self._get_flange_size(capacity)
        fittings.append({
            "type": "FL",
            "size": flange_size,
            "quantity": 2,  # Inlet and Outlet
            "description": f"Flange {flange_size}mm",
            "recommended": True
        })

        return fittings

    def _get_drain_size(self, capacity: float) -> int:
        """Determine drain size based on capacity"""
        if capacity < 10:
            return 40
        elif capacity < 50:
            return 50
        elif capacity < 100:
            return 65
        elif capacity < 200:
            return 80
        elif capacity < 500:
            return 100
        else:
            return 150

    def _get_overflow_size(self, capacity: float) -> int:
        """Determine overflow size based on capacity"""
        if capacity < 10:
            return 50
        elif capacity < 50:
            return 65
        elif capacity < 100:
            return 80
        elif capacity < 200:
            return 100
        elif capacity < 500:
            return 125
        else:
            return 150

    def _get_flange_size(self, capacity: float) -> int:
        """Determine flange size based on capacity"""
        if capacity < 20:
            return 50
        elif capacity < 50:
            return 65
        elif capacity < 100:
            return 80
        elif capacity < 200:
            return 100
        elif capacity < 500:
            return 125
        else:
            return 150
