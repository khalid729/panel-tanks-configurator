import { useState } from 'react';
import { Calculator, RotateCcw, FileDown } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { calculateTank } from '@/services/api';
import { exportToPDF } from '@/services/pdfExport';

import DimensionsSection from './configurator/DimensionsSection';
import PanelOptionsSection from './configurator/PanelOptionsSection';
import SteelOptionsSection from './configurator/SteelOptionsSection';
import AccessoriesSection from './configurator/AccessoriesSection';
import FittingsSection from './configurator/FittingsSection';

import CapacityCard from './results/CapacityCard';
import CostSummaryCard from './results/CostSummaryCard';
import WeightSummaryCard from './results/WeightSummaryCard';
import BOMTable from './results/BOMTable';

import {
  TankDimensions,
  PanelOptions,
  SteelOptions,
  AccessoryOptions,
  FittingItem,
  CapacityInfo,
  CostSummary,
  WeightSummary,
  BOMItem,
  TankConfigRequest,
  DEFAULT_DIMENSIONS,
  DEFAULT_PANEL_OPTIONS,
  DEFAULT_STEEL_OPTIONS,
  DEFAULT_ACCESSORY_OPTIONS,
  DEFAULT_EXCHANGE_RATE,
} from '@/types/tank';

const TankConfigurator = () => {
  const { language, isRTL } = useLanguage();
  const { toast } = useToast();

  // Configuration State
  const [dimensions, setDimensions] = useState<TankDimensions>(DEFAULT_DIMENSIONS);
  const [panelOptions, setPanelOptions] = useState<PanelOptions>(DEFAULT_PANEL_OPTIONS);
  const [steelOptions, setSteelOptions] = useState<SteelOptions>(DEFAULT_STEEL_OPTIONS);
  const [accessoryOptions, setAccessoryOptions] = useState<AccessoryOptions>(DEFAULT_ACCESSORY_OPTIONS);
  const [fittings, setFittings] = useState<FittingItem[]>([]);
  const [exchangeRate, setExchangeRate] = useState(DEFAULT_EXCHANGE_RATE);

  // Results State
  const [capacity, setCapacity] = useState<CapacityInfo | null>(null);
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null);
  const [weightSummary, setWeightSummary] = useState<WeightSummary | null>(null);
  const [bomItems, setBomItems] = useState<BOMItem[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);

  // Handle Calculate - calls real backend API
  const handleCalculate = async () => {
    setIsCalculating(true);

    try {
      // Build request object
      const request = {
        dimensions: {
          width: dimensions.width,
          length1: dimensions.length1,
          length2: dimensions.length2,
          length3: dimensions.length3,
          length4: dimensions.length4,
          height: dimensions.height,
          quantity: dimensions.quantity,
        },
        panel_options: {
          product_type: panelOptions.product_type,
          insulation: panelOptions.insulation,
          use_side_panel_1x1: panelOptions.use_side_panel_1x1,
          use_partition_panel_1x1: panelOptions.use_partition_panel_1x1,
        },
        steel_options: {
          reinforcing_type: steelOptions.reinforcing_type,
          steel_skid: steelOptions.steel_skid,
          internal_material: steelOptions.internal_material,
          bolts_nuts: steelOptions.bolts_nuts,
          tie_rod_material: steelOptions.tie_rod_material,
          tie_rod_spec: steelOptions.tie_rod_spec,
        },
        accessory_options: {
          level_indicator: accessoryOptions.level_indicator,
          internal_ladder_material: accessoryOptions.internal_ladder_material,
          internal_ladder_qty: accessoryOptions.internal_ladder_qty,
          external_ladder_material: accessoryOptions.external_ladder_material,
          external_ladder_qty: accessoryOptions.external_ladder_qty,
        },
        fittings: fittings,
        exchange_rate: exchangeRate,
      };

      // Call backend API
      const response = await calculateTank(request);

      // Update state with response
      setCapacity(response.capacity);
      setBomItems(response.bom);
      setCostSummary(response.cost_summary);
      setWeightSummary(response.weight_summary);

      toast({
        title: language === 'en' ? 'Calculation Complete' : 'اكتمل الحساب',
        description: language === 'en'
          ? `Generated ${response.bom.length} BOM items`
          : `تم إنشاء ${response.bom.length} عنصر في قائمة المواد`,
      });
    } catch (error) {
      console.error('Calculation error:', error);
      toast({
        title: language === 'en' ? 'Calculation Error' : 'خطأ في الحساب',
        description: error instanceof Error ? error.message :
          (language === 'en' ? 'An error occurred during calculation' : 'حدث خطأ أثناء الحساب'),
        variant: 'destructive',
      });
    } finally {
      setIsCalculating(false);
    }
  };

  // Handle Reset
  const handleReset = () => {
    setDimensions(DEFAULT_DIMENSIONS);
    setPanelOptions(DEFAULT_PANEL_OPTIONS);
    setSteelOptions(DEFAULT_STEEL_OPTIONS);
    setAccessoryOptions(DEFAULT_ACCESSORY_OPTIONS);
    setFittings([]);
    setExchangeRate(DEFAULT_EXCHANGE_RATE);
    setCapacity(null);
    setCostSummary(null);
    setWeightSummary(null);
    setBomItems([]);

    toast({
      title: language === 'en' ? 'Reset Complete' : 'تم إعادة التعيين',
      description: language === 'en'
        ? 'All values have been reset to defaults'
        : 'تم إعادة تعيين جميع القيم إلى الافتراضية',
    });
  };

  // Handle PDF Export
  const handleExport = () => {
    if (!capacity || !costSummary || !weightSummary || bomItems.length === 0) {
      toast({
        title: language === 'en' ? 'No Data' : 'لا توجد بيانات',
        description: language === 'en'
          ? 'Please calculate first before exporting'
          : 'يرجى إجراء الحساب أولاً قبل التصدير',
        variant: 'destructive',
      });
      return;
    }

    try {
      exportToPDF({
        dimensions,
        capacity,
        bomItems,
        costSummary,
        weightSummary,
      });

      toast({
        title: language === 'en' ? 'Export Complete' : 'تم التصدير',
        description: language === 'en'
          ? 'PDF has been downloaded'
          : 'تم تحميل ملف PDF',
      });
    } catch (error) {
      toast({
        title: language === 'en' ? 'Export Error' : 'خطأ في التصدير',
        description: language === 'en'
          ? 'Failed to generate PDF'
          : 'فشل في إنشاء ملف PDF',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <div className={`grid gap-6 lg:grid-cols-2 ${isRTL ? 'lg:grid-flow-dense' : ''}`}>
        {/* Configuration Panel */}
        <div className={`space-y-4 ${isRTL ? 'lg:col-start-2' : ''}`}>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              <Calculator className="h-5 w-5 text-primary" />
              {language === 'en' ? 'Tank Configuration' : 'تكوين الخزان'}
            </h2>
          </div>

          {/* Exchange Rate */}
          <div className="section-card">
            <div className="flex items-center gap-4">
              <Label className="input-label whitespace-nowrap">
                {t('exchangeRate', language)} (USD → SAR)
              </Label>
              <Input
                type="number"
                value={exchangeRate}
                onChange={(e) => setExchangeRate(parseFloat(e.target.value) || 3.75)}
                step={0.01}
                className="w-24"
              />
            </div>
          </div>

          <DimensionsSection dimensions={dimensions} onChange={setDimensions} />
          <PanelOptionsSection options={panelOptions} onChange={setPanelOptions} />
          <SteelOptionsSection options={steelOptions} onChange={setSteelOptions} />
          <AccessoriesSection options={accessoryOptions} onChange={setAccessoryOptions} />
          <FittingsSection fittings={fittings} onChange={setFittings} />

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <Button
              onClick={handleCalculate}
              disabled={isCalculating}
              className="flex-1 bg-success hover:bg-success/90 text-success-foreground"
              size="lg"
            >
              {isCalculating ? (
                <span className="animate-pulse">{t('loading', language)}</span>
              ) : (
                <>
                  <Calculator className="h-5 w-5 mr-2" />
                  {t('calculate', language)}
                </>
              )}
            </Button>
            <Button onClick={handleReset} variant="outline" size="lg">
              <RotateCcw className="h-5 w-5 mr-2" />
              {t('reset', language)}
            </Button>
          </div>
        </div>

        {/* Results Panel */}
        <div className={`space-y-4 ${isRTL ? 'lg:col-start-1 lg:row-start-1' : ''}`}>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-bold text-foreground">
              {t('results', language)}
            </h2>
            {bomItems.length > 0 && (
              <Button variant="outline" size="sm" onClick={handleExport}>
                <FileDown className="h-4 w-4 mr-2" />
                {t('export', language)}
              </Button>
            )}
          </div>

          <CapacityCard capacity={capacity} />
          <CostSummaryCard costs={costSummary} />
          <WeightSummaryCard weights={weightSummary} />
          <BOMTable items={bomItems} />
        </div>
      </div>
    </div>
  );
};

export default TankConfigurator;
