// ==================== Request Types ====================

export interface TankDimensions {
  width: number;        // 0.5 - 20m
  length1: number;      // 0.5 - 20m (required)
  length2: number;      // 0 - 20m (partition 1)
  length3: number;      // 0 - 20m (partition 2)
  length4: number;      // 0 - 20m (partition 3)
  height: number;       // 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
  quantity: number;     // 1+
}

export type ProductType = 'MNT' | 'Not Included';

export type InsulationType = 
  | 'Non-Insulated' 
  | 'Insulated' 
  | 'Insulated Roof Only'
  | 'Insulated(Roof,Side)' 
  | 'Non-insulated(Roof Only)';

export interface PanelOptions {
  product_type: ProductType;
  insulation: InsulationType;
  use_side_panel_1x1: boolean;
  use_partition_panel_1x1: boolean;
}

export type ReinforcingType = 'Internal' | 'External';

export type SteelSkidType = 'Default' | 'Angle 75' | 'Channel 125' | 'Channel 150' | 'Except SKB';

export type InternalMaterial = 'SS316' | 'SS304';

export type TieRodMaterial = 'SS316' | 'SS304' | 'SS304+PET coated' | 'SS316+PE Coated';

export type TieRodSpec = 'M12' | 'M16' | '3mH_Tie_Rod(1+1)' | '3mH_Tie_Rod(2+1)';

export interface SteelOptions {
  reinforcing_type: ReinforcingType;
  steel_skid: SteelSkidType;
  internal_material: InternalMaterial;
  bolts_nuts: string;
  tie_rod_material: TieRodMaterial;
  tie_rod_spec: TieRodSpec;
}

export type LevelIndicator = 'General' | 'Sensor' | 'No needed';

export type InternalLadderMaterial = 'GRP' | 'SS304' | 'SS316L';

export type ExternalLadderMaterial = 'HDG' | 'SS304' | 'SS316';

export interface AccessoryOptions {
  level_indicator: LevelIndicator;
  internal_ladder_material: InternalLadderMaterial;
  internal_ladder_qty: number;  // -1 = default
  external_ladder_material: ExternalLadderMaterial;
  external_ladder_qty: number;  // -1 = default
}

export interface FittingItem {
  fitting_type: string;
  quantity: number;
  position?: string;
}

export interface OrderInfo {
  order_no?: string;
  project_name?: string;
  location?: string;
  sales_rep?: string;
  delivery_date?: string;
  payment_terms?: string;
  port_of_discharge?: string;
}

export interface TankConfigRequest {
  order_info?: OrderInfo;
  dimensions: TankDimensions;
  panel_options: PanelOptions;
  steel_options: SteelOptions;
  accessory_options: AccessoryOptions;
  fittings: FittingItem[];
  exchange_rate: number;  // Default: 3.75
}

// ==================== Response Types ====================

export interface BOMItem {
  part_no: string;
  part_name: string;
  quantity: number;
  unit_price_usd: number;
  total_price_usd: number;
  weight_kg: number;
  total_weight_kg: number;
  category: string;
}

export interface CapacityInfo {
  nominal_capacity_m3: number;
  actual_capacity_m3: number;
  surface_area_m2: number;
  total_length: number;
  num_partitions: number;
}

export interface CostSummary {
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

export interface WeightSummary {
  panels_kg: number;
  steel_kg: number;
  accessories_kg: number;
  total_kg: number;
}

export interface TankConfigResponse {
  capacity: CapacityInfo;
  bom: BOMItem[];
  cost_summary: CostSummary;
  weight_summary: WeightSummary;
}

// ==================== Tank Options (for dropdowns) ====================

export interface TankOptions {
  product_types: ProductType[];
  insulation_types: InsulationType[];
  steel_skid_types: SteelSkidType[];
  internal_materials: InternalMaterial[];
  bolts_nuts_options: string[];
  tie_rod_materials: TieRodMaterial[];
  tie_rod_specs: TieRodSpec[];
  level_indicators: LevelIndicator[];
  ladder_materials_internal: InternalLadderMaterial[];
  ladder_materials_external: ExternalLadderMaterial[];
  fitting_types: string[];
  available_heights: number[];
}

// ==================== Default Values ====================

export const DEFAULT_TANK_OPTIONS: TankOptions = {
  product_types: ['MNT', 'Not Included'],
  insulation_types: [
    'Non-Insulated',
    'Insulated',
    'Insulated Roof Only',
    'Insulated(Roof,Side)',
    'Non-insulated(Roof Only)'
  ],
  steel_skid_types: ['Default', 'Angle 75', 'Channel 125', 'Channel 150', 'Except SKB'],
  internal_materials: ['SS316', 'SS304'],
  bolts_nuts_options: [
    'EXT:HDG/INT:SS304+R/F:HDG',
    'EXT:HDG/INT:SS304+R/F:SS304',
    'EXT:SS304/INT:SS316',
    'EXT:HDG/INT:SS316',
    'EXT:SS304/INT:SS304',
    'EXT:SS316/INT:SS316',
    'Except All Bolts',
    'Except Panel Assemble Bolts'
  ],
  tie_rod_materials: ['SS316', 'SS304', 'SS304+PET coated', 'SS316+PE Coated'],
  tie_rod_specs: ['M12', 'M16', '3mH_Tie_Rod(1+1)', '3mH_Tie_Rod(2+1)'],
  level_indicators: ['General', 'Sensor', 'No needed'],
  ladder_materials_internal: ['GRP', 'SS304', 'SS316L'],
  ladder_materials_external: ['HDG', 'SS304', 'SS316'],
  fitting_types: [
    'WSD-015A', 'WSD-020A', 'WSD-025A', 'WSD-032A', 'WSD-040A', 'WSD-050A',
    'WFL-050A', 'WFL-065A', 'WFL-080A', 'WFL-100A', 'WFL-125A', 'WFL-150A',
    'WFL-200A', 'WFL-250A', 'WFL-300A'
  ],
  available_heights: [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
};

export const DEFAULT_DIMENSIONS: TankDimensions = {
  width: 5,
  length1: 5,
  length2: 0,
  length3: 0,
  length4: 0,
  height: 3,
  quantity: 1
};

export const DEFAULT_PANEL_OPTIONS: PanelOptions = {
  product_type: 'MNT',
  insulation: 'Non-Insulated',
  use_side_panel_1x1: false,
  use_partition_panel_1x1: false
};

export const DEFAULT_STEEL_OPTIONS: SteelOptions = {
  reinforcing_type: 'Internal',
  steel_skid: 'Default',
  internal_material: 'SS316',
  bolts_nuts: 'EXT:HDG/INT:SS316',
  tie_rod_material: 'SS316',
  tie_rod_spec: 'M12'
};

export const DEFAULT_ACCESSORY_OPTIONS: AccessoryOptions = {
  level_indicator: 'General',
  internal_ladder_material: 'GRP',
  internal_ladder_qty: -1,
  external_ladder_material: 'HDG',
  external_ladder_qty: -1
};

export const DEFAULT_EXCHANGE_RATE = 3.75;
