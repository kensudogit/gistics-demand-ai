import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Logistics Demand AI",
  description: "SKU×拠点の日次需要予測と容量・時間窓付き配送（デモ）",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
