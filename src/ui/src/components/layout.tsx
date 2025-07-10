import { Header } from './header';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen w-full bg-gray-50">
      <Header />
      <main className="container w-full mx-auto py-4 px-2 sm:py-6 sm:px-4 md:py-8 md:px-6">{children}</main>
    </div>
  );
}
