import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BookOpen, Search, Play, RefreshCw, FileCode, 
  ExternalLink, BarChart, CheckCircle, AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { API } from '@/App';

const ResearchPanel = () => {
  const [searches, setSearches] = useState([]);
  const [prototypes, setPrototypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [searchTopic, setSearchTopic] = useState('');
  const [selectedSearch, setSelectedSearch] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [searchesRes, prototypesRes] = await Promise.all([
        axios.get(`${API}/research/searches`),
        axios.get(`${API}/research/prototypes`)
      ]);
      setSearches(searchesRes.data || []);
      setPrototypes(prototypesRes.data || []);
    } catch (e) {
      console.error('Failed to fetch research data');
    }
    setLoading(false);
  };

  const searchArxiv = async () => {
    if (!searchTopic) return;
    
    setSearching(true);
    try {
      const res = await axios.post(`${API}/research/search`, {
        topic: searchTopic,
        categories: ["cs.AI", "cs.LG", "cs.SE"],
        max_papers: 10,
        auto_prototype: false
      });
      
      // Poll for results
      const pollResults = async () => {
        const searchRes = await axios.get(`${API}/research/search/${res.data.search_id}`);
        if (searchRes.data.status === 'completed') {
          setSelectedSearch(searchRes.data);
          fetchData();
          setSearching(false);
        } else {
          setTimeout(pollResults, 1000);
        }
      };
      
      setTimeout(pollResults, 1000);
    } catch (e) {
      console.error('Search failed');
      setSearching(false);
    }
  };

  const createPrototype = async (paperId) => {
    try {
      await axios.post(`${API}/research/prototype`, {
        paper_id: paperId,
        implementation_type: 'minimal'
      });
      fetchData();
    } catch (e) {
      console.error('Failed to create prototype');
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-blue-950/20 to-black" data-testid="research-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">RESEARCH MODE</h2>
              <p className="text-xs text-zinc-500">arXiv paper → Working prototype</p>
            </div>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={fetchData}
            className="text-zinc-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Search */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Search arXiv</h3>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                  <Input
                    value={searchTopic}
                    onChange={(e) => setSearchTopic(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && searchArxiv()}
                    placeholder="Search topic... (e.g., 'transformer attention')"
                    className="pl-10 bg-zinc-800/50 border-zinc-700"
                  />
                </div>
                <Button
                  onClick={searchArxiv}
                  disabled={searching || !searchTopic}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {searching ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Search Results */}
            {selectedSearch && selectedSearch.papers?.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">
                  Found {selectedSearch.papers.length} Papers
                </h3>
                <div className="space-y-3">
                  {selectedSearch.papers.map(paper => (
                    <div
                      key={paper.id}
                      className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-white mb-1 line-clamp-2">
                            {paper.title}
                          </h4>
                          <p className="text-xs text-zinc-500 mb-2">
                            {paper.authors?.join(', ')}
                          </p>
                          <p className="text-xs text-zinc-600 line-clamp-2 mb-3">
                            {paper.summary}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {paper.categories?.map((cat, i) => (
                              <Badge key={i} variant="outline" className="text-[10px]">
                                {cat}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          <Button
                            size="sm"
                            onClick={() => createPrototype(paper.id)}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            <Play className="w-3 h-3 mr-1" />
                            Build
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-zinc-700"
                            onClick={() => window.open(paper.pdf_url, '_blank')}
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            PDF
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Prototypes */}
            {prototypes.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">Built Prototypes</h3>
                <div className="space-y-3">
                  {prototypes.map(prototype => (
                    <div
                      key={prototype.id}
                      className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <FileCode className="w-5 h-5 text-blue-400" />
                          <div>
                            <p className="text-sm font-medium text-white">
                              {prototype.paper_title?.slice(0, 50)}...
                            </p>
                            <p className="text-xs text-zinc-500">
                              {new Date(prototype.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <Badge className={
                          prototype.status === 'completed'
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }>
                          {prototype.status}
                        </Badge>
                      </div>
                      
                      {prototype.stages && (
                        <div className="flex gap-1 mb-3">
                          {prototype.stages.map((stage, i) => (
                            <div
                              key={i}
                              className={`flex-1 h-1 rounded ${
                                stage.status === 'completed'
                                  ? 'bg-green-500'
                                  : stage.status === 'running'
                                    ? 'bg-blue-500 animate-pulse'
                                    : 'bg-zinc-700'
                              }`}
                            />
                          ))}
                        </div>
                      )}
                      
                      {prototype.code_files?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {prototype.code_files.map((file, i) => (
                            <span key={i} className="text-[10px] px-2 py-0.5 bg-zinc-800 rounded text-zinc-400">
                              {file.name}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Searches */}
            {searches.length > 0 && !selectedSearch && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">Recent Searches</h3>
                <div className="space-y-2">
                  {searches.slice(0, 5).map(search => (
                    <button
                      key={search.id}
                      onClick={() => setSelectedSearch(search)}
                      className="w-full p-3 bg-zinc-900/50 rounded-lg border border-zinc-800 hover:border-blue-500/50 text-left transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-white">{search.topic}</span>
                        <Badge variant="outline" className="text-[10px]">
                          {search.papers?.length || 0} papers
                        </Badge>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchPanel;
