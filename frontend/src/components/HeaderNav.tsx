"use client";

import { usePathname } from "next/navigation";

export default function HeaderNav() {
  const pathname = usePathname() || "/";

  // Hide header buttons on /about (and subpaths)
  if (pathname === "/about" || pathname.startsWith("/about/")) {
    return null;
  }

  return (
    <nav className="header-nav">
      <a href="/about" className="link-btn ghost" aria-label="About this site">
        About
      </a>
      <a
        href="https://uwo.ca"
        target="_blank"
        rel="noreferrer"
        className="link-btn ghost"
        aria-label="UWO HomePage"
      >
        UWO HomePage
      </a>
    </nav>
  );
}