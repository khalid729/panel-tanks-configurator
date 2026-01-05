import { useState, useMemo } from 'react';
import { FileSpreadsheet, Filter, ChevronDown, ChevronUp } from 'lucide-react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { BOMItem } from '@/types/tank';

interface BOMTableProps {
  items: BOMItem[];
}

type SortField = 'part_no' | 'quantity' | 'total_price_usd' | 'total_weight_kg';
type SortDirection = 'asc' | 'desc';

const CATEGORY_COLORS: Record<string, string> = {
  'Panels': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  'Steel Skid': 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  'Bolts & Nuts': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  'External Reinforcing': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  'Internal Reinforcing': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
  'Internal Tie-rod': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  'Tie Rods': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  'Tie Rod Accessories': 'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200',
  'ETC': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  'Etc': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  'Fittings': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
};

const BOMTable = ({ items }: BOMTableProps) => {
  const { language, isRTL } = useLanguage();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('part_no');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  // Get unique categories
  const categories = useMemo(() => {
    const cats = [...new Set(items.map(item => item.category))];
    return cats.sort();
  }, [items]);

  // Filter and sort items
  const filteredItems = useMemo(() => {
    let result = selectedCategory === 'all'
      ? items
      : items.filter(item => item.category === selectedCategory);

    // Sort
    result = [...result].sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case 'part_no':
          comparison = a.part_no.localeCompare(b.part_no);
          break;
        case 'quantity':
          comparison = a.quantity - b.quantity;
          break;
        case 'total_price_usd':
          comparison = a.total_price_usd - b.total_price_usd;
          break;
        case 'total_weight_kg':
          comparison = a.total_weight_kg - b.total_weight_kg;
          break;
      }
      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [items, selectedCategory, sortField, sortDirection]);

  // Calculate totals for filtered items
  const totals = useMemo(() => {
    return {
      quantity: filteredItems.reduce((sum, item) => sum + item.quantity, 0),
      price: filteredItems.reduce((sum, item) => sum + item.total_price_usd, 0),
      weight: filteredItems.reduce((sum, item) => sum + item.total_weight_kg, 0),
    };
  }, [filteredItems]);

  // Handle sort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc'
      ? <ChevronUp className="h-3 w-3 inline ml-1" />
      : <ChevronDown className="h-3 w-3 inline ml-1" />;
  };

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
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-secondary" />
          {t('bom', language)}
          <span className="text-sm font-normal text-muted-foreground">
            ({filteredItems.length} {language === 'en' ? 'items' : 'عنصر'})
          </span>
        </h3>

        {/* Category Filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-[180px] h-8 text-sm">
              <SelectValue placeholder={language === 'en' ? 'Filter by category' : 'فلترة حسب الفئة'} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">
                {language === 'en' ? 'All Categories' : 'جميع الفئات'}
              </SelectItem>
              {categories.map(cat => (
                <SelectItem key={cat} value={cat}>{cat}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <ScrollArea className="h-[350px] rounded-md border">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className={isRTL ? 'text-right' : 'text-left'}>
                {language === 'en' ? 'Category' : 'الفئة'}
              </TableHead>
              <TableHead
                className={`${isRTL ? 'text-right' : 'text-left'} cursor-pointer hover:bg-muted/70`}
                onClick={() => handleSort('part_no')}
              >
                {t('partNo', language)}
                <SortIcon field="part_no" />
              </TableHead>
              <TableHead className={isRTL ? 'text-right' : 'text-left'}>
                {t('partName', language)}
              </TableHead>
              <TableHead
                className="text-center cursor-pointer hover:bg-muted/70"
                onClick={() => handleSort('quantity')}
              >
                {t('qty', language)}
                <SortIcon field="quantity" />
              </TableHead>
              <TableHead className={isRTL ? 'text-left' : 'text-right'}>
                {t('unitPrice', language)}
              </TableHead>
              <TableHead
                className={`${isRTL ? 'text-left' : 'text-right'} cursor-pointer hover:bg-muted/70`}
                onClick={() => handleSort('total_price_usd')}
              >
                {t('totalPrice', language)}
                <SortIcon field="total_price_usd" />
              </TableHead>
              <TableHead
                className={`${isRTL ? 'text-left' : 'text-right'} cursor-pointer hover:bg-muted/70`}
                onClick={() => handleSort('total_weight_kg')}
              >
                {t('weight', language)}
                <SortIcon field="total_weight_kg" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((item, index) => (
              <TableRow key={index} className="hover:bg-muted/30">
                <TableCell>
                  <Badge
                    variant="secondary"
                    className={`text-xs ${CATEGORY_COLORS[item.category] || 'bg-gray-100'}`}
                  >
                    {item.category}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-sm">{item.part_no}</TableCell>
                <TableCell className="text-sm">{item.part_name}</TableCell>
                <TableCell className="text-center font-medium">{item.quantity}</TableCell>
                <TableCell className={`${isRTL ? 'text-left' : 'text-right'} font-mono text-sm`}>
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

            {/* Totals Row */}
            <TableRow className="bg-muted/70 font-semibold border-t-2">
              <TableCell colSpan={3} className={isRTL ? 'text-right' : 'text-left'}>
                {language === 'en' ? 'Total' : 'المجموع'}
              </TableCell>
              <TableCell className="text-center">{totals.quantity.toLocaleString()}</TableCell>
              <TableCell></TableCell>
              <TableCell className={`${isRTL ? 'text-left' : 'text-right'} font-mono`}>
                ${totals.price.toFixed(2)}
              </TableCell>
              <TableCell className={`${isRTL ? 'text-left' : 'text-right'}`}>
                {totals.weight.toFixed(1)} kg
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </ScrollArea>
    </div>
  );
};

export default BOMTable;
