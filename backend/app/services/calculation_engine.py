"""
Calculation Engine - Core calculation logic for GRP Panel Tank Configuration
Using specialized calculators for accurate Excel formula replication
"""
from typing import List
from app.schemas.tank import (
    TankConfigRequest,
    TankConfigResponse,
    BOMItem,
    CapacityInfo,
    CostSummary,
    WeightSummary,
)
from app.services.data_loader import get_data_loader
from app.services.panel_calculator import PanelCalculator
from app.services.steel_skid_calculator import SteelSkidCalculator
from app.services.bolts_calculator import BoltsCalculator
from app.services.reinforcing_calculator import ReinforcingCalculator
from app.services.tie_rod_calculator import TieRodCalculator
from app.services.etc_calculator import ETCCalculator
from app.services.fittings_calculator import FittingsCalculator


class CalculationEngine:
    """Main calculation engine for tank configuration using specialized calculators"""

    def __init__(self, request: TankConfigRequest):
        self.request = request
        self.data_loader = get_data_loader()
        self.bom_items: List[BOMItem] = []

        # Extract dimensions
        self.width = request.dimensions.width
        self.length1 = request.dimensions.length1
        self.length2 = request.dimensions.length2 or 0
        self.length3 = request.dimensions.length3 or 0
        self.length4 = request.dimensions.length4 or 0
        self.height = request.dimensions.height
        self.quantity = request.dimensions.quantity

        # Calculate derived values
        self.total_length = self.length1 + self.length2 + self.length3 + self.length4

        # Number of partitions
        self.num_partitions = sum([
            1 if self.length2 > 0 else 0,
            1 if self.length3 > 0 else 0,
            1 if self.length4 > 0 else 0,
        ])

        # Calculate capacities
        self.nominal_capacity = self.width * self.total_length * self.height

    def calculate(self) -> TankConfigResponse:
        """Run all calculations and return complete response"""
        capacity = self._calculate_capacity()

        # Use specialized calculators
        self._calculate_panels()
        self._calculate_steel_skid()
        self._calculate_bolts_nuts()
        self._calculate_reinforcing()
        self._calculate_tie_rods()
        self._calculate_etc()
        self._calculate_fittings()

        cost_summary = self._calculate_cost_summary()
        weight_summary = self._calculate_weight_summary()

        return TankConfigResponse(
            capacity=capacity,
            bom=self.bom_items,
            cost_summary=cost_summary,
            weight_summary=weight_summary,
        )

    def _calculate_capacity(self) -> CapacityInfo:
        """Calculate tank capacity and surface area"""
        nominal_capacity = self.width * self.total_length * self.height
        actual_capacity = max(0, self.width * self.total_length * (self.height - 0.2))

        surface_area = (
            2 * (self.width * self.total_length +
                 self.width * self.height +
                 self.total_length * self.height) +
            self.width * self.height * self.num_partitions
        )

        return CapacityInfo(
            nominal_capacity_m3=round(nominal_capacity, 2),
            actual_capacity_m3=round(actual_capacity, 2),
            surface_area_m2=round(surface_area, 2),
            total_length=self.total_length,
            num_partitions=self.num_partitions,
        )

    def _add_bom_item(self, part_no: str, quantity: int, category: str,
                      description: str = ""):
        """Add item to BOM"""
        if quantity <= 0:
            return

        part_info = self.data_loader.get_part_info(part_no)
        unit_price = part_info.get("price_usd", 0)
        weight = part_info.get("weight_kg", 0)

        self.bom_items.append(BOMItem(
            part_no=part_no,
            part_name=part_info.get("name", description or part_no),
            quantity=quantity,
            unit_price_usd=unit_price,
            total_price_usd=round(unit_price * quantity, 2),
            weight_kg=weight,
            total_weight_kg=round(weight * quantity, 2),
            category=category,
        ))

    def _add_parts_from_calculator(self, parts: List[dict]):
        """Add parts from calculator output to BOM"""
        for part in parts:
            self._add_bom_item(
                part_no=part["part_no"],
                quantity=part["quantity"] * self.quantity,
                category=part["category"],
                description=part.get("description", "")
            )

    def _calculate_panels(self):
        """Calculate panel requirements using PanelCalculator"""
        calculator = PanelCalculator(
            width=self.width,
            length1=self.length1,
            length2=self.length2,
            length3=self.length3,
            length4=self.length4,
            height=self.height,
            use_side_1x1=self.request.panel_options.use_side_panel_1x1,
            use_partition_1x1=self.request.panel_options.use_partition_panel_1x1,
            insulated=self.request.panel_options.insulated
        )

        panels = calculator.calculate_all_panels()
        self._add_parts_from_calculator(panels)
        # Note: Sealing tape is calculated in ETC calculator to avoid duplication

    def _calculate_steel_skid(self):
        """Calculate steel skid requirements using SteelSkidCalculator"""
        # Map steel option string to type number
        steel_option = self.request.steel_options.steel_skid
        skid_type_map = {
            "Default": 1,
            "Angle 75": 2,
            "Channel 125": 3,
            "Channel 150": 4,
            "Except SKB": 5,
        }
        skid_type = skid_type_map.get(steel_option, 1)

        calculator = SteelSkidCalculator(
            width=self.width,
            length1=self.length1,
            length2=self.length2,
            length3=self.length3,
            length4=self.length4,
            height=self.height,
            skid_type=skid_type
        )

        parts = calculator.calculate_all_parts()
        self._add_parts_from_calculator(parts)

    def _calculate_bolts_nuts(self):
        """Calculate bolts and nuts using BoltsCalculator"""
        bolts_option_str = self.request.steel_options.bolts_nuts

        # Map option string to number
        # Note: Excel uses SA4 for SS316 internal bolts (not SA2)
        bolt_option_map = {
            "EXT:HDG/INT:SS304+R/F:HDG": 1,
            "EXT:HDG/INT:SS304+R/F:SS304": 2,
            "EXT:SS304/INT:SS316": 3,
            "EXT:HDG/INT:SS316": 4,  # Uses SS304 (SA4) parts in Excel
            "EXT:SS304/INT:SS304": 5,
            "EXT:SS316/INT:SS316": 6,
            "Except All Bolts": 7,
            "Except Panel Assemble Bolts": 8,
        }
        bolt_option = bolt_option_map.get(bolts_option_str, 1)

        calculator = BoltsCalculator(
            width=self.width,
            length1=self.length1,
            length2=self.length2,
            length3=self.length3,
            length4=self.length4,
            height=self.height,
            bolt_option=bolt_option,
            use_side_1x1=self.request.panel_options.use_side_panel_1x1
        )

        parts = calculator.calculate_all_parts()
        self._add_parts_from_calculator(parts)

    def _calculate_reinforcing(self):
        """Calculate reinforcing using ReinforcingCalculator"""
        # Determine internal material
        material_str = self.request.steel_options.internal_material
        internal_material = 2 if "SS316" in material_str else 4  # 2=SS316, 4=SS304

        calculator = ReinforcingCalculator(
            width=self.width,
            length1=self.length1,
            length2=self.length2,
            length3=self.length3,
            length4=self.length4,
            height=self.height,
            internal_material=internal_material,
            use_side_1x1=self.request.panel_options.use_side_panel_1x1
        )

        parts = calculator.calculate_all_parts()
        self._add_parts_from_calculator(parts)

    def _calculate_tie_rods(self):
        """Calculate tie rods using TieRodCalculator"""
        # Only calculate if height >= 2m typically
        if self.height < 2.0:
            return

        # Determine tie rod material
        material_str = self.request.steel_options.tie_rod_material
        tie_rod_material = 2 if "SS316" in material_str else 4

        # Determine tie rod spec
        spec_str = self.request.steel_options.tie_rod_spec
        tie_rod_spec = 2 if "M16" in spec_str else 1  # 1=M12, 2=M16

        calculator = TieRodCalculator(
            width=self.width,
            length1=self.length1,
            length2=self.length2,
            length3=self.length3,
            length4=self.length4,
            height=self.height,
            tie_rod_material=tie_rod_material,
            tie_rod_spec=tie_rod_spec
        )

        parts = calculator.calculate_all_parts()
        self._add_parts_from_calculator(parts)

        # Add tie rod accessories
        accessories = calculator.get_tie_rod_accessories()
        self._add_parts_from_calculator(accessories)

    def _calculate_etc(self):
        """Calculate ETC items using ETCCalculator"""
        # Map level indicator option
        level_indicator_str = self.request.accessory_options.level_indicator
        level_indicator_map = {
            "General": 1,
            "Sensor": 2,
            "No needed": 0,
        }
        level_indicator_type = level_indicator_map.get(level_indicator_str, 1)

        # Map ladder materials
        int_ladder_mat = self.request.accessory_options.internal_ladder_material
        ext_ladder_mat = self.request.accessory_options.external_ladder_material

        int_ladder_material = 2 if "GRP" in int_ladder_mat or "FRP" in int_ladder_mat else 1
        ext_ladder_material = 2 if "SS" in ext_ladder_mat else 1

        calculator = ETCCalculator(
            width=self.width,
            length1=self.length1,
            length2=self.length2,
            length3=self.length3,
            length4=self.length4,
            height=self.height,
            nominal_capacity=self.nominal_capacity,
            level_indicator_type=level_indicator_type,
            internal_ladder_material=int_ladder_material,
            external_ladder_material=ext_ladder_material
        )

        parts = calculator.calculate_all_parts()
        self._add_parts_from_calculator(parts)

    def _calculate_fittings(self):
        """Calculate fittings from user input using FittingsCalculator"""
        if not self.request.fittings:
            return

        # Convert request fittings to calculator format
        fittings_config = []
        for fitting in self.request.fittings:
            # Parse fitting type from part number (e.g., "WSD-050A" -> type="SD", size=50)
            part_no = fitting.fitting_type
            if part_no.startswith("W"):
                fitting_type = part_no[1:3]  # SD, FL, SF
                try:
                    size = int(part_no[4:7])  # Extract size from part number
                except (ValueError, IndexError):
                    size = 50  # Default size
            else:
                fitting_type = "SD"
                size = 50

            fittings_config.append({
                "type": fitting_type,
                "size": size,
                "quantity": fitting.quantity
            })

        calculator = FittingsCalculator(fittings_config=fittings_config)
        parts = calculator.calculate_all_parts()

        for part in parts:
            self._add_bom_item(
                part_no=part["part_no"],
                quantity=part["quantity"] * self.quantity,
                category="Fittings",
                description=part.get("description", "")
            )

    def _calculate_cost_summary(self) -> CostSummary:
        """Calculate cost summary by category"""
        categories = {
            "Panels": 0.0,
            "Steel Skid": 0.0,
            "Bolts & Nuts": 0.0,
            "External Reinforcing": 0.0,
            "Internal Reinforcing": 0.0,
            "Internal Tie-rod": 0.0,
            "Tie Rods": 0.0,
            "Tie Rod Accessories": 0.0,
            "ETC": 0.0,
            "Etc": 0.0,
            "Fittings": 0.0,
        }

        for item in self.bom_items:
            if item.category in categories:
                categories[item.category] += item.total_price_usd

        # Combine similar categories
        total_tie_rod = categories["Internal Tie-rod"] + categories["Tie Rods"] + categories["Tie Rod Accessories"]
        total_etc = categories["ETC"] + categories["Etc"]

        total_usd = sum(categories.values())
        total_sar = total_usd * self.request.exchange_rate

        return CostSummary(
            panels=round(categories["Panels"], 2),
            steel_skid=round(categories["Steel Skid"], 2),
            bolts_nuts=round(categories["Bolts & Nuts"], 2),
            external_reinforcing=round(categories["External Reinforcing"], 2),
            internal_reinforcing=round(categories["Internal Reinforcing"], 2),
            internal_tie_rod=round(total_tie_rod, 2),
            etc=round(total_etc, 2),
            fittings=round(categories["Fittings"], 2),
            total_usd=round(total_usd, 2),
            total_sar=round(total_sar, 2),
        )

    def _calculate_weight_summary(self) -> WeightSummary:
        """Calculate weight summary by category"""
        panels_weight = sum(
            item.total_weight_kg for item in self.bom_items
            if item.category == "Panels"
        )

        steel_weight = sum(
            item.total_weight_kg for item in self.bom_items
            if item.category in ["Steel Skid", "Bolts & Nuts", "External Reinforcing",
                                 "Internal Reinforcing", "Internal Tie-rod", "Tie Rods",
                                 "Tie Rod Accessories"]
        )

        accessories_weight = sum(
            item.total_weight_kg for item in self.bom_items
            if item.category in ["Etc", "ETC", "Fittings"]
        )

        return WeightSummary(
            panels_kg=round(panels_weight, 2),
            steel_kg=round(steel_weight, 2),
            accessories_kg=round(accessories_weight, 2),
            total_kg=round(panels_weight + steel_weight + accessories_weight, 2),
        )


def calculate_tank_config(request: TankConfigRequest) -> TankConfigResponse:
    """Main function to calculate tank configuration"""
    engine = CalculationEngine(request)
    return engine.calculate()
