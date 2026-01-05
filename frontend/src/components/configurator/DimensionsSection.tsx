import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { TankDimensions, DEFAULT_TANK_OPTIONS } from '@/types/tank';

interface DimensionsSectionProps {
  dimensions: TankDimensions;
  onChange: (dimensions: TankDimensions) => void;
}

const DimensionsSection = ({ dimensions, onChange }: DimensionsSectionProps) => {
  const { language } = useLanguage();

  const handleChange = (field: keyof TankDimensions, value: number) => {
    onChange({ ...dimensions, [field]: value });
  };

  return (
    <div className="section-card animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <span className="section-number">1</span>
        <h3 className="text-lg font-semibold text-foreground">
          {t('dimensions', language)}
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Width */}
        <div className="input-group">
          <Label className="input-label">
            {t('width', language)} ({t('meters', language)})
          </Label>
          <Input
            type="number"
            value={dimensions.width}
            onChange={(e) => handleChange('width', parseFloat(e.target.value) || 0)}
            min={0.5}
            max={20}
            step={0.5}
          />
        </div>

        {/* Height */}
        <div className="input-group">
          <Label className="input-label">
            {t('height', language)} ({t('meters', language)})
          </Label>
          <Select
            value={dimensions.height.toString()}
            onValueChange={(value) => handleChange('height', parseFloat(value))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_TANK_OPTIONS.available_heights.map((h) => (
                <SelectItem key={h} value={h.toString()}>
                  {h} {t('meters', language)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Length 1 */}
        <div className="input-group">
          <Label className="input-label">
            {t('length1', language)} ({t('meters', language)})
          </Label>
          <Input
            type="number"
            value={dimensions.length1}
            onChange={(e) => handleChange('length1', parseFloat(e.target.value) || 0)}
            min={0.5}
            max={20}
            step={0.5}
          />
        </div>

        {/* Length 2 */}
        <div className="input-group">
          <Label className="input-label text-muted-foreground">
            {t('length2', language)} ({t('meters', language)})
          </Label>
          <Input
            type="number"
            value={dimensions.length2}
            onChange={(e) => handleChange('length2', parseFloat(e.target.value) || 0)}
            min={0}
            max={20}
            step={0.5}
            className="border-dashed"
          />
        </div>

        {/* Length 3 */}
        <div className="input-group">
          <Label className="input-label text-muted-foreground">
            {t('length3', language)} ({t('meters', language)})
          </Label>
          <Input
            type="number"
            value={dimensions.length3}
            onChange={(e) => handleChange('length3', parseFloat(e.target.value) || 0)}
            min={0}
            max={20}
            step={0.5}
            className="border-dashed"
          />
        </div>

        {/* Length 4 */}
        <div className="input-group">
          <Label className="input-label text-muted-foreground">
            {t('length4', language)} ({t('meters', language)})
          </Label>
          <Input
            type="number"
            value={dimensions.length4}
            onChange={(e) => handleChange('length4', parseFloat(e.target.value) || 0)}
            min={0}
            max={20}
            step={0.5}
            className="border-dashed"
          />
        </div>

        {/* Quantity */}
        <div className="input-group col-span-2">
          <Label className="input-label">
            {t('quantity', language)}
          </Label>
          <Input
            type="number"
            value={dimensions.quantity}
            onChange={(e) => handleChange('quantity', parseInt(e.target.value) || 1)}
            min={1}
            max={100}
            step={1}
          />
        </div>
      </div>
    </div>
  );
};

export default DimensionsSection;
