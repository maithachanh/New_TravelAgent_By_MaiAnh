import './globals.css';
import Navbar from '@/components/Navbar';
import { AppProvider } from '@/contexts/AppContext';

export const metadata = {
  title: 'AI Travel Agent - Hệ Thống Lập Kế Hoạch Du Lịch Toàn Cầu',
  description: 'Hệ thống Travel Agent AI thông minh hỗ trợ tất cả quốc gia & địa danh toàn cầu theo thời gian thực (LangGraph + OpenStreetMap + Frankfurter)',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body className="min-h-screen bg-slate-50 flex flex-col text-slate-900 antialiased">
        <AppProvider>
          <Navbar />
          <main className="flex-1 max-w-[1680px] w-full mx-auto p-3 sm:p-5 lg:p-6">
            {children}
          </main>
          <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
            © 2026 Universal AI Travel Agent System • Đồ Án Chuyên Sâu Next.js + FastAPI + LangGraph DAG + OpenStreetMap Geocoding + Frankfurter API
          </footer>
        </AppProvider>
      </body>
    </html>
  );
}
