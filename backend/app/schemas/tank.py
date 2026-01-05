"""
Tank Configuration Schemas
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ==================== Input Options ====================

class TankDimensions(BaseModel):
    """Tank dimensions input"""
    width: float = Field(..., gt=0, le=20, description="Tank width in meters")
    length1: float = Field(..., gt=0, le=20, description="Tank length section 1 in meters")
    length2: Optional[float] = Field(0, ge=0, le=20, description="Tank length section 2 in meters")
    length3: Optional[float] = Field(0, ge=0, le=20, description="Tank length section 3 in meters")
    length4: Optional[float] = Field(0, ge=0, le=20, description="Tank length section 4 in meters")
    height: float = Field(..., gt=0, le=10, description="Tank height in meters")
    quantity: int = Field(1, gt=0, description="Number of tanks")


class PanelOptions(BaseModel):
    """Panel configuration options"""
    product_type: Literal["MNT", "Not Included"] = "MNT"
    insulation: Literal[
        "Non-Insulated",
        "Insulated",
        "Insulated Roof Only",
        "Insulated(Roof,Side)",
        "Non-insulated(Roof Only)"
    ] = "Non-Insulated"
    use_side_panel_1x1: bool = False
    use_partition_panel_1x1: bool = False

    @property
    def insulated(self) -> bool:
        """Check if tank is insulated"""
        return "Insulated" in self.insulation and self.insulation != "Non-Insulated"


class SteelOptions(BaseModel):
    """Steel accessories options"""
    reinforcing_type: Literal["Internal", "External"] = "Internal"
    steel_skid: Literal["Default", "Angle 75", "Channel 125", "Channel 150", "Except SKB"] = "Default"
    internal_material: Literal["SS316", "SS304"] = "SS316"
    bolts_nuts: Literal[
        "EXT:HDG/INT:SS304+R/F:HDG",
        "EXT:HDG/INT:SS304+R/F:SS304",
        "EXT:SS304/INT:SS316",
        "EXT:HDG/INT:SS316",
        "EXT:SS304/INT:SS304",
        "EXT:SS316/INT:SS316",
        "Except All Bolts",
        "Except Panel Assemble Bolts"
    ] = "EXT:HDG/INT:SS316"
    tie_rod_material: Literal["SS316", "SS304", "SS304+PET coated", "SS316+PE Coated"] = "SS316"
    tie_rod_spec: Literal["M12", "M16", "3mH_Tie_Rod(1+1)", "3mH_Tie_Rod(2+1)"] = "M12"


class AccessoryOptions(BaseModel):
    """Additional accessories options"""
    level_indicator: Literal["General", "Sensor", "No needed"] = "General"
    internal_ladder_material: Literal["GRP", "SS304", "SS316L"] = "GRP"
    internal_ladder_qty: int = Field(default=-1, ge=-1, le=5, description="-1 means Default")
    external_ladder_material: Literal["HDG", "SS304", "SS316"] = "HDG"
    external_ladder_qty: int = Field(default=-1, ge=-1, le=5, description="-1 means Default")


class FittingItem(BaseModel):
    """Single fitting item"""
    fitting_type: str = Field(..., description="Fitting type code (e.g., WFL-100A)")
    quantity: int = Field(1, gt=0)
    position: Optional[str] = Field(None, description="Position description")


class OrderInfo(BaseModel):
    """Order information"""
    order_no: Optional[str] = None
    project_name: Optional[str] = None
    location: Optional[str] = None
    sales_rep: Optional[str] = None
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    port_of_discharge: Optional[str] = None


# ==================== Main Input Schema ====================

class TankConfigRequest(BaseModel):
    """Complete tank configuration request"""
    order_info: Optional[OrderInfo] = None
    dimensions: TankDimensions
    panel_options: PanelOptions = PanelOptions()
    steel_options: SteelOptions = SteelOptions()
    accessory_options: AccessoryOptions = AccessoryOptions()
    fittings: list[FittingItem] = []
    exchange_rate: float = Field(3.75, gt=0, description="USD to SAR exchange rate")


# ==================== Output Schemas ====================

class BOMItem(BaseModel):
    """Bill of Materials item"""
    part_no: str
    part_name: str
    quantity: int
    unit_price_usd: float
    total_price_usd: float
    weight_kg: float
    total_weight_kg: float
    category: str


class CapacityInfo(BaseModel):
    """Tank capacity information"""
    nominal_capacity_m3: float
    actual_capacity_m3: float
    surface_area_m2: float
    total_length: float
    num_partitions: int


class CostSummary(BaseModel):
    """Cost summary by category"""
    panels: float
    steel_skid: float
    bolts_nuts: float
    external_reinforcing: float
    internal_reinforcing: float
    internal_tie_rod: float
    etc: float
    fittings: float
    total_usd: float
    total_sar: float


class WeightSummary(BaseModel):
    """Weight summary by category"""
    panels_kg: float
    steel_kg: float
    accessories_kg: float
    total_kg: float


class TankConfigResponse(BaseModel):
    """Complete tank configuration response"""
    capacity: CapacityInfo
    bom: list[BOMItem]
    cost_summary: CostSummary
    weight_summary: WeightSummary


# ==================== Options Response ====================

class InputOptionsResponse(BaseModel):
    """Available input options"""
    product_types: list[str]
    insulation_types: list[str]
    steel_skid_types: list[str]
    internal_materials: list[str]
    bolts_nuts_options: list[str]
    tie_rod_materials: list[str]
    tie_rod_specs: list[str]
    level_indicators: list[str]
    ladder_materials_internal: list[str]
    ladder_materials_external: list[str]
    fitting_types: list[str]
    available_heights: list[float]
