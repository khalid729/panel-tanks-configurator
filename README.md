# GRP Panel Tank Configuration System

Al Muhaideb National Tanks - Panel Tank Bill of Materials Calculator

## Overview

This system calculates the complete bill of materials (BOM) for GRP (Glass Reinforced Plastic) panel tanks. It generates accurate quantities for all components including panels, bolts, reinforcements, and accessories based on tank dimensions.

## Features

- **Accurate Calculations**: 100% match with original Excel calculations across all test configurations
- **Multiple Tank Sizes**: Supports tanks from 2x2x2m to 10x15x4m
- **Partition Support**: Handles multi-compartment tanks with up to 4 sections
- **Material Options**: Supports SS304, SS316, and Hot Dip Galvanized (HDG) materials
- **Weight Calculations**: Automatic total weight calculation based on component quantities
- **Dynamic Reports**: Customizable report generation with item filtering

## Project Structure

```
panel_tank_config/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Calculation engines
│   │   └── main.py         # Application entry
│   ├── data/               # Reference data (weights, prices)
│   └── tests/              # Test suite
├── frontend/               # React Frontend (Coming Soon)
├── assets/                 # Static assets (logo, images)
├── excel_analysis/         # Original Excel data extraction
└── docs/                   # Documentation
```

## Backend Setup

### Requirements
- Python 3.10+
- FastAPI
- Uvicorn

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Calculate BOM
```
POST /api/calculate
```

Request body:
```json
{
  "width": 5,
  "length1": 5,
  "length2": 0,
  "length3": 0,
  "length4": 0,
  "height": 3,
  "internal_material": "SA4",
  "external_material": "Z"
}
```

### Get Weights
```
GET /api/weights
```

### Health Check
```
GET /api/health
```

## Supported Tank Configurations

| Size (WxLxH) | Partitions | Nominal Capacity |
|--------------|------------|------------------|
| 5x5x2m       | None       | 50 m³           |
| 5x5x3m       | None       | 75 m³           |
| 5x5x4m       | None       | 100 m³          |
| 10x8x3m      | 2 sections | 240 m³          |
| 10x15x4m     | 3 sections | 600 m³          |

## Component Categories

- **Panels**: Bottom (BF), Roof (RF), Side (SF/SL), Partition (PF/PL)
- **Bolts**: Various sizes (M10x35, M10x50, M14x120, etc.)
- **Internal Reinforcing**: Tie rods, cross plates, center plates
- **External Reinforcing**: Flat bars, gussets, L-angles
- **Accessories**: Ladders, air vents, level indicators, sealing tape

## Testing

```bash
cd backend
pytest tests/ -v
```

## License

Proprietary - Al Muhaideb National Tanks

## Contact

For support or inquiries, contact the development team.
