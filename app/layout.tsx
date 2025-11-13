import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
});

export const metadata: Metadata = {
  title: "ACL Guardian - Smart Injury Prevention",
  description: "AI-powered ACL injury prevention system using wearable data and machine learning to predict and prevent ACL injuries in athletes",
  keywords: "ACL injury prevention, sports medicine, wearable technology, Fitbit, injury prediction, athlete health, knee injury prevention",
  authors: [{ name: "ACL Guardian Team" }],
  icons: {
    icon: [
      { url: '/logo.png', type: 'image/png' },
      { url: '/favicon.ico', sizes: 'any' }
    ],
    apple: [
      { url: '/logo.png', sizes: '180x180', type: 'image/png' }
    ],
  },
  openGraph: {
    title: 'ACL Guardian - Smart Injury Prevention',
    description: 'AI-powered ACL injury prevention for athletes',
    type: 'website',
    siteName: 'ACL Guardian',
    images: ['/logo.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ACL Guardian - Smart Injury Prevention',
    description: 'AI-powered ACL injury prevention for athletes',
    images: ['/logo.png'],
  },
};

export function generateViewport() {
  return {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
    themeColor: '#0066CC',
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${poppins.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
