import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const themes = {
  dark: {
    name: 'Dark Mode',
    bg: '#0a0a0c',
    bgSecondary: '#18181b',
    bgTertiary: '#27272a',
    border: '#3f3f46',
    text: '#fafafa',
    textSecondary: '#a1a1aa',
    textMuted: '#71717a',
    accent: '#3b82f6',
    accentHover: '#2563eb',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    card: 'rgba(24, 24, 27, 0.8)',
    glass: 'rgba(10, 10, 12, 0.9)',
  },
  light: {
    name: 'Light Mode',
    bg: '#fafafa',
    bgSecondary: '#f4f4f5',
    bgTertiary: '#e4e4e7',
    border: '#d4d4d8',
    text: '#18181b',
    textSecondary: '#52525b',
    textMuted: '#71717a',
    accent: '#2563eb',
    accentHover: '#1d4ed8',
    success: '#16a34a',
    warning: '#d97706',
    error: '#dc2626',
    card: 'rgba(255, 255, 255, 0.9)',
    glass: 'rgba(250, 250, 250, 0.95)',
  },
  midnight: {
    name: 'Midnight Blue',
    bg: '#0f172a',
    bgSecondary: '#1e293b',
    bgTertiary: '#334155',
    border: '#475569',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',
    accent: '#6366f1',
    accentHover: '#4f46e5',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#f43f5e',
    card: 'rgba(30, 41, 59, 0.9)',
    glass: 'rgba(15, 23, 42, 0.95)',
  },
  jarvis: {
    name: 'J.A.R.V.I.S.',
    bg: '#030712',
    bgSecondary: '#0c1222',
    bgTertiary: '#1a2744',
    border: '#1e3a5f',
    text: '#e0f2fe',
    textSecondary: '#7dd3fc',
    textMuted: '#38bdf8',
    accent: '#0ea5e9',
    accentHover: '#0284c7',
    success: '#22d3ee',
    warning: '#fbbf24',
    error: '#f87171',
    card: 'rgba(12, 18, 34, 0.9)',
    glass: 'rgba(3, 7, 18, 0.95)',
  }
};

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('agentforge-theme');
    return saved || 'dark';
  });

  useEffect(() => {
    localStorage.setItem('agentforge-theme', theme);
    const t = themes[theme];
    const root = document.documentElement;
    root.style.setProperty('--bg-primary', t.bg);
    root.style.setProperty('--bg-secondary', t.bgSecondary);
    root.style.setProperty('--bg-tertiary', t.bgTertiary);
    root.style.setProperty('--border-color', t.border);
    root.style.setProperty('--text-primary', t.text);
    root.style.setProperty('--text-secondary', t.textSecondary);
    root.style.setProperty('--text-muted', t.textMuted);
    root.style.setProperty('--accent', t.accent);
    root.style.setProperty('--accent-hover', t.accentHover);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, currentTheme: themes[theme] }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
