import '../styles/globals.css'
import { Providers } from '@/components/providers'

export const metadata = {
  title: 'USA Swing — Market Intelligence Platform',
  description: 'Institutional-grade swing trading predictions for all US equities',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&display=swap"
          rel="stylesheet"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content="#2A7A6F" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
