/**
 * QuickActionsPanel Component
 * ===========================
 * Displays quick action cards for common operations
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const QUICK_ACTION_ICONS = {
  layout: require('lucide-react').Layers,
  gamepad: require('lucide-react').Gamepad2,
  package: require('lucide-react').Package,
  save: require('lucide-react').Save,
  heart: require('lucide-react').Heart,
  bot: require('lucide-react').Bot
};

const QuickActionsPanel = ({ 
  quickActions, 
  isCollapsed, 
  onToggleCollapse, 
  onExecuteAction,
  isExecuting,
  executingActionId 
}) => {
  return (
    <div className="flex-shrink-0 border-b transition-colors duration-300" style={{ borderColor: 'var(--border-color)' }}>
      <button
        onClick={onToggleCollapse}
        className="w-full px-4 py-2 flex items-center justify-between hover:bg-zinc-800/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4" style={{ color: 'var(--accent)' }} />
          <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Quick Actions</span>
          <Badge className="text-[10px]" style={{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }}>
            {quickActions.length}
          </Badge>
        </div>
        {isCollapsed ? (
          <ChevronDown className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
        ) : (
          <ChevronUp className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
        )}
      </button>
      
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 grid grid-cols-2 sm:grid-cols-3 gap-2">
              {quickActions.slice(0, 6).map((action) => {
                const IconComponent = QUICK_ACTION_ICONS[action.icon] || QUICK_ACTION_ICONS.layout;
                const isThisExecuting = isExecuting && executingActionId === action.id;
                return (
                  <Button
                    key={action.id}
                    variant="outline"
                    size="sm"
                    onClick={() => onExecuteAction(action)}
                    disabled={isExecuting}
                    className="justify-start h-auto py-2 px-3 text-left transition-all hover:scale-[1.02]"
                    style={{ 
                      borderColor: 'var(--border-color)',
                      backgroundColor: isThisExecuting ? 'color-mix(in srgb, var(--accent) 10%, transparent)' : 'transparent'
                    }}
                    data-testid={`quick-action-${action.id}`}
                  >
                    <IconComponent className="w-4 h-4 mr-2 flex-shrink-0" style={{ color: 'var(--accent)' }} />
                    <span className="text-xs truncate" style={{ color: 'var(--text-secondary)' }}>
                      {action.name}
                    </span>
                  </Button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default QuickActionsPanel;
