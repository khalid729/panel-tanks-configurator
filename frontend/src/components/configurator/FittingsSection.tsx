import { Plus, Trash2 } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { FittingItem, DEFAULT_TANK_OPTIONS } from '@/types/tank';

interface FittingsSectionProps {
  fittings: FittingItem[];
  onChange: (fittings: FittingItem[]) => void;
}

const FittingsSection = ({ fittings, onChange }: FittingsSectionProps) => {
  const { language } = useLanguage();

  const addFitting = () => {
    onChange([...fittings, { fitting_type: 'WSD-050A', quantity: 1, position: '' }]);
  };

  const removeFitting = (index: number) => {
    onChange(fittings.filter((_, i) => i !== index));
  };

  const updateFitting = (index: number, updates: Partial<FittingItem>) => {
    onChange(
      fittings.map((fitting, i) => (i === index ? { ...fitting, ...updates } : fitting))
    );
  };

  return (
    <div className="section-card animate-fade-in" style={{ animationDelay: '0.4s' }}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="section-number">5</span>
          <h3 className="text-lg font-semibold text-foreground">
            {t('fittings', language)}
          </h3>
        </div>
        <Button onClick={addFitting} size="sm" variant="outline">
          <Plus className="h-4 w-4 mr-1" />
          {t('addFitting', language)}
        </Button>
      </div>

      <div className="space-y-3">
        {fittings.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            {language === 'en'
              ? 'No fittings added. Click "Add Fitting" to add one.'
              : 'لم تتم إضافة تركيبات. انقر على "إضافة تركيب" لإضافة واحد.'}
          </p>
        ) : (
          fittings.map((fitting, index) => (
            <div
              key={index}
              className="grid grid-cols-[1fr_80px_100px_40px] gap-2 items-end p-3 bg-muted/50 rounded-lg"
            >
              <div className="input-group">
                <Label className="input-label text-xs">{t('fittingType', language)}</Label>
                <Select
                  value={fitting.fitting_type}
                  onValueChange={(value) => updateFitting(index, { fitting_type: value })}
                >
                  <SelectTrigger className="h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {DEFAULT_TANK_OPTIONS.fitting_types.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="input-group">
                <Label className="input-label text-xs">{t('qty', language)}</Label>
                <Input
                  type="number"
                  value={fitting.quantity}
                  onChange={(e) =>
                    updateFitting(index, { quantity: parseInt(e.target.value) || 1 })
                  }
                  min={1}
                  className="h-9"
                />
              </div>

              <div className="input-group">
                <Label className="input-label text-xs">{t('position', language)}</Label>
                <Input
                  type="text"
                  value={fitting.position || ''}
                  onChange={(e) => updateFitting(index, { position: e.target.value })}
                  placeholder="..."
                  className="h-9"
                />
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFitting(index)}
                className="h-9 w-9 text-destructive hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FittingsSection;
