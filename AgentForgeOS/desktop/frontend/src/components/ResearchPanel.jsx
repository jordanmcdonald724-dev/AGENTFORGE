import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const ResearchPanel = () => {
  const [activeTab, setActiveTab] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchSource, setSearchSource] = useState('arxiv');
  const [results, setResults] = useState([]);
  const [prototypes, setPrototypes] = useState([]);
  const [sources, setSources] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedPaper, setSelectedPaper] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [sourcesRes, prototypesRes] = await Promise.all([
        axios.get(`${API}/api/research/sources`),
        axios.get(`${API}/api/research/prototypes`)
      ]);
      setSources(sourcesRes.data || {});
      setPrototypes(prototypesRes.data || []);
    } catch (e) {}
  };

  const search = async () => {
    if (!searchQuery) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/research/search`, {
        query: searchQuery,
        source: searchSource,
        max_results: 10
      });
      setResults(res.data.results || []);
    } catch (e) {}
    setLoading(false);
  };

  const createPrototype = async (paper) => {
    try {
      await axios.post(`${API}/api/research/prototype`, {
        paper_id: paper.id,
        source: paper.source,
        title: paper.title,
        framework: 'pytorch'
      });
      fetchData();
      setActiveTab('prototypes');
    } catch (e) {}
  };

  return (
    <div style={{ padding: 20, background: '#1a1a2e', borderRadius: 12, color: 'white' }}>
      <h2 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 24 }}>📚</span> Research Mode
        <span style={{ fontSize: 12, background: '#3b82f6', padding: '2px 8px', borderRadius: 4 }}>arXiv • PapersWithCode • HuggingFace</span>
      </h2>

      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        {['search', 'prototypes'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              background: activeTab === tab ? '#3b82f6' : '#2d2d44',
              border: 'none',
              borderRadius: 6,
              color: 'white',
              cursor: 'pointer',
              textTransform: 'capitalize'
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'search' && (
        <div>
          <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
            <select
              value={searchSource}
              onChange={e => setSearchSource(e.target.value)}
              style={{ padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white' }}
            >
              <option value="arxiv">arXiv</option>
              <option value="paperswithcode">Papers With Code</option>
              <option value="huggingface">HuggingFace Models</option>
            </select>
            <input
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && search()}
              placeholder="Search papers, models..."
              style={{ flex: 1, padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white' }}
            />
            <button
              onClick={search}
              disabled={loading}
              style={{ padding: '12px 24px', background: '#3b82f6', border: 'none', borderRadius: 6, color: 'white', cursor: 'pointer' }}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Source Info */}
          {sources[searchSource] && (
            <div style={{ background: '#2d2d44', padding: 12, borderRadius: 8, marginBottom: 20 }}>
              <strong>{sources[searchSource].name}</strong>
              <p style={{ fontSize: 12, color: '#888', marginTop: 4 }}>{sources[searchSource].description}</p>
            </div>
          )}

          {/* Results */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {results.map((paper, i) => (
              <div
                key={i}
                style={{
                  background: selectedPaper?.id === paper.id ? '#3b82f620' : '#2d2d44',
                  padding: 15,
                  borderRadius: 8,
                  border: selectedPaper?.id === paper.id ? '1px solid #3b82f6' : '1px solid transparent',
                  cursor: 'pointer'
                }}
                onClick={() => setSelectedPaper(paper)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: 14 }}>{paper.title}</strong>
                    {paper.authors && (
                      <p style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                        {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 && ' et al.'}
                      </p>
                    )}
                    <p style={{ fontSize: 12, color: '#aaa', marginTop: 8, lineHeight: 1.4 }}>
                      {paper.summary?.slice(0, 200)}...
                    </p>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginLeft: 10 }}>
                    <span style={{ fontSize: 10, background: '#3b82f6', padding: '2px 6px', borderRadius: 4 }}>
                      {paper.source}
                    </span>
                    {paper.downloads && (
                      <span style={{ fontSize: 10, color: '#888' }}>↓ {paper.downloads.toLocaleString()}</span>
                    )}
                  </div>
                </div>
                {selectedPaper?.id === paper.id && (
                  <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #444', display: 'flex', gap: 10 }}>
                    <button
                      onClick={(e) => { e.stopPropagation(); createPrototype(paper); }}
                      style={{ padding: '8px 16px', background: '#10b981', border: 'none', borderRadius: 4, color: 'white', cursor: 'pointer', fontSize: 12 }}
                    >
                      Create Prototype
                    </button>
                    <a
                      href={paper.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={e => e.stopPropagation()}
                      style={{ padding: '8px 16px', background: '#2d2d44', border: 'none', borderRadius: 4, color: 'white', textDecoration: 'none', fontSize: 12 }}
                    >
                      View Paper
                    </a>
                  </div>
                )}
              </div>
            ))}
            {results.length === 0 && !loading && searchQuery && (
              <p style={{ color: '#888', textAlign: 'center' }}>No results found</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'prototypes' && (
        <div>
          {prototypes.length === 0 ? (
            <p style={{ color: '#888' }}>No prototypes created yet. Search for papers and create one!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {prototypes.map(p => (
                <div key={p.id} style={{ background: '#2d2d44', padding: 15, borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong>{p.title}</strong>
                      <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                        <span style={{ fontSize: 11, background: '#3b82f6', padding: '2px 6px', borderRadius: 4 }}>{p.source}</span>
                        <span style={{ fontSize: 11, background: '#10b981', padding: '2px 6px', borderRadius: 4 }}>{p.framework}</span>
                      </div>
                    </div>
                  </div>
                  {p.code && (
                    <pre style={{
                      marginTop: 12,
                      background: '#0d0d1a',
                      padding: 12,
                      borderRadius: 6,
                      overflow: 'auto',
                      maxHeight: 200,
                      fontSize: 11,
                      fontFamily: 'monospace'
                    }}>
                      {p.code}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResearchPanel;
