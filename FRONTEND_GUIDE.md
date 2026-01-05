# GRP Panel Tank Configuration System
## Al Muhaideb National Tanks - Complete Development Guide

**Version:** 2.0
**Last Updated:** 2025-01-05
**Backend Accuracy:** 100% Match with Excel (267/267 items)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Current Capabilities](#current-capabilities)
3. [Backend API Reference](#backend-api-reference)
4. [Data Files Structure](#data-files-structure)
5. [Future Requirements](#future-requirements)
6. [UI/UX Design Guide](#uiux-design-guide)
7. [Business Logic Rules](#business-logic-rules)
8. [Localization](#localization)
9. [Testing & Validation](#testing--validation)

---

## System Overview

### Purpose
Calculate Bill of Materials (BOM), costs, and weights for GRP (Glass Reinforced Plastic) panel water storage tanks. The system replicates exact Excel calculations for Al Muhaideb National Tanks.

### Tested Tank Configurations
| Tank Size | Status | Items Matched |
|-----------|--------|---------------|
| 5×5×2m | ✅ 100% | 40/40 |
| 5×5×3m | ✅ 100% | 46/46 |
| 5×5×4m | ✅ 100% | 47/47 |
| 10×8×3m (partitioned) | ✅ 100% | 64/64 |
| 10×15×4m (partitioned) | ✅ 100% | 70/70 |
| **Total** | **✅ 100%** | **267/267** |

---

## Current Capabilities

### Implemented Features ✅
- [x] Tank dimension input (W × L × H)
- [x] Multi-compartment tanks (up to 4 sections)
- [x] Panel calculation (BF, RF, SF, SL, PF, PL, MF, DN, SN)
- [x] Steel skid calculation (75 Angle, 125 Channel, 150 Channel)
- [x] Bolts & nuts calculation (HDG, SS304, SS316)
- [x] Internal/External reinforcing
- [x] Tie rod calculation with connectors
- [x] Accessories (ladders, air vents, level indicators)
- [x] Sealing tape calculation
- [x] Fittings (drains, flanges, overflows)
- [x] Cost summary by category
- [x] Weight summary
- [x] Price lookup from database
- [x] Weight lookup from database

### Pending Features ⏳
- [ ] Admin panel for data management
- [ ] Price import/export (Excel/CSV)
- [ ] Weight data management
- [ ] PDF report generation
- [ ] Excel export
- [ ] Multi-tank quotation
- [ ] Drawing/diagram generation
- [ ] User authentication
- [ ] Quote history/saving

---

## Backend API Reference

### Base URL
```
Development: http://localhost:8000/api/v1
Production:  https://your-domain.com/api/v1
```

### Running the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

### Endpoints

#### 1. GET `/tank/options`
Get all available configuration options for dropdowns.

**Response:**
```json
{
  "product_types": ["MNT", "Not Included"],
  "insulation_types": [
    "Non-Insulated",
    "Insulated",
    "Insulated Roof Only",
    "Insulated(Roof,Side)",
    "Non-insulated(Roof Only)"
  ],
  "steel_skid_types": ["Default", "Angle 75", "Channel 125", "Channel 150", "Except SKB"],
  "internal_materials": ["SS316", "SS304"],
  "bolts_nuts_options": [
    "EXT:HDG/INT:SS304+R/F:HDG",
    "EXT:HDG/INT:SS304+R/F:SS304",
    "EXT:SS304/INT:SS316",
    "EXT:HDG/INT:SS316",
    "EXT:SS304/INT:SS304",
    "EXT:SS316/INT:SS316",
    "Except All Bolts",
    "Except Panel Assemble Bolts"
  ],
  "tie_rod_materials": ["SS316", "SS304", "SS304+PET coated", "SS316+PE Coated"],
  "tie_rod_specs": ["M12", "M16", "3mH_Tie_Rod(1+1)", "3mH_Tie_Rod(2+1)"],
  "level_indicators": ["General", "Sensor", "No needed"],
  "ladder_materials_internal": ["GRP", "SS304", "SS316L"],
  "ladder_materials_external": ["HDG", "SS304", "SS316"],
  "fitting_types": ["WSD-015A", "WSD-020A", "WSD-025A", "WFL-100A", "..."],
  "available_heights": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
}
```

---

#### 2. POST `/tank/calculate`
Calculate complete BOM, costs, and weights.

**Request:**
```json
{
  "order_info": {
    "order_no": "ORD-2024-001",
    "project_name": "Water Storage Project",
    "location": "Riyadh",
    "sales_rep": "Ahmed",
    "delivery_date": "2024-03-15",
    "payment_terms": "Net 30",
    "port_of_discharge": "Jeddah"
  },
  "dimensions": {
    "width": 5,
    "length1": 5,
    "length2": 0,
    "length3": 0,
    "length4": 0,
    "height": 3,
    "quantity": 1
  },
  "panel_options": {
    "product_type": "MNT",
    "insulation": "Non-Insulated",
    "use_side_panel_1x1": false,
    "use_partition_panel_1x1": false
  },
  "steel_options": {
    "reinforcing_type": "Internal",
    "steel_skid": "Default",
    "internal_material": "SS316",
    "bolts_nuts": "EXT:HDG/INT:SS316",
    "tie_rod_material": "SS316",
    "tie_rod_spec": "M12"
  },
  "accessory_options": {
    "level_indicator": "General",
    "internal_ladder_material": "GRP",
    "internal_ladder_qty": -1,
    "external_ladder_material": "HDG",
    "external_ladder_qty": -1
  },
  "fittings": [
    {"fitting_type": "WSD-050A", "quantity": 1, "position": "Drain"},
    {"fitting_type": "WFL-100A", "quantity": 2, "position": "Inlet/Outlet"}
  ],
  "exchange_rate": 3.75
}
```

**Response:**
```json
{
  "capacity": {
    "nominal_capacity_m3": 75.0,
    "actual_capacity_m3": 70.0,
    "surface_area_m2": 130.0,
    "total_length": 5.0,
    "num_partitions": 0
  },
  "bom": [
    {
      "part_no": "BF30M",
      "part_name": "Bottom Panel 30M",
      "quantity": 24,
      "unit_price_usd": 45.0,
      "total_price_usd": 1080.0,
      "weight_kg": 18.5,
      "total_weight_kg": 444.0,
      "category": "Panels"
    }
  ],
  "cost_summary": {
    "panels": 5000.0,
    "steel_skid": 1768.0,
    "bolts_nuts": 500.0,
    "external_reinforcing": 0.0,
    "internal_reinforcing": 2736.0,
    "internal_tie_rod": 200.0,
    "etc": 903.0,
    "fittings": 150.0,
    "total_usd": 11257.0,
    "total_sar": 42213.75
  },
  "weight_summary": {
    "panels_kg": 850.0,
    "steel_kg": 354.06,
    "accessories_kg": 10.2,
    "total_kg": 1214.26
  }
}
```

---

#### 3. POST `/tank/capacity`
Quick capacity calculation (lightweight).

**Request:**
```json
{
  "width": 5,
  "length1": 5,
  "length2": 0,
  "length3": 0,
  "length4": 0,
  "height": 3
}
```

**Response:**
```json
{
  "nominal_capacity_m3": 75.0,
  "actual_capacity_m3": 70.0,
  "surface_area_m2": 130.0,
  "total_length": 5.0,
  "num_partitions": 0
}
```

---

#### 4. GET `/tank/prices`
List all parts with prices.

**Response:**
```json
{
  "items": [
    {
      "part_no": "WBT-1035Z",
      "name_en": "M10x35 HDG Bolt",
      "name_kr": "M10x35 볼트",
      "price_usd": 0.15,
      "spec": "M10x35"
    }
  ],
  "total_count": 384
}
```

---

#### 5. GET `/tank/prices/{part_no}`
Get specific part info.

**Response:**
```json
{
  "part_no": "WBT-1035Z",
  "name_en": "M10x35 HDG Bolt",
  "price_usd": 0.15,
  "weight_kg": 0.07,
  "spec": "M10x35"
}
```

---

## Data Files Structure

### Current Data Files (JSON)
Located in `/backend/app/data/`:

```
data/
├── prices_complete.json     # All part prices (USD)
├── weights_complete.json    # All part weights (kg)
├── input_options.json       # Dropdown options
└── panel_config.json        # Panel configuration rules
```

### prices_complete.json Format
```json
[
  {
    "row": 1,
    "data": {
      "B": "WBT-1035Z",      // Part Number
      "C": "M10x35 볼트",    // Korean Name
      "D": 0.15,            // Price USD
      "E": "M10x35",        // Spec
      "F": "M10x35 HDG Bolt" // English Name
    }
  }
]
```

### weights_complete.json Format
```json
[
  {
    "row": 1,
    "data": {
      "A": "WBT-1035Z",  // Part Number
      "B": 0.07         // Weight in kg
    }
  }
]
```

---

## Future Requirements

### Phase 1: Admin Data Management 🔴 High Priority

#### 1.1 Price Management
```
POST /admin/prices/import     # Import prices from Excel/CSV
GET  /admin/prices/export     # Export prices to Excel/CSV
PUT  /admin/prices/{part_no}  # Update single part price
POST /admin/prices/bulk       # Bulk update prices
```

**Import File Format (Excel/CSV):**
| Part_No | Name_EN | Name_AR | Price_USD | Spec |
|---------|---------|---------|-----------|------|
| WBT-1035Z | M10x35 HDG Bolt | برغي M10x35 | 0.15 | M10x35 |

#### 1.2 Weight Management
```
POST /admin/weights/import    # Import weights from Excel/CSV
GET  /admin/weights/export    # Export weights
PUT  /admin/weights/{part_no} # Update single weight
```

#### 1.3 Exchange Rate Management
```
GET  /admin/settings/exchange-rate
PUT  /admin/settings/exchange-rate
```

---

### Phase 2: Report Generation 🟡 Medium Priority

#### 2.1 PDF Report
```
POST /tank/report/pdf
```
**Features:**
- Company letterhead
- Tank specifications
- BOM table with prices
- Cost summary
- Weight summary
- Terms & conditions
- Arabic/English support

#### 2.2 Excel Export
```
POST /tank/report/excel
```
**Sheets:**
1. Summary
2. BOM Details
3. Cost Breakdown
4. Weight Breakdown

---

### Phase 3: Advanced Features 🟢 Future

#### 3.1 Multi-Tank Quotation
```json
{
  "quotation_info": {
    "quote_no": "QT-2024-001",
    "customer": "ABC Company",
    "validity_days": 30
  },
  "tanks": [
    { "id": 1, "dimensions": {...}, "quantity": 2 },
    { "id": 2, "dimensions": {...}, "quantity": 1 }
  ],
  "discount_percent": 5
}
```

#### 3.2 Drawing Generation
- 2D schematic diagram
- Panel layout
- Tie rod positions
- Fitting positions

#### 3.3 Quote History
```
GET  /quotes                  # List all quotes
POST /quotes                  # Save new quote
GET  /quotes/{id}             # Get quote details
PUT  /quotes/{id}             # Update quote
DELETE /quotes/{id}           # Delete quote
```

#### 3.4 User Management
```
POST /auth/login
POST /auth/logout
GET  /users
POST /users
PUT  /users/{id}
```

**User Roles:**
- `admin` - Full access + data management
- `sales` - Create/view quotes
- `viewer` - View only

---

## UI/UX Design Guide

### Recommended Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  🏭 Al Muhaideb National Tanks - Tank Configuration System         │
│  [🌐 AR/EN] [👤 User] [⚙️ Settings]                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────┐  ┌──────────────────────────────────┐ │
│  │   📐 TANK CONFIGURATION │  │   📊 RESULTS                     │ │
│  │                         │  │                                  │ │
│  │  ┌─────────────────┐    │  │  ┌────────────────────────────┐  │ │
│  │  │ 1. Dimensions   │    │  │  │ Capacity                   │  │ │
│  │  │   W: [5  ] m    │    │  │  │ Nominal: 75 m³            │  │ │
│  │  │   L1:[5  ] m    │    │  │  │ Actual:  70 m³            │  │ │
│  │  │   L2:[0  ] m    │    │  │  │ Surface: 130 m²           │  │ │
│  │  │   L3:[0  ] m    │    │  │  └────────────────────────────┘  │ │
│  │  │   L4:[0  ] m    │    │  │                                  │ │
│  │  │   H: [3 ▼] m    │    │  │  ┌────────────────────────────┐  │ │
│  │  │   Qty:[1 ]      │    │  │  │ Cost Summary               │  │ │
│  │  └─────────────────┘    │  │  │ Panels:        $5,000      │  │ │
│  │                         │  │  │ Steel Skid:    $1,768      │  │ │
│  │  ┌─────────────────┐    │  │  │ Bolts:         $500        │  │ │
│  │  │ 2. Panel Options│    │  │  │ Reinforcing:   $2,736      │  │ │
│  │  │ Product: [MNT▼] │    │  │  │ Tie Rods:      $200        │  │ │
│  │  │ Insulation:[▼]  │    │  │  │ ETC:           $903        │  │ │
│  │  │ ☐ 1x1 Side      │    │  │  │ Fittings:      $150        │  │ │
│  │  │ ☐ 1x1 Partition │    │  │  │ ──────────────────────     │  │ │
│  │  └─────────────────┘    │  │  │ TOTAL USD:     $11,257     │  │ │
│  │                         │  │  │ TOTAL SAR:     42,214 ر.س  │  │ │
│  │  ┌─────────────────┐    │  │  └────────────────────────────┘  │ │
│  │  │ 3. Steel Options│    │  │                                  │ │
│  │  │ Skid: [Default▼]│    │  │  ┌────────────────────────────┐  │ │
│  │  │ Material:[SS316]│    │  │  │ Weight Summary             │  │ │
│  │  │ Bolts: [HDG/SS▼]│    │  │  │ Panels:    850 kg          │  │ │
│  │  │ Tie Rod:[SS316▼]│    │  │  │ Steel:     354 kg          │  │ │
│  │  │ Spec: [M12▼]    │    │  │  │ Access.:   10 kg           │  │ │
│  │  └─────────────────┘    │  │  │ TOTAL:     1,214 kg        │  │ │
│  │                         │  │  └────────────────────────────┘  │ │
│  │  ┌─────────────────┐    │  │                                  │ │
│  │  │ 4. Accessories  │    │  │  ┌────────────────────────────┐  │ │
│  │  │ Level:[General▼]│    │  │  │ BOM Table                  │  │ │
│  │  │ Int.Ladder:[GRP]│    │  │  │ ┌──────┬────┬─────┬─────┐  │  │ │
│  │  │ Ext.Ladder:[HDG]│    │  │  │ │Part  │Qty │Price│Total│  │  │ │
│  │  └─────────────────┘    │  │  │ ├──────┼────┼─────┼─────┤  │  │ │
│  │                         │  │  │ │BF30M │ 24 │ $45 │$1080│  │  │ │
│  │  ┌─────────────────┐    │  │  │ │RF00M │ 24 │ $40 │$960 │  │  │ │
│  │  │ 5. Fittings     │    │  │  │ │...   │... │ ... │ ... │  │  │ │
│  │  │ [+ Add Fitting] │    │  │  │ └──────┴────┴─────┴─────┘  │  │ │
│  │  │ WSD-050A × 1    │    │  │  └────────────────────────────┘  │ │
│  │  │ WFL-100A × 2    │    │  │                                  │ │
│  │  └─────────────────┘    │  │  ┌────────────────────────────┐  │ │
│  │                         │  │  │ [📄 PDF] [📊 Excel] [💾 Save] │ │
│  │  [🔄 Calculate]         │  │  └────────────────────────────┘  │ │
│  └─────────────────────────┘  └──────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Color Scheme
```css
:root {
  --primary: #1a365d;      /* Navy Blue - Main brand */
  --secondary: #2b6cb0;    /* Medium Blue */
  --accent: #38a169;       /* Green - Success */
  --warning: #d69e2e;      /* Yellow - Warnings */
  --danger: #e53e3e;       /* Red - Errors */
  --bg-light: #f7fafc;     /* Light background */
  --text-dark: #1a202c;    /* Dark text */
}
```

### Responsive Breakpoints
```css
/* Mobile */
@media (max-width: 640px) { /* Stack vertically */ }

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) { /* 2 columns */ }

/* Desktop */
@media (min-width: 1025px) { /* Side by side */ }
```

---

## Business Logic Rules

### Dimension Rules
| Field | Min | Max | Step | Required |
|-------|-----|-----|------|----------|
| Width | 0.5 | 20 | 0.5 | ✅ |
| Length1 | 0.5 | 20 | 0.5 | ✅ |
| Length2-4 | 0 | 20 | 0.5 | ❌ |
| Height | 1.0 | 5.0 | 0.5 | ✅ |
| Quantity | 1 | 100 | 1 | ✅ |

### Capacity Formulas
```
Nominal Capacity = Width × (L1+L2+L3+L4) × Height
Actual Capacity  = Width × (L1+L2+L3+L4) × (Height - 0.2)
Surface Area     = 2×(W×L + W×H + L×H) + W×H×N_PA
```

### Steel Skid Auto-Selection (Default)
```
if Height > 4.3m → Channel 150
elif Height > 2.5m → Channel 125
elif Height > 0 → Angle 75
```

### Partition Detection
```
N_PA = count(L2 > 0, L3 > 0, L4 > 0)
```

### Tie Rod Tiers
```
if Height >= 3m:
    tiers = 2 × H_C - 3
else:
    tiers = 1
```

---

## Localization

### Supported Languages
- **English (en)** - Primary
- **Arabic (ar)** - RTL support required

### Translation Keys Structure
```json
{
  "common": {
    "calculate": { "en": "Calculate", "ar": "احسب" },
    "export": { "en": "Export", "ar": "تصدير" },
    "save": { "en": "Save", "ar": "حفظ" }
  },
  "dimensions": {
    "width": { "en": "Width", "ar": "العرض" },
    "length": { "en": "Length", "ar": "الطول" },
    "height": { "en": "Height", "ar": "الارتفاع" }
  },
  "units": {
    "meters": { "en": "m", "ar": "م" },
    "kg": { "en": "kg", "ar": "كجم" },
    "usd": { "en": "USD", "ar": "دولار" },
    "sar": { "en": "SAR", "ar": "ر.س" }
  }
}
```

### Arabic Direction
```html
<html dir="rtl" lang="ar">
```

---

## Testing & Validation

### Test Cases (Must Pass)
```typescript
const testCases = [
  { w: 5, l1: 5, l2: 0, l3: 0, l4: 0, h: 2, expected: 40 },  // 40 items
  { w: 5, l1: 5, l2: 0, l3: 0, l4: 0, h: 3, expected: 46 },  // 46 items
  { w: 5, l1: 5, l2: 0, l3: 0, l4: 0, h: 4, expected: 47 },  // 47 items
  { w: 10, l1: 5, l2: 5, l3: 5, l4: 0, h: 3, expected: 64 }, // partitioned
  { w: 10, l1: 5, l2: 5, l3: 5, l4: 0, h: 4, expected: 70 }, // tall partitioned
];
```

### Validation Rules
```typescript
const validationRules = {
  dimensions: {
    width: { min: 0.5, max: 20, step: 0.5 },
    length1: { min: 0.5, max: 20, step: 0.5, required: true },
    length2: { min: 0, max: 20, step: 0.5 },
    length3: { min: 0, max: 20, step: 0.5 },
    length4: { min: 0, max: 20, step: 0.5 },
    height: { enum: [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5] },
    quantity: { min: 1, max: 100, integer: true }
  }
};
```

---

## TypeScript Interfaces

```typescript
// ==================== Request Types ====================

interface TankDimensions {
  width: number;        // 0.5 - 20m
  length1: number;      // 0.5 - 20m (required)
  length2?: number;     // 0 - 20m (partition 1)
  length3?: number;     // 0 - 20m (partition 2)
  length4?: number;     // 0 - 20m (partition 3)
  height: number;       // 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
  quantity: number;     // 1+
}

interface PanelOptions {
  product_type: 'MNT' | 'Not Included';
  insulation: 'Non-Insulated' | 'Insulated' | 'Insulated Roof Only' |
              'Insulated(Roof,Side)' | 'Non-insulated(Roof Only)';
  use_side_panel_1x1: boolean;
  use_partition_panel_1x1: boolean;
}

interface SteelOptions {
  reinforcing_type: 'Internal' | 'External';
  steel_skid: 'Default' | 'Angle 75' | 'Channel 125' | 'Channel 150' | 'Except SKB';
  internal_material: 'SS316' | 'SS304';
  bolts_nuts: string;
  tie_rod_material: 'SS316' | 'SS304' | 'SS304+PET coated' | 'SS316+PE Coated';
  tie_rod_spec: 'M12' | 'M16' | '3mH_Tie_Rod(1+1)' | '3mH_Tie_Rod(2+1)';
}

interface AccessoryOptions {
  level_indicator: 'General' | 'Sensor' | 'No needed';
  internal_ladder_material: 'GRP' | 'SS304' | 'SS316L';
  internal_ladder_qty: number;  // -1 = default
  external_ladder_material: 'HDG' | 'SS304' | 'SS316';
  external_ladder_qty: number;  // -1 = default
}

interface FittingItem {
  fitting_type: string;
  quantity: number;
  position?: string;
}

interface OrderInfo {
  order_no?: string;
  project_name?: string;
  location?: string;
  sales_rep?: string;
  delivery_date?: string;
  payment_terms?: string;
  port_of_discharge?: string;
}

interface TankConfigRequest {
  order_info?: OrderInfo;
  dimensions: TankDimensions;
  panel_options: PanelOptions;
  steel_options: SteelOptions;
  accessory_options: AccessoryOptions;
  fittings: FittingItem[];
  exchange_rate: number;  // Default: 3.75
}

// ==================== Response Types ====================

interface BOMItem {
  part_no: string;
  part_name: string;
  quantity: number;
  unit_price_usd: number;
  total_price_usd: number;
  weight_kg: number;
  total_weight_kg: number;
  category: string;
}

interface CapacityInfo {
  nominal_capacity_m3: number;
  actual_capacity_m3: number;
  surface_area_m2: number;
  total_length: number;
  num_partitions: number;
}

interface CostSummary {
  panels: number;
  steel_skid: number;
  bolts_nuts: number;
  external_reinforcing: number;
  internal_reinforcing: number;
  internal_tie_rod: number;
  etc: number;
  fittings: number;
  total_usd: number;
  total_sar: number;
}

interface WeightSummary {
  panels_kg: number;
  steel_kg: number;
  accessories_kg: number;
  total_kg: number;
}

interface TankConfigResponse {
  capacity: CapacityInfo;
  bom: BOMItem[];
  cost_summary: CostSummary;
  weight_summary: WeightSummary;
}

// ==================== Admin Types (Future) ====================

interface PriceImportRequest {
  file: File;  // Excel or CSV
  overwrite_existing: boolean;
}

interface PriceUpdateRequest {
  part_no: string;
  price_usd: number;
  name_en?: string;
  name_ar?: string;
}

interface QuotationRequest {
  quotation_info: {
    quote_no: string;
    customer_name: string;
    customer_email?: string;
    validity_days: number;
    notes?: string;
  };
  tanks: Array<{
    tank_id: number;
    config: TankConfigRequest;
  }>;
  discount_percent?: number;
  additional_charges?: Array<{
    description: string;
    amount_usd: number;
  }>;
}
```

---

## Backend Source Files Reference

```
backend/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── api/
│   │   ├── router.py              # API routes
│   │   └── endpoints/
│   │       └── tank.py            # Tank endpoints
│   ├── core/
│   │   └── config.py              # Settings
│   ├── schemas/
│   │   └── tank.py                # Pydantic models
│   ├── services/
│   │   ├── calculation_engine.py  # Main orchestrator
│   │   ├── data_loader.py         # Load prices/weights
│   │   ├── panel_calculator.py    # Panel calculations
│   │   ├── steel_skid_calculator.py
│   │   ├── bolts_calculator.py
│   │   ├── reinforcing_calculator.py
│   │   ├── tie_rod_calculator.py
│   │   ├── etc_calculator.py      # Accessories
│   │   └── fittings_calculator.py
│   └── data/
│       ├── prices_complete.json
│       ├── weights_complete.json
│       ├── input_options.json
│       └── panel_config.json
├── tests/
│   └── test_excel_compare.py      # Validation tests
└── requirements.txt
```

---

## Contact & Support

For backend issues or questions:
- Check API documentation at `/docs`
- Review test file: `test_excel_compare.py`
- Backend calculations match Excel 100%

---

*Document Version: 2.0 | Backend Accuracy: 100% (267/267)*
