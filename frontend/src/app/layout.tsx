import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const satoshi = localFont({
  src: [
    { path: "../../public/fonts/satoshi/Satoshi-Light.woff2", weight: "300", style: "normal" },
    { path: "../../public/fonts/satoshi/Satoshi-Regular.woff2", weight: "400", style: "normal" },
    { path: "../../public/fonts/satoshi/Satoshi-Medium.woff2", weight: "500", style: "normal" },
    { path: "../../public/fonts/satoshi/Satoshi-Bold.woff2", weight: "700", style: "normal" },
    { path: "../../public/fonts/satoshi/Satoshi-Black.woff2", weight: "900", style: "normal" },
    { path: "../../public/fonts/satoshi/Satoshi-LightItalic.woff2", weight: "300", style: "italic" },
    { path: "../../public/fonts/satoshi/Satoshi-Italic.woff2", weight: "400", style: "italic" },
    { path: "../../public/fonts/satoshi/Satoshi-MediumItalic.woff2", weight: "500", style: "italic" },
    { path: "../../public/fonts/satoshi/Satoshi-BoldItalic.woff2", weight: "700", style: "italic" },
    { path: "../../public/fonts/satoshi/Satoshi-BlackItalic.woff2", weight: "900", style: "italic" },
  ],
  variable: "--font-satoshi",
  display: "swap",
});
const mono = localFont({ src: [{ path: "../../node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2", weight: "400" }, { path: "../../node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2", weight: "600" }], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = { title: { default: "Career Copilot", template: "%s · Career Copilot" }, description: "Your private career workspace for resumes, interviews, and next steps." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body className={`${satoshi.variable} ${mono.variable}`}>
        <a className="skip-link" href="#main-content">Skip to content</a>
        {children}
      </body>
    </html>
  );
}
