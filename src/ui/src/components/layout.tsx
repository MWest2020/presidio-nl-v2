import { Header } from './header';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen w-full bg-gray-50">
      <Header />
  <main className="w-full mx-auto py-6 px-4 sm:py-8 sm:px-6 lg:py-10 lg:px-12">
        <div className="space-y-10">
          {children}
        </div>
      </main>
      <footer className="mt-auto w-full border-t bg-white/60 backdrop-blur supports-[backdrop-filter]:bg-white/40">
        <div className="mx-auto px-4 lg:px-12 py-6 text-xs sm:text-sm text-gray-500 flex flex-col sm:flex-row gap-2 sm:items-center justify-between">
          <span>&copy; {new Date().getFullYear()} OpenAnonymiser</span>
          <span className="hidden sm:inline">Secure document anonymization &amp; deanonymization</span>
        </div>
      </footer>
    </div>
  );
}
