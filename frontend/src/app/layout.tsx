import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';
import { AppProvider } from '@/contexts/AppContext';

export const metadata: Metadata = {
  title: 'TravelAgent AI | Lập kế hoạch chuyến đi',
  description: 'Trợ lý lập kế hoạch du lịch với lịch trình, đổi tiền tệ và dịch câu giao tiếp.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="vi">
      <body className="min-h-screen text-slate-900 antialiased">
        <AppProvider>
          <Navbar />
          <main className="mx-auto w-full max-w-[1680px] flex-1 px-3 py-4 sm:px-5 sm:py-6 lg:px-7">{children}</main>
          <footer className="mt-6 border-t border-slate-200/80 bg-white/70 py-6 text-center text-xs text-slate-500">© 2026 TravelAgent AI · Lập kế hoạch hành trình dễ hiểu và linh hoạt</footer>
        </AppProvider>
      </body>
    </html>
  );
}
