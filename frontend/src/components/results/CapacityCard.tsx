import { Droplets, Box, Layers } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { CapacityInfo } from '@/types/tank';

interface CapacityCardProps {
  capacity: CapacityInfo | null;
}

const CapacityCard = ({ capacity }: CapacityCardProps) => {
  const { language } = useLanguage();

  if (!capacity) {
    return (
      <div className="result-card animate-fade-in">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Droplets className="h-5 w-5 text-accent" />
          {t('capacity', language)}
        </h3>
        <p className="text-sm text-muted-foreground text-center py-4">
          {language === 'en'
            ? 'Configure tank dimensions to see capacity'
            : 'قم بتكوين أبعاد الخزان لعرض السعة'}
        </p>
      </div>
    );
  }

  return (
    <div className="result-card animate-fade-in">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Droplets className="h-5 w-5 text-accent" />
        {t('capacity', language)}
      </h3>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">
            {t('nominalCapacity', language)}
          </span>
          <span className="font-semibold text-lg">
            {capacity.nominal_capacity_m3.toLocaleString()} {t('cubicMeters', language)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">
            {t('actualCapacity', language)}
          </span>
          <span className="font-semibold text-lg text-accent">
            {capacity.actual_capacity_m3.toLocaleString()} {t('cubicMeters', language)}
          </span>
        </div>

        <div className="h-px bg-border my-2" />

        <div className="flex justify-between items-center text-sm">
          <span className="text-muted-foreground flex items-center gap-2">
            <Box className="h-4 w-4" />
            {t('surfaceArea', language)}
          </span>
          <span className="font-medium">
            {capacity.surface_area_m2.toLocaleString()} {t('squareMeters', language)}
          </span>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-muted-foreground flex items-center gap-2">
            <Layers className="h-4 w-4" />
            {t('partitions', language)}
          </span>
          <span className="font-medium">{capacity.num_partitions}</span>
        </div>
      </div>
    </div>
  );
};

export default CapacityCard;
