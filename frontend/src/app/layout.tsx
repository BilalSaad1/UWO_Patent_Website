import type { Metadata } from "next";
import "./globals.css";
import HeaderNav from "@/components/HeaderNav";

export const metadata: Metadata = {
  title: "Free Inactive Patents II",
  description: "Search inactive U.S. patents (including age-expired ≥20 years).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="brandbar" />
        <div className="container">
          <header className="header">
            <img src="/logo.svg" alt="Western University" width={150} height={46} />
            <div className="titles">
              <div className="title">Free Inactive Patents II</div>
            </div>
            <HeaderNav />
          </header>
        </div>
        {children}
      </body>
    </html>
  );
}
