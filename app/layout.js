import './globals.css'

export const metadata = {
  title: 'Himbhoomi | Properties in Himachal Pradesh',
  description: 'Discover premium properties across Himachal Pradesh with Himbhoomi.',
}

function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

export default RootLayout