import { Globe } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/i18n/translations';
import logo from '@/assets/logo.png';

const Header = () => {
  const { language, setLanguage, isRTL } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'ar' : 'en');
  };

  return (
    <header className="bg-primary text-primary-foreground shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <img 
              src={logo} 
              alt="Al Muhaidib National Tanks" 
              className="h-12 w-auto"
            />
            <div className={isRTL ? 'text-right' : 'text-left'}>
              <h1 className="text-xl font-bold tracking-tight">
                {t('company', language)}
              </h1>
              <p className="text-sm text-primary-foreground/80">
                {t('title', language)}
              </p>
            </div>
          </div>

          {/* Language Toggle */}
          <button
            onClick={toggleLanguage}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-foreground/10 hover:bg-primary-foreground/20 transition-colors"
          >
            <Globe className="h-4 w-4" />
            <span className="font-medium">
              {language === 'en' ? 'العربية' : 'English'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
