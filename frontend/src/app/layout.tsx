import type { Metadata } from "next";
import "./globals.css";
import HeaderNav from "@/components/HeaderNav";

export const metadata: Metadata = {
  title: "Expired U.S. Patents — Western University",
  description: "Search lapsed U.S. patents by title (inactive for non-payment).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="brandbar" />
        <div className="container">
          <header className="header">
            <img src="/logo.svg" alt="Western" width={150} height={46} />
            <div className="titles">
              <div className="kicker">Western University</div>
              <div className="title">Expired U.S. Patents</div>
            </div>

            {/* Header buttons are conditionally shown via HeaderNav */}
            <HeaderNav />
          </header>
        </div>

        {children}
      </body>
    </html>
  );
}