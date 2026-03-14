import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'sonner';
import {
  ArrowLeft, Search, Globe, BookOpen, Github, ExternalLink,
  FileText, Code, Brain, Sparkles, Filter, RefreshCw, Star,
  Download, Bookmark, ChevronRight, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { API } from '@/App';

const SOURCES = [
  { id: 'arxiv', label: 'arXiv', icon: FileText, color: '#b31b1b' },
  { id: 'huggingface', label: 'HuggingFace', icon: Brain, color: '#ff9d00' },
  { id: 'paperswithcode', label: 'Papers', icon: Code, color: '#21cbff' },
  { id: 'github', label: 'GitHub', icon: Github, color: '#ffffff' },
];

const ResearchLab = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeSource, setActiveSource] = useState('arxiv');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [savedPapers, setSavedPapers] = useState([]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const res = await axios.post(`${API}/research/search`, {
        query: searchQuery,
        source: activeSource,
        limit: 20
      });
      setResults(res.data.results || []);
    } catch (error) {
      // Mock results for demo
      setResults([
        {
          id: '1',
          title: 'Attention Is All You Need',
          authors: ['Vaswani et al.'],
          abstract: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...',
          url: 'https://arxiv.org/abs/1706.03762',
          date: '2017-06-12',
          citations: 95000,
          source: 'arxiv'
        },
        {
          id: '2',
          title: 'BERT: Pre-training of Deep Bidirectional Transformers',
          authors: ['Devlin et al.'],
          abstract: 'We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers...',
          url: 'https://arxiv.org/abs/1810.04805',
          date: '2018-10-11',
          citations: 65000,
          source: 'arxiv'
        },
        {
          id: '3',
          title: 'GPT-4 Technical Report',
          authors: ['OpenAI'],
          abstract: 'We report the development of GPT-4, a large-scale, multimodal model which can accept image and text inputs...',
          url: 'https://arxiv.org/abs/2303.08774',
          date: '2023-03-15',
          citations: 5000,
          source: 'arxiv'
        }
      ]);
      toast.info('Using demo results');
    } finally {
      setLoading(false);
    }
  };

  const savePaper = (paper) => {
    if (savedPapers.find(p => p.id === paper.id)) {
      setSavedPapers(savedPapers.filter(p => p.id !== paper.id));
      toast.success('Removed from saved');
    } else {
      setSavedPapers([...savedPapers, paper]);
      toast.success('Saved to library');
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      {/* Background */}
      <div className="fixed inset-0 gradient-mesh opacity-20" />
      
      {/* Header */}
      <header className="relative z-10 border-b border-white/5 bg-[#09090b]/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate('/studio')}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-zinc-400" />
              </button>
              <div>
                <div className="flex items-center gap-3">
                  <BookOpen className="w-5 h-5 text-cyan-400" />
                  <h1 className="text-lg font-semibold text-white">Research Lab</h1>
                </div>
                <p className="text-sm text-zinc-500">Academic papers & models</p>
              </div>
            </div>
            
            {savedPapers.length > 0 && (
              <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
                <Bookmark className="w-3 h-3 mr-1" />
                {savedPapers.length} saved
              </Badge>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        {/* Search Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
              <Input
                placeholder="Search papers, models, code..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-12 py-6 bg-white/5 border-white/10 focus:border-cyan-500 text-base"
              />
            </div>
            <Button 
              onClick={handleSearch}
              disabled={loading}
              className="bg-cyan-500 hover:bg-cyan-600 px-6"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </Button>
          </div>
        </motion.div>

        {/* Source Tabs */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="flex gap-2">
            {SOURCES.map(source => (
              <button
                key={source.id}
                onClick={() => setActiveSource(source.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeSource === source.id
                    ? 'bg-white/10 text-white'
                    : 'text-zinc-500 hover:text-white hover:bg-white/5'
                }`}
              >
                <source.icon className="w-4 h-4" style={{ color: activeSource === source.id ? source.color : undefined }} />
                {source.label}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Results */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {results.length === 0 ? (
            <div className="text-center py-20">
              <BookOpen className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-zinc-400 mb-2">
                Search for papers and models
              </h3>
              <p className="text-sm text-zinc-600">
                Enter a topic to find relevant research
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((paper, idx) => (
                <motion.div
                  key={paper.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-medium text-white mb-2 group-hover:text-cyan-400 transition-colors">
                        {paper.title}
                      </h3>
                      <p className="text-sm text-zinc-500 mb-3">
                        {paper.authors?.join(', ')}
                      </p>
                      <p className="text-sm text-zinc-400 line-clamp-2 mb-4">
                        {paper.abstract}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-zinc-500">
                        <span>{paper.date}</span>
                        {paper.citations && (
                          <span className="flex items-center gap-1">
                            <Star className="w-3 h-3" />
                            {paper.citations.toLocaleString()} citations
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => savePaper(paper)}
                        className={savedPapers.find(p => p.id === paper.id) ? 'text-cyan-400' : 'text-zinc-400'}
                      >
                        <Bookmark className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(paper.url, '_blank')}
                        className="text-zinc-400 hover:text-white"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </main>
    </div>
  );
};

export default ResearchLab;
