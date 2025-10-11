import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Western University — Expired U.S. Patents",
  description: "Prototype search interface for maintenance-fee–expired U.S. patents.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased bg-white text-gray-900">
        {children}
      </body>
    </html>
  );
}