import { useState, useEffect } from 'react'

export function useTheme() {
  // Artifact constraints: use React state rather than localStorage 
  // so it works cleanly in a sandboxed iframe without throwing DOM exceptions.
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
  }, [theme])

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light')

  return { theme, toggleTheme }
}
