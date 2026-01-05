"""
Tank Configuration API Endpoints
"""
from fastapi import APIRouter, HTTPException
from app.schemas.tank import (
    TankConfigRequest,
    TankConfigResponse,
    InputOptionsResponse,
    TankDimensions,
    CapacityInfo,
)
from app.services.calculation_engine import calculate_tank_config
from app.services.data_loader import get_data_loader

router = APIRouter()


@router.get("/options", response_model=InputOptionsResponse)
async def get_input_options():
    """
    Get all available input options for tank configuration.

    Returns lists of valid options for:
    - Product types
    - Insulation types
    - Steel skid types
    - Material options
    - Bolt/nut options
    - Fitting types
    - Available heights
    """
    data_loader = get_data_loader()
    options = data_loader.get_input_options()

    return InputOptionsResponse(
        product_types=options.get("product_type", []),
        insulation_types=options.get("insulation", []),
        steel_skid_types=options.get("steel_skid", []),
        internal_materials=options.get("internal_item_material", []),
        bolts_nuts_options=options.get("bolts_nuts", []),
        tie_rod_materials=options.get("internal_tie_rod_material", []),
        tie_rod_specs=options.get("tie_rod_spec", []),
        level_indicators=options.get("level_indicator", []),
        ladder_materials_internal=options.get("internal_ladder_material", []),
        ladder_materials_external=options.get("external_ladder_material", []),
        fitting_types=options.get("fitting_types", []),
        available_heights=options.get("available_heights", []),
    )


@router.post("/calculate", response_model=TankConfigResponse)
async def calculate_configuration(request: TankConfigRequest):
    """
    Calculate complete tank configuration.

    Takes tank dimensions and options, returns:
    - Capacity information (nominal, actual, surface area)
    - Complete Bill of Materials (BOM)
    - Cost summary by category (USD and SAR)
    - Weight summary by category
    """
    try:
        result = calculate_tank_config(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/capacity", response_model=CapacityInfo)
async def calculate_capacity_only(dimensions: TankDimensions):
    """
    Calculate tank capacity only (quick calculation).

    Returns:
    - Nominal capacity (m³)
    - Actual capacity (m³)
    - Surface area (m²)
    - Number of partitions
    """
    total_length = (
        dimensions.length1 +
        (dimensions.length2 or 0) +
        (dimensions.length3 or 0) +
        (dimensions.length4 or 0)
    )

    nominal_capacity = dimensions.width * total_length * dimensions.height
    actual_capacity = dimensions.width * total_length * max(0, dimensions.height - 0.2)

    surface_area = 2 * (
        dimensions.width * total_length +
        dimensions.width * dimensions.height +
        total_length * dimensions.height
    )

    num_partitions = sum([
        1 if (dimensions.length2 or 0) > 0 else 0,
        1 if (dimensions.length3 or 0) > 0 else 0,
        1 if (dimensions.length4 or 0) > 0 else 0,
    ])

    # Add partition area
    surface_area += dimensions.width * dimensions.height * num_partitions

    return CapacityInfo(
        nominal_capacity_m3=round(nominal_capacity, 2),
        actual_capacity_m3=round(actual_capacity, 2),
        surface_area_m2=round(surface_area, 2),
        total_length=total_length,
        num_partitions=num_partitions,
    )


@router.get("/prices/{part_no}")
async def get_part_price(part_no: str):
    """
    Get price and weight for a specific part number.
    """
    data_loader = get_data_loader()
    part_info = data_loader.get_part_info(part_no)

    if not part_info.get("price_usd"):
        raise HTTPException(status_code=404, detail=f"Part not found: {part_no}")

    return part_info


@router.get("/prices")
async def list_all_prices(skip: int = 0, limit: int = 100):
    """
    List all available parts with prices.
    """
    data_loader = get_data_loader()
    prices = data_loader.get_prices()

    items = list(prices.values())[skip:skip + limit]
    return {
        "total": len(prices),
        "items": items,
        "skip": skip,
        "limit": limit,
    }
