"use client";
import Image from "next/image";
import Link from "next/link";

export default function Header() {
  return (
    <header className="border-b">
      <div className="bg-western-purple text-white">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-3">
          <Image src="/logo.svg" alt="Western University" width={400} height={100} priority />
          <div className="leading-tight">
            <div className="text-sm opacity-90">Western University</div>
            <div className="text-base font-semibold">Expired U.S. Patents </div>
          </div>
          <div className="ml-auto text-xs opacity-90">
            <Link href="https://www.uwo.ca/" target="_blank" className="hover:underline">uwo.ca</Link>
          </div>
        </div>
      </div>
      <div className="border-t bg-white">
        <div className="mx-auto max-w-6xl px-4 py-2 text-sm text-gray-700">
          Open source (GPL-3.0) website
        </div>
      </div>
    </header>
  );
}