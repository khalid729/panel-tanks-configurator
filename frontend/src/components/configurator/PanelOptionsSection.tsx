import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PanelOptions, DEFAULT_TANK_OPTIONS } from '@/types/tank';

interface PanelOptionsSectionProps {
  options: PanelOptions;
  onChange: (options: PanelOptions) => void;
}

const PanelOptionsSection = ({ options, onChange }: PanelOptionsSectionProps) => {
  const { language } = useLanguage();

  return (
    <div className="section-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="section-number">2</span>
        <h3 className="text-lg font-semibold text-foreground">
          {t('panelOptions', language)}
        </h3>
      </div>

      <div className="space-y-4">
        {/* Product Type */}
        <div className="input-group">
          <Label className="input-label">{t('productType', language)}</Label>
          <Select
            value={options.product_type}
            onValueChange={(value) => onChange({ ...options, product_type: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.product_types.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Insulation */}
        <div className="input-group">
          <Label className="input-label">{t('insulation', language)}</Label>
          <Select
            value={options.insulation}
            onValueChange={(value) => onChange({ ...options, insulation: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.insulation_types.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Checkboxes */}
        <div className="space-y-3 pt-2">
          <div className="flex items-center gap-3">
            <Checkbox
              id="side_panel"
              checked={options.use_side_panel_1x1}
              onCheckedChange={(checked) =>
                onChange({ ...options, use_side_panel_1x1: !!checked })
              }
            />
            <Label htmlFor="side_panel" className="cursor-pointer">
              {t('sidePanel1x1', language)}
            </Label>
          </div>

          <div className="flex items-center gap-3">
            <Checkbox
              id="partition_panel"
              checked={options.use_partition_panel_1x1}
              onCheckedChange={(checked) =>
                onChange({ ...options, use_partition_panel_1x1: !!checked })
              }
            />
            <Label htmlFor="partition_panel" className="cursor-pointer">
              {t('partitionPanel1x1', language)}
            </Label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PanelOptionsSection;
