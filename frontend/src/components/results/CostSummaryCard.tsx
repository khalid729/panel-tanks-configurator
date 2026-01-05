import { DollarSign } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import { CostSummary } from '@/types/tank';

interface CostSummaryCardProps {
  costs: CostSummary | null;
}

const CostSummaryCard = ({ costs }: CostSummaryCardProps) => {
  const { language } = useLanguage();

  const formatCurrency = (value: number, currency: 'usd' | 'sar') => {
    const symbol = currency === 'usd' ? '$' : '';
    const suffix = currency === 'sar' ? ` ${t('sar', language)}` : '';
    return `${symbol}${value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}${suffix}`;
  };

  if (!costs) {
    return (
      <div className="summary-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <DollarSign className="h-5 w-5 text-success" />
          {t('costSummary', language)}
        </h3>
        <p className="text-sm text-muted-foreground text-center py-4">
          {language === 'en'
            ? 'Click Calculate to see costs'
            : 'انقر على احسب لعرض التكاليف'}
        </p>
      </div>
    );
  }

  const costItems = [
    { label: t('panels', language), value: costs.panels },
    { label: t('steelSkidCost', language), value: costs.steel_skid },
    { label: t('bolts', language), value: costs.bolts_nuts },
    { label: t('reinforcing', language), value: costs.internal_reinforcing + costs.external_reinforcing },
    { label: t('tieRods', language), value: costs.internal_tie_rod },
    { label: t('etc', language), value: costs.etc },
    { label: t('fittings', language), value: costs.fittings },
  ];

  return (
    <div className="summary-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <DollarSign className="h-5 w-5 text-success" />
        {t('costSummary', language)}
      </h3>

      <div className="space-y-2">
        {costItems.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground">{item.label}</span>
            <span className="font-medium">{formatCurrency(item.value, 'usd')}</span>
          </div>
        ))}

        <div className="h-px bg-primary/20 my-3" />

        <div className="flex justify-between items-center">
          <span className="font-semibold">{t('total', language)} ({t('usd', language)})</span>
          <span className="font-bold text-lg text-success">
            {formatCurrency(costs.total_usd, 'usd')}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="font-semibold">{t('total', language)} ({t('sar', language)})</span>
          <span className="font-bold text-lg text-primary">
            {formatCurrency(costs.total_sar, 'sar')}
          </span>
        </div>
      </div>
    </div>
  );
};

export default CostSummaryCard;
