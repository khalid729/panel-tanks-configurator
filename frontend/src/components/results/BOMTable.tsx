import { FileSpreadsheet } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';
import { BOMItem } from '@/types/tank';

interface BOMTableProps {
  items: BOMItem[];
}

const BOMTable = ({ items }: BOMTableProps) => {
  const { language, isRTL } = useLanguage();

  if (items.length === 0) {
    return (
      <div className="result-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-secondary" />
          {t('bom', language)}
        </h3>
        <p className="text-sm text-muted-foreground text-center py-8">
          {language === 'en'
            ? 'Bill of Materials will appear here after calculation'
            : 'ستظهر قائمة المواد هنا بعد الحساب'}
        </p>
      </div>
    );
  }

  return (
    <div className="result-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <FileSpreadsheet className="h-5 w-5 text-secondary" />
        {t('bom', language)}
        <span className="text-sm font-normal text-muted-foreground">
          ({items.length} {language === 'en' ? 'items' : 'عنصر'})
        </span>
      </h3>

      <ScrollArea className="h-[300px] rounded-md border">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className={isRTL ? 'text-right' : 'text-left'}>
                {t('partNo', language)}
              </TableHead>
              <TableHead className={isRTL ? 'text-right' : 'text-left'}>
                {t('partName', language)}
              </TableHead>
              <TableHead className="text-center">{t('qty', language)}</TableHead>
              <TableHead className={isRTL ? 'text-left' : 'text-right'}>
                {t('unitPrice', language)}
              </TableHead>
              <TableHead className={isRTL ? 'text-left' : 'text-right'}>
                {t('totalPrice', language)}
              </TableHead>
              <TableHead className={isRTL ? 'text-left' : 'text-right'}>
                {t('weight', language)}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item, index) => (
              <TableRow key={index} className="hover:bg-muted/30">
                <TableCell className="font-mono text-sm">{item.part_no}</TableCell>
                <TableCell>{item.part_name}</TableCell>
                <TableCell className="text-center font-medium">{item.quantity}</TableCell>
                <TableCell className={`${isRTL ? 'text-left' : 'text-right'} font-mono`}>
                  ${item.unit_price_usd.toFixed(2)}
                </TableCell>
                <TableCell className={`${isRTL ? 'text-left' : 'text-right'} font-mono font-medium`}>
                  ${item.total_price_usd.toFixed(2)}
                </TableCell>
                <TableCell className={`${isRTL ? 'text-left' : 'text-right'} text-muted-foreground`}>
                  {item.total_weight_kg.toFixed(1)} kg
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ScrollArea>
    </div>
  );
};

export default BOMTable;
