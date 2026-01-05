import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { SteelOptions, DEFAULT_TANK_OPTIONS } from '@/types/tank';

interface SteelOptionsSectionProps {
  options: SteelOptions;
  onChange: (options: SteelOptions) => void;
}

const SteelOptionsSection = ({ options, onChange }: SteelOptionsSectionProps) => {
  const { language } = useLanguage();

  return (
    <div className="section-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="section-number">3</span>
        <h3 className="text-lg font-semibold text-foreground">
          {t('steelOptions', language)}
        </h3>
      </div>

      <div className="space-y-4">
        {/* Reinforcing Type */}
        <div className="input-group">
          <Label className="input-label">{t('reinforcingType', language)}</Label>
          <RadioGroup
            value={options.reinforcing_type}
            onValueChange={(value) => onChange({ ...options, reinforcing_type: value as any })}
            className="flex gap-4 mt-2"
          >
            <div className="flex items-center gap-2">
              <RadioGroupItem value="Internal" id="internal" />
              <Label htmlFor="internal" className="cursor-pointer">
                {t('internal', language)}
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <RadioGroupItem value="External" id="external" />
              <Label htmlFor="external" className="cursor-pointer">
                {t('external', language)}
              </Label>
            </div>
          </RadioGroup>
        </div>

        {/* Steel Skid */}
        <div className="input-group">
          <Label className="input-label">{t('steelSkid', language)}</Label>
          <Select
            value={options.steel_skid}
            onValueChange={(value) => onChange({ ...options, steel_skid: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.steel_skid_types.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Internal Material */}
        <div className="input-group">
          <Label className="input-label">{t('internalMaterial', language)}</Label>
          <Select
            value={options.internal_material}
            onValueChange={(value) => onChange({ ...options, internal_material: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.internal_materials.map((mat) => (
                <SelectItem key={mat} value={mat}>
                  {mat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Bolts & Nuts */}
        <div className="input-group">
          <Label className="input-label">{t('boltsNuts', language)}</Label>
          <Select
            value={options.bolts_nuts}
            onValueChange={(value) => onChange({ ...options, bolts_nuts: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.bolts_nuts_options.map((opt) => (
                <SelectItem key={opt} value={opt}>
                  {opt}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tie Rod Material */}
        <div className="input-group">
          <Label className="input-label">{t('tieRodMaterial', language)}</Label>
          <Select
            value={options.tie_rod_material}
            onValueChange={(value) => onChange({ ...options, tie_rod_material: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.tie_rod_materials.map((mat) => (
                <SelectItem key={mat} value={mat}>
                  {mat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tie Rod Spec */}
        <div className="input-group">
          <Label className="input-label">{t('tieRodSpec', language)}</Label>
          <Select
            value={options.tie_rod_spec}
            onValueChange={(value) => onChange({ ...options, tie_rod_spec: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.tie_rod_specs.map((spec) => (
                <SelectItem key={spec} value={spec}>
                  {spec}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

export default SteelOptionsSection;
