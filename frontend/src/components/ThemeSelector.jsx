import React from 'react';
import { useTheme, themes } from '@/context/ThemeContext';
import { Sun, Moon, Monitor, Sparkles, Check } from 'lucide-react';

const ThemeSelector = () => {
  const { theme, setTheme } = useTheme();

  const themeIcons = {
    dark: Moon,
    light: Sun,
    midnight: Monitor,
    jarvis: Sparkles
  };

  return (
    <div className="p-4">
      <h3 className="text-sm font-medium mb-3" style={{ color: 'var(--text-primary)' }}>
        Theme
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(themes).map(([key, t]) => {
          const Icon = themeIcons[key];
          const isActive = theme === key;
          return (
            <button
              key={key}
              onClick={() => setTheme(key)}
              className="flex items-center gap-3 p-3 rounded-lg border transition-all"
              style={{
                background: isActive ? t.accent + '20' : t.bgSecondary,
                borderColor: isActive ? t.accent : t.border,
              }}
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ background: t.bg, border: `2px solid ${t.accent}` }}
              >
                <Icon className="w-4 h-4" style={{ color: t.accent }} />
              </div>
              <div className="flex-1 text-left">
                <p className="text-sm font-medium" style={{ color: isActive ? t.accent : t.text }}>
                  {t.name}
                </p>
              </div>
              {isActive && (
                <Check className="w-4 h-4" style={{ color: t.accent }} />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ThemeSelector;
