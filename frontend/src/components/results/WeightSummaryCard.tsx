import { Weight } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { WeightSummary } from '@/types/tank';

interface WeightSummaryCardProps {
  weights: WeightSummary | null;
}

const WeightSummaryCard = ({ weights }: WeightSummaryCardProps) => {
  const { language } = useLanguage();

  if (!weights) {
    return (
      <div className="result-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Weight className="h-5 w-5 text-warning" />
          {t('weightSummary', language)}
        </h3>
        <p className="text-sm text-muted-foreground text-center py-4">
          {language === 'en'
            ? 'Click Calculate to see weights'
            : 'انقر على احسب لعرض الأوزان'}
        </p>
      </div>
    );
  }

  const weightItems = [
    { label: t('panels', language), value: weights.panels_kg },
    { label: t('steel', language), value: weights.steel_kg },
    { label: t('accessoriesWeight', language), value: weights.accessories_kg },
  ];

  return (
    <div className="result-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Weight className="h-5 w-5 text-warning" />
        {t('weightSummary', language)}
      </h3>

      <div className="space-y-2">
        {weightItems.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground">{item.label}</span>
            <span className="font-medium">
              {item.value.toLocaleString()} {t('kg', language)}
            </span>
          </div>
        ))}

        <div className="h-px bg-border my-3" />

        <div className="flex justify-between items-center">
          <span className="font-semibold">{t('totalWeight', language)}</span>
          <span className="font-bold text-lg text-warning">
            {weights.total_kg.toLocaleString()} {t('kg', language)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default WeightSummaryCard;
