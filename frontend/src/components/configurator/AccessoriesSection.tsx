import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AccessoryOptions, DEFAULT_TANK_OPTIONS } from '@/types/tank';

interface AccessoriesSectionProps {
  options: AccessoryOptions;
  onChange: (options: AccessoryOptions) => void;
}

const AccessoriesSection = ({ options, onChange }: AccessoriesSectionProps) => {
  const { language } = useLanguage();

  return (
    <div className="section-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="section-number">4</span>
        <h3 className="text-lg font-semibold text-foreground">
          {t('accessories', language)}
        </h3>
      </div>

      <div className="space-y-4">
        {/* Level Indicator */}
        <div className="input-group">
          <Label className="input-label">{t('levelIndicator', language)}</Label>
          <Select
            value={options.level_indicator}
            onValueChange={(value) => onChange({ ...options, level_indicator: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.level_indicators.map((ind) => (
                <SelectItem key={ind} value={ind}>
                  {ind}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Internal Ladder */}
        <div className="space-y-2">
          <Label className="input-label">{t('internalLadder', language)}</Label>
          <div className="grid grid-cols-2 gap-2">
            <Select
              value={options.internal_ladder_material}
              onValueChange={(value) =>
                onChange({ ...options, internal_ladder_material: value as any })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder={t('material', language)} />
              </SelectTrigger>
              <SelectContent>
                {DEFAULT_TANK_OPTIONS.ladder_materials_internal.map((mat) => (
                  <SelectItem key={mat} value={mat}>
                    {mat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              type="number"
              value={options.internal_ladder_qty === -1 ? '' : options.internal_ladder_qty}
              onChange={(e) =>
                onChange({
                  ...options,
                  internal_ladder_qty: e.target.value ? parseInt(e.target.value) : -1,
                })
              }
              placeholder="Auto"
              min={-1}
            />
          </div>
        </div>

        {/* External Ladder */}
        <div className="space-y-2">
          <Label className="input-label">{t('externalLadder', language)}</Label>
          <div className="grid grid-cols-2 gap-2">
            <Select
              value={options.external_ladder_material}
              onValueChange={(value) =>
                onChange({ ...options, external_ladder_material: value as any })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder={t('material', language)} />
              </SelectTrigger>
              <SelectContent>
                {DEFAULT_TANK_OPTIONS.ladder_materials_external.map((mat) => (
                  <SelectItem key={mat} value={mat}>
                    {mat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              type="number"
              value={options.external_ladder_qty === -1 ? '' : options.external_ladder_qty}
              onChange={(e) =>
                onChange({
                  ...options,
                  external_ladder_qty: e.target.value ? parseInt(e.target.value) : -1,
                })
              }
              placeholder="Auto"
              min={-1}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccessoriesSection;
