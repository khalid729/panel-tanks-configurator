import { LanguageProvider } from '@/contexts/LanguageContext';
import Header from '@/components/Header';
import TankConfigurator from '@/components/TankConfigurator';

const Index = () => {
  return (
    <LanguageProvider>
      <div className="min-h-screen bg-background">
        <Header />
        <main>
          <TankConfigurator />
        </main>
        <footer className="border-t border-border py-4 mt-8">
          <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
            © {new Date().getFullYear()} Al Muhaidib National Tanks. All rights reserved.
          </div>
        </footer>
      </div>
    </LanguageProvider>
  );
};

export default Index;
