export type Language = 'en' | 'ar';

export const translations = {
  // Header
  title: {
    en: 'Tank Configuration System',
    ar: 'نظام تكوين الخزانات'
  },
  company: {
    en: 'Al Muhaidib National Tanks',
    ar: 'خزانات الوطني المهيدب'
  },
  
  // Common
  calculate: { en: 'Calculate', ar: 'احسب' },
  export: { en: 'Export', ar: 'تصدير' },
  save: { en: 'Save', ar: 'حفظ' },
  reset: { en: 'Reset', ar: 'إعادة تعيين' },
  loading: { en: 'Loading...', ar: 'جاري التحميل...' },
  
  // Sections
  dimensions: { en: 'Dimensions', ar: 'الأبعاد' },
  panelOptions: { en: 'Panel Options', ar: 'خيارات الألواح' },
  steelOptions: { en: 'Steel Options', ar: 'خيارات الفولاذ' },
  accessories: { en: 'Accessories', ar: 'الملحقات' },
  fittings: { en: 'Fittings', ar: 'التركيبات' },
  
  // Dimension Fields
  width: { en: 'Width', ar: 'العرض' },
  length: { en: 'Length', ar: 'الطول' },
  length1: { en: 'Length 1', ar: 'الطول 1' },
  length2: { en: 'Length 2', ar: 'الطول 2' },
  length3: { en: 'Length 3', ar: 'الطول 3' },
  length4: { en: 'Length 4', ar: 'الطول 4' },
  height: { en: 'Height', ar: 'الارتفاع' },
  quantity: { en: 'Quantity', ar: 'الكمية' },
  
  // Panel Options
  productType: { en: 'Product Type', ar: 'نوع المنتج' },
  insulation: { en: 'Insulation', ar: 'العزل' },
  sidePanel1x1: { en: '1×1 Side Panel', ar: 'لوح جانبي 1×1' },
  partitionPanel1x1: { en: '1×1 Partition Panel', ar: 'لوح فاصل 1×1' },
  
  // Steel Options
  reinforcingType: { en: 'Reinforcing Type', ar: 'نوع التعزيز' },
  internal: { en: 'Internal', ar: 'داخلي' },
  external: { en: 'External', ar: 'خارجي' },
  steelSkid: { en: 'Steel Skid', ar: 'قاعدة الفولاذ' },
  internalMaterial: { en: 'Internal Material', ar: 'المادة الداخلية' },
  boltsNuts: { en: 'Bolts & Nuts', ar: 'البراغي والصواميل' },
  tieRodMaterial: { en: 'Tie Rod Material', ar: 'مادة قضبان الربط' },
  tieRodSpec: { en: 'Tie Rod Spec', ar: 'مواصفات قضبان الربط' },
  
  // Accessories
  levelIndicator: { en: 'Level Indicator', ar: 'مؤشر المستوى' },
  internalLadder: { en: 'Internal Ladder', ar: 'سلم داخلي' },
  externalLadder: { en: 'External Ladder', ar: 'سلم خارجي' },
  material: { en: 'Material', ar: 'المادة' },
  
  // Fittings
  addFitting: { en: 'Add Fitting', ar: 'إضافة تركيب' },
  fittingType: { en: 'Fitting Type', ar: 'نوع التركيب' },
  position: { en: 'Position', ar: 'الموضع' },
  
  // Results
  results: { en: 'Results', ar: 'النتائج' },
  capacity: { en: 'Capacity', ar: 'السعة' },
  nominalCapacity: { en: 'Nominal Capacity', ar: 'السعة الاسمية' },
  actualCapacity: { en: 'Actual Capacity', ar: 'السعة الفعلية' },
  surfaceArea: { en: 'Surface Area', ar: 'مساحة السطح' },
  partitions: { en: 'Partitions', ar: 'الفواصل' },
  
  // Cost Summary
  costSummary: { en: 'Cost Summary', ar: 'ملخص التكلفة' },
  panels: { en: 'Panels', ar: 'الألواح' },
  steelSkidCost: { en: 'Steel Skid', ar: 'قاعدة الفولاذ' },
  bolts: { en: 'Bolts', ar: 'البراغي' },
  reinforcing: { en: 'Reinforcing', ar: 'التعزيز' },
  tieRods: { en: 'Tie Rods', ar: 'قضبان الربط' },
  etc: { en: 'ETC', ar: 'أخرى' },
  total: { en: 'Total', ar: 'المجموع' },
  
  // Weight Summary
  weightSummary: { en: 'Weight Summary', ar: 'ملخص الوزن' },
  steel: { en: 'Steel', ar: 'الفولاذ' },
  accessoriesWeight: { en: 'Accessories', ar: 'الملحقات' },
  totalWeight: { en: 'Total Weight', ar: 'الوزن الإجمالي' },
  
  // BOM
  bom: { en: 'Bill of Materials', ar: 'قائمة المواد' },
  partNo: { en: 'Part No.', ar: 'رقم القطعة' },
  partName: { en: 'Part Name', ar: 'اسم القطعة' },
  qty: { en: 'Qty', ar: 'الكمية' },
  unitPrice: { en: 'Unit Price', ar: 'سعر الوحدة' },
  totalPrice: { en: 'Total Price', ar: 'السعر الإجمالي' },
  weight: { en: 'Weight', ar: 'الوزن' },
  category: { en: 'Category', ar: 'الفئة' },
  
  // Units
  meters: { en: 'm', ar: 'م' },
  kg: { en: 'kg', ar: 'كجم' },
  usd: { en: 'USD', ar: 'دولار' },
  sar: { en: 'SAR', ar: 'ر.س' },
  cubicMeters: { en: 'm³', ar: 'م³' },
  squareMeters: { en: 'm²', ar: 'م²' },
  
  // Actions
  downloadPDF: { en: 'Download PDF', ar: 'تحميل PDF' },
  downloadExcel: { en: 'Download Excel', ar: 'تحميل Excel' },
  
  // Exchange Rate
  exchangeRate: { en: 'Exchange Rate', ar: 'سعر الصرف' },
} as const;

export type TranslationKey = keyof typeof translations;

export const t = (key: TranslationKey, lang: Language): string => {
  return translations[key][lang];
};
