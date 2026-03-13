import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Code, Search, Shield, Zap, AlertTriangle, CheckCircle, 
  RefreshCw, FileCode, Bug, Sparkles, ChevronDown, ChevronRight,
  XCircle, Info, AlertCircle, Eye
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { API } from '@/App';

const AIReviewPanel = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState('review');
  const [reviews, setReviews] = useState([]);
  const [currentReview, setCurrentReview] = useState(null);
  const [patterns, setPatterns] = useState({});
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(false);
  
  // Review options
  const [reviewType, setReviewType] = useState('full');
  const [severityThreshold, setSeverityThreshold] = useState('low');
  
  // Quick review
  const [codeContent, setCodeContent] = useState('');
  const [filename, setFilename] = useState('');
  const [quickResult, setQuickResult] = useState(null);

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reviewsRes, patternsRes] = await Promise.all([
        projectId ? axios.get(`${API}/ai-review/reviews/${projectId}`) : Promise.resolve({ data: [] }),
        axios.get(`${API}/ai-review/patterns`)
      ]);
      setReviews(reviewsRes.data || []);
      setPatterns(patternsRes.data || {});
    } catch (e) {
      console.error('Failed to fetch data:', e);
    }
    setLoading(false);
  };

  const startReview = async () => {
    if (!projectId) return;
    
    setReviewing(true);
    try {
      const res = await axios.post(`${API}/ai-review/review`, {
        project_id: projectId,
        review_type: reviewType,
        severity_threshold: severityThreshold
      });
      
      // Poll for completion
      const reviewId = res.data.review_id;
      pollReviewStatus(reviewId);
    } catch (e) {
      console.error('Failed to start review:', e);
      setReviewing(false);
    }
  };

  const pollReviewStatus = async (reviewId) => {
    const poll = async () => {
      try {
        const res = await axios.get(`${API}/ai-review/review/${reviewId}`);
        if (res.data.status === 'completed') {
          setCurrentReview(res.data);
          setReviewing(false);
          fetchData();
        } else if (res.data.status === 'analyzing') {
          setTimeout(poll, 2000);
        } else {
          setReviewing(false);
        }
      } catch (e) {
        setReviewing(false);
      }
    };
    poll();
  };

  const quickReview = async () => {
    if (!codeContent || !filename) return;
    
    setReviewing(true);
    try {
      const res = await axios.post(`${API}/ai-review/review-file`, {
        content: codeContent,
        filename: filename
      });
      setQuickResult(res.data);
    } catch (e) {
      console.error('Failed to review file:', e);
    }
    setReviewing(false);
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'high': return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'low': return <Info className="w-4 h-4 text-blue-500" />;
      default: return <Info className="w-4 h-4 text-zinc-500" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
      default: return 'bg-zinc-500/20 text-zinc-400 border-zinc-500/50';
    }
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return 'text-green-400';
      case 'B': return 'text-emerald-400';
      case 'C': return 'text-yellow-400';
      case 'D': return 'text-orange-400';
      case 'F': return 'text-red-400';
      default: return 'text-zinc-400';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-amber-950/20 to-black" data-testid="ai-review-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <Code className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">AI CODE REVIEW</h2>
              <p className="text-xs text-zinc-500">Intelligent code analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-amber-500/20 text-amber-400 text-xs">
              {Object.keys(patterns).length} Languages
            </Badge>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="flex-shrink-0 mx-6 mt-4 bg-zinc-900/50 p-1">
          <TabsTrigger value="review" className="flex-1 data-[state=active]:bg-amber-600">
            <Search className="w-4 h-4 mr-2" />
            Review
          </TabsTrigger>
          <TabsTrigger value="results" className="flex-1 data-[state=active]:bg-amber-600">
            <Bug className="w-4 h-4 mr-2" />
            Results
          </TabsTrigger>
          <TabsTrigger value="quick" className="flex-1 data-[state=active]:bg-amber-600">
            <Zap className="w-4 h-4 mr-2" />
            Quick Check
          </TabsTrigger>
          <TabsTrigger value="patterns" className="flex-1 data-[state=active]:bg-amber-600">
            <Sparkles className="w-4 h-4 mr-2" />
            Patterns
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-auto p-6">
          {/* Review Tab */}
          <TabsContent value="review" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Start Code Review</h3>
              
              <div className="space-y-4">
                {/* Review Type */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Review Type</label>
                  <div className="grid grid-cols-5 gap-2">
                    {[
                      { value: 'full', label: 'Full', icon: Search },
                      { value: 'security', label: 'Security', icon: Shield },
                      { value: 'performance', label: 'Performance', icon: Zap },
                      { value: 'style', label: 'Style', icon: Code },
                      { value: 'architecture', label: 'Architecture', icon: FileCode }
                    ].map(type => (
                      <button
                        key={type.value}
                        onClick={() => setReviewType(type.value)}
                        className={`p-3 rounded-lg border transition-all ${
                          reviewType === type.value
                            ? 'border-amber-500 bg-amber-500/10'
                            : 'border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <type.icon className={`w-4 h-4 mx-auto mb-1 ${
                          reviewType === type.value ? 'text-amber-400' : 'text-zinc-500'
                        }`} />
                        <p className="text-xs text-center">{type.label}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Severity Threshold */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Minimum Severity</label>
                  <Select value={severityThreshold} onValueChange={setSeverityThreshold}>
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low (All issues)</SelectItem>
                      <SelectItem value="medium">Medium+</SelectItem>
                      <SelectItem value="high">High+</SelectItem>
                      <SelectItem value="critical">Critical only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  onClick={startReview}
                  disabled={reviewing || !projectId}
                  className="w-full bg-amber-600 hover:bg-amber-700"
                >
                  {reviewing ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4 mr-2" />
                  )}
                  {projectId ? 'Start Review' : 'Select a project first'}
                </Button>
              </div>
            </div>

            {/* Previous Reviews */}
            {reviews.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">Previous Reviews</h3>
                <div className="space-y-2">
                  {reviews.slice(0, 5).map(review => (
                    <div
                      key={review.id}
                      className="p-3 bg-zinc-900/50 rounded-lg border border-zinc-800 flex items-center justify-between cursor-pointer hover:border-zinc-700"
                      onClick={() => {
                        setCurrentReview(review);
                        setActiveTab('results');
                      }}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`text-2xl font-bold ${getGradeColor(review.summary?.grade)}`}>
                          {review.summary?.grade || '-'}
                        </div>
                        <div>
                          <p className="text-sm text-white capitalize">{review.review_type} Review</p>
                          <p className="text-xs text-zinc-500">
                            {review.summary?.total_issues || 0} issues • {review.summary?.files_reviewed || 0} files
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-zinc-500" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="m-0 space-y-6">
            {currentReview ? (
              <>
                {/* Summary Card */}
                <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className={`text-5xl font-bold ${getGradeColor(currentReview.summary?.grade)}`}>
                        {currentReview.summary?.grade}
                      </div>
                      <div>
                        <p className="text-lg font-medium text-white">Health Score</p>
                        <p className="text-2xl font-bold text-white">{currentReview.summary?.health_score}/100</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-white">{currentReview.summary?.total_issues}</p>
                      <p className="text-sm text-zinc-500">Total Issues</p>
                    </div>
                  </div>

                  {/* Severity Breakdown */}
                  <div className="grid grid-cols-4 gap-3">
                    {['critical', 'high', 'medium', 'low'].map(severity => (
                      <div key={severity} className={`p-3 rounded-lg border ${getSeverityColor(severity)}`}>
                        <div className="flex items-center gap-2 mb-1">
                          {getSeverityIcon(severity)}
                          <span className="text-xs capitalize">{severity}</span>
                        </div>
                        <p className="text-xl font-bold">
                          {currentReview.summary?.severity_breakdown?.[severity] || 0}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Issues List */}
                <div>
                  <h3 className="text-sm font-medium text-white mb-3">
                    Issues Found ({currentReview.issues_found?.length || 0})
                  </h3>
                  <div className="space-y-2 max-h-96 overflow-auto">
                    {currentReview.issues_found?.map((issue, i) => (
                      <div
                        key={issue.id || i}
                        className="p-4 bg-zinc-900/50 rounded-lg border border-zinc-800"
                      >
                        <div className="flex items-start gap-3">
                          {getSeverityIcon(issue.severity)}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="text-sm font-medium text-white">{issue.message}</p>
                              <Badge variant="outline" className="text-xs">
                                {issue.category}
                              </Badge>
                            </div>
                            <p className="text-xs text-zinc-500 mb-2">
                              {issue.file}:{issue.line}
                            </p>
                            {issue.code && (
                              <div className="p-2 bg-black/50 rounded text-xs font-mono text-zinc-400 overflow-x-auto">
                                {issue.code}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <Bug className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-500">No review selected</p>
                <Button 
                  onClick={() => setActiveTab('review')} 
                  className="mt-4 bg-amber-600 hover:bg-amber-700"
                >
                  Start a Review
                </Button>
              </div>
            )}
          </TabsContent>

          {/* Quick Check Tab */}
          <TabsContent value="quick" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Quick Code Check</h3>
              
              <div className="space-y-4">
                <Input
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="filename.js"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Textarea
                  value={codeContent}
                  onChange={(e) => setCodeContent(e.target.value)}
                  placeholder="Paste your code here..."
                  className="bg-zinc-800/50 border-zinc-700 h-48 font-mono text-sm"
                />

                <Button
                  onClick={quickReview}
                  disabled={reviewing || !codeContent || !filename}
                  className="w-full bg-amber-600 hover:bg-amber-700"
                >
                  {reviewing ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4 mr-2" />
                  )}
                  Analyze Code
                </Button>
              </div>
            </div>

            {/* Quick Result */}
            {quickResult && (
              <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-white">Results for {quickResult.filename}</h3>
                  <div className={`text-2xl font-bold ${getGradeColor(quickResult.summary?.grade)}`}>
                    {quickResult.summary?.grade}
                  </div>
                </div>
                
                <div className="space-y-2">
                  {quickResult.issues?.map((issue, i) => (
                    <div key={i} className="flex items-start gap-2 p-2 bg-zinc-800/50 rounded">
                      {getSeverityIcon(issue.severity)}
                      <div>
                        <p className="text-sm text-white">{issue.message}</p>
                        <p className="text-xs text-zinc-500">Line {issue.line}</p>
                      </div>
                    </div>
                  ))}
                  {quickResult.issues?.length === 0 && (
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm">No issues found!</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </TabsContent>

          {/* Patterns Tab */}
          <TabsContent value="patterns" className="m-0 space-y-4">
            {Object.entries(patterns).map(([lang, langPatterns]) => (
              <div key={lang} className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
                <h3 className="text-sm font-medium text-white mb-3 capitalize">{lang} Patterns</h3>
                <div className="space-y-2">
                  {langPatterns?.map((pattern, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-zinc-800/30 rounded">
                      <div className="flex items-center gap-2">
                        {getSeverityIcon(pattern.severity)}
                        <span className="text-sm text-zinc-300">{pattern.message}</span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {pattern.category}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default AIReviewPanel;
