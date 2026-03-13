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
    <div className="p-2">
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(themes).map(([key, t]) => {
          const Icon = themeIcons[key];
          const isActive = theme === key;
          return (
            <button
              key={key}
              onClick={() => setTheme(key)}
              data-testid={`theme-${key}`}
              className={`flex items-center gap-2 p-2 rounded-lg border transition-all ${
                isActive 
                  ? 'bg-cyan-500/20 border-cyan-500/50' 
                  : 'bg-zinc-800 border-zinc-700 hover:border-zinc-600'
              }`}
            >
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center"
                style={{ background: t.bg, border: `2px solid ${t.accent}` }}
              >
                <Icon className="w-3 h-3" style={{ color: t.accent }} />
              </div>
              <span className={`text-xs font-medium ${isActive ? 'text-cyan-400' : 'text-zinc-300'}`}>
                {t.name}
              </span>
              {isActive && (
                <Check className="w-3 h-3 ml-auto text-cyan-400" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ThemeSelector;
