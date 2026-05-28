import type { Metadata } from "next";
import { JetBrains_Mono, Archivo_Black } from "next/font/google";
import "./globals.css";

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

const display = Archivo_Black({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "ELEVENTOOLS // CONSOLE",
  description: "Bulk text-to-speech generation console — developer-grade audio synthesis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`dark ${mono.variable} ${display.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
