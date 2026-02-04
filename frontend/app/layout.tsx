import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'MentorMind - AI Evaluator Training',
  description: 'Train your AI evaluation skills with objective feedback from GPT-4o',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-50`}
      >
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <div className="flex-1 ml-64">
            <Header />
            <main className="p-8">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
