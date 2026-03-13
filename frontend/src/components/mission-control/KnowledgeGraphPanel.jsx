import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Database, Network, Search, RefreshCw, ChevronRight,
  Code, Layout, Server, Cloud, Gamepad2, BookOpen
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { API } from '@/App';

const CATEGORY_ICONS = {
  frontend: Layout,
  backend: Server,
  database: Database,
  infrastructure: Cloud,
  game_dev: Gamepad2
};

const CATEGORY_COLORS = {
  frontend: '#8b5cf6',
  backend: '#06b6d4',
  database: '#22c55e',
  infrastructure: '#f59e0b',
  game_dev: '#ec4899'
};

const KnowledgeGraphPanel = () => {
  const [graph, setGraph] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedTech, setSelectedTech] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    fetchKnowledgeGraph();
  }, []);

  const fetchKnowledgeGraph = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/intelligence/knowledge-graph`);
      setGraph(res.data.graph);
      setStats(res.data.stats);
    } catch (e) {
      console.error('Failed to fetch knowledge graph');
    }
    setLoading(false);
  };

  const searchKnowledge = async () => {
    if (!searchQuery.trim()) return;
    try {
      const res = await axios.post(`${API}/intelligence/knowledge-graph/query?query=${encodeURIComponent(searchQuery)}&limit=10`);
      setSearchResults(res.data);
    } catch (e) {
      console.error('Search failed');
    }
  };

  const handleCategoryClick = (category) => {
    setSelectedCategory(category === selectedCategory ? null : category);
    setSelectedTech(null);
  };

  const handleTechClick = (tech) => {
    setSelectedTech(tech === selectedTech ? null : tech);
  };

  return (
    <div className="h-full flex flex-col bg-black/90 backdrop-blur-xl" data-testid="knowledge-graph-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50 bg-gradient-to-r from-pink-900/20 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">KNOWLEDGE GRAPH</h2>
              <p className="text-xs text-zinc-500">Global software pattern memory</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {stats && (
              <>
                <Badge className="bg-pink-500/20 text-pink-400 text-xs">
                  {stats.categories} Categories
                </Badge>
                <Badge className="bg-purple-500/20 text-purple-400 text-xs">
                  {stats.total_patterns} Patterns
                </Badge>
              </>
            )}
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={fetchKnowledgeGraph}
              className="text-zinc-400 hover:text-white"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="px-6 py-4 border-b border-zinc-800/50">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && searchKnowledge()}
            placeholder="Search patterns... (e.g., 'auth', 'react hooks', 'docker')"
            className="pl-12 bg-zinc-900/50 border-zinc-700 focus:border-pink-500"
          />
        </div>
        
        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-4 space-y-2 max-h-48 overflow-auto">
            {searchResults.map((result, i) => (
              <div key={i} className="p-3 bg-zinc-900/50 rounded-lg border border-zinc-800">
                <div className="flex items-center gap-2 mb-1">
                  <Badge 
                    className="text-[10px]"
                    style={{ 
                      backgroundColor: `${CATEGORY_COLORS[result.category] || '#6b7280'}20`,
                      color: CATEGORY_COLORS[result.category] || '#6b7280'
                    }}
                  >
                    {result.category}
                  </Badge>
                  <Badge variant="outline" className="text-[10px]">
                    {result.tech}
                  </Badge>
                  <span className="text-xs text-zinc-500 ml-auto">Score: {result.score}</span>
                </div>
                <div className="text-sm text-white font-medium">{result.pattern.pattern}</div>
                <div className="text-xs text-zinc-500">{result.pattern.description}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <RefreshCw className="w-8 h-8 text-pink-500 animate-spin" />
          </div>
        ) : (
          <>
            {/* Categories Sidebar */}
            <div className="w-64 border-r border-zinc-800/50 p-4 overflow-auto">
              <div className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Categories</div>
              <div className="space-y-2">
                {graph && Object.keys(graph).map(category => {
                  const Icon = CATEGORY_ICONS[category] || Code;
                  const isSelected = selectedCategory === category;
                  const techCount = Object.keys(graph[category]).length;
                  const patternCount = Object.values(graph[category]).flat().length;
                  
                  return (
                    <div key={category}>
                      <button
                        onClick={() => handleCategoryClick(category)}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                          isSelected 
                            ? 'bg-zinc-800/80 border border-zinc-700' 
                            : 'hover:bg-zinc-900/50 border border-transparent'
                        }`}
                      >
                        <div 
                          className="w-8 h-8 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: `${CATEGORY_COLORS[category] || '#6b7280'}20` }}
                        >
                          <Icon className="w-4 h-4" style={{ color: CATEGORY_COLORS[category] || '#6b7280' }} />
                        </div>
                        <div className="flex-1 text-left">
                          <div className="text-sm font-medium text-white capitalize">{category.replace('_', ' ')}</div>
                          <div className="text-xs text-zinc-500">{techCount} techs, {patternCount} patterns</div>
                        </div>
                        <ChevronRight className={`w-4 h-4 text-zinc-600 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
                      </button>
                      
                      {/* Technologies Sub-menu */}
                      {isSelected && (
                        <div className="ml-4 mt-2 space-y-1">
                          {Object.keys(graph[category]).map(tech => (
                            <button
                              key={tech}
                              onClick={() => handleTechClick(tech)}
                              className={`w-full flex items-center gap-2 p-2 rounded-lg text-left transition-all ${
                                selectedTech === tech 
                                  ? 'bg-zinc-800 text-white' 
                                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
                              }`}
                            >
                              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[category] }} />
                              <span className="text-sm capitalize">{tech}</span>
                              <span className="text-xs text-zinc-600 ml-auto">
                                {graph[category][tech].length}
                              </span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Patterns Display */}
            <div className="flex-1 p-6 overflow-auto">
              {selectedTech && selectedCategory ? (
                <div>
                  <div className="flex items-center gap-2 mb-6">
                    <BookOpen className="w-5 h-5 text-zinc-400" />
                    <h3 className="text-lg font-bold text-white capitalize">{selectedTech} Patterns</h3>
                  </div>
                  
                  <div className="grid gap-4">
                    {graph[selectedCategory][selectedTech].map((pattern, i) => (
                      <div key={i} className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                        <div className="flex items-center gap-2 mb-2">
                          <div 
                            className="w-2 h-2 rounded-full" 
                            style={{ backgroundColor: CATEGORY_COLORS[selectedCategory] }}
                          />
                          <h4 className="font-bold text-white capitalize">{pattern.pattern}</h4>
                        </div>
                        <p className="text-sm text-zinc-400 mb-3">{pattern.description}</p>
                        <div className="flex flex-wrap gap-1.5">
                          {pattern.examples?.map((example, j) => (
                            <Badge key={j} variant="outline" className="text-xs border-zinc-700 text-zinc-400">
                              {example}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Network className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-zinc-400">Select a category and technology</h3>
                    <p className="text-sm text-zinc-600 mt-1">to explore software patterns</p>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default KnowledgeGraphPanel;
