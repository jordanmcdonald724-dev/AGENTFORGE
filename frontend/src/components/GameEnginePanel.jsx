import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const GameEnginePanel = () => {
  const [activeTab, setActiveTab] = useState('projects');
  const [projects, setProjects] = useState([]);
  const [builds, setBuilds] = useState([]);
  const [engines, setEngines] = useState({ unreal: [], unity: [] });
  const [loading, setLoading] = useState(true);
  
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [selectedEngine, setSelectedEngine] = useState('unreal');
  const [template, setTemplate] = useState('blank');
  const [templates, setTemplates] = useState({});
  
  const [unrealPath, setUnrealPath] = useState('');
  const [unityPath, setUnityPath] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedEngine) {
      axios.get(`${API}/api/game-engine/templates/${selectedEngine}`)
        .then(res => setTemplates(res.data || {}))
        .catch(() => {});
    }
  }, [selectedEngine]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [projectsRes, buildsRes, enginesRes] = await Promise.all([
        axios.get(`${API}/api/game-engine/projects`),
        axios.get(`${API}/api/game-engine/builds`),
        axios.get(`${API}/api/game-engine/detect`)
      ]);
      setProjects(projectsRes.data || []);
      setBuilds(buildsRes.data || []);
      setEngines(enginesRes.data || { unreal: [], unity: [] });
    } catch (e) {}
    setLoading(false);
  };

  const createProject = async () => {
    if (!projectName) return;
    try {
      await axios.post(`${API}/api/game-engine/projects`, {
        name: projectName,
        description: projectDesc,
        engine: selectedEngine,
        template
      });
      setProjectName('');
      setProjectDesc('');
      fetchData();
    } catch (e) {}
  };

  const startBuild = async (projectId) => {
    try {
      await axios.post(`${API}/api/game-engine/build`, { project_id: projectId });
      fetchData();
    } catch (e) {}
  };

  const savePaths = async () => {
    try {
      await axios.post(`${API}/api/game-engine/config`, {
        unreal_path: unrealPath,
        unity_path: unityPath
      });
      fetchData();
    } catch (e) {}
  };

  return (
    <div style={{ padding: 20, background: '#1a1a2e', borderRadius: 12, color: 'white' }}>
      <h2 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 24 }}>🎮</span> Game Engine Builder
        <span style={{ fontSize: 12, background: '#8b5cf6', padding: '2px 8px', borderRadius: 4 }}>UE5 + Unity</span>
      </h2>

      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        {['projects', 'builds', 'create', 'config'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              background: activeTab === tab ? '#8b5cf6' : '#2d2d44',
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

      {activeTab === 'projects' && (
        <div>
          {loading ? <p>Loading...</p> : projects.length === 0 ? (
            <p style={{ color: '#888' }}>No projects yet. Create one!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {projects.map(p => (
                <div key={p.id} style={{ background: '#2d2d44', padding: 15, borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong>{p.name}</strong>
                      <span style={{ marginLeft: 10, fontSize: 12, color: '#888' }}>
                        {p.engine === 'unreal' ? '🎮 Unreal' : '🔷 Unity'} • {p.template}
                      </span>
                    </div>
                    <button
                      onClick={() => startBuild(p.id)}
                      style={{ padding: '6px 12px', background: '#10b981', border: 'none', borderRadius: 4, color: 'white', cursor: 'pointer' }}
                    >
                      Build
                    </button>
                  </div>
                  {p.description && <p style={{ fontSize: 12, color: '#aaa', marginTop: 8 }}>{p.description}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'builds' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {builds.length === 0 ? <p style={{ color: '#888' }}>No builds yet</p> : builds.map(b => (
            <div key={b.id} style={{ background: '#2d2d44', padding: 15, borderRadius: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <strong>{b.project_name}</strong>
                <span style={{
                  padding: '2px 8px',
                  borderRadius: 4,
                  fontSize: 12,
                  background: b.status === 'completed' ? '#10b981' : b.status === 'building' ? '#3b82f6' : '#f59e0b'
                }}>
                  {b.status} {b.progress > 0 && b.progress < 100 && `${b.progress}%`}
                </span>
              </div>
              {b.logs && b.logs.length > 0 && (
                <div style={{ marginTop: 10, padding: 10, background: '#1a1a2e', borderRadius: 4, maxHeight: 100, overflow: 'auto' }}>
                  {b.logs.slice(-5).map((log, i) => (
                    <div key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#888' }}>{log}</div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'create' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={() => setSelectedEngine('unreal')}
              style={{
                flex: 1,
                padding: 20,
                background: selectedEngine === 'unreal' ? '#8b5cf620' : '#2d2d44',
                border: selectedEngine === 'unreal' ? '2px solid #8b5cf6' : '2px solid transparent',
                borderRadius: 8,
                color: 'white',
                cursor: 'pointer'
              }}
            >
              <div style={{ fontSize: 24, marginBottom: 8 }}>🎮</div>
              <strong>Unreal Engine 5</strong>
              <p style={{ fontSize: 12, color: '#888', marginTop: 4 }}>AAA quality games</p>
            </button>
            <button
              onClick={() => setSelectedEngine('unity')}
              style={{
                flex: 1,
                padding: 20,
                background: selectedEngine === 'unity' ? '#3b82f620' : '#2d2d44',
                border: selectedEngine === 'unity' ? '2px solid #3b82f6' : '2px solid transparent',
                borderRadius: 8,
                color: 'white',
                cursor: 'pointer'
              }}
            >
              <div style={{ fontSize: 24, marginBottom: 8 }}>🔷</div>
              <strong>Unity</strong>
              <p style={{ fontSize: 12, color: '#888', marginTop: 4 }}>2D/3D/Mobile/VR</p>
            </button>
          </div>
          <input
            value={projectName}
            onChange={e => setProjectName(e.target.value)}
            placeholder="Project Name"
            style={{ padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white' }}
          />
          <input
            value={projectDesc}
            onChange={e => setProjectDesc(e.target.value)}
            placeholder="Description"
            style={{ padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white' }}
          />
          <select
            value={template}
            onChange={e => setTemplate(e.target.value)}
            style={{ padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white' }}
          >
            {Object.entries(templates).map(([k, v]) => (
              <option key={k} value={k}>{k} - {v}</option>
            ))}
          </select>
          <button
            onClick={createProject}
            disabled={!projectName}
            style={{ padding: 12, background: '#8b5cf6', border: 'none', borderRadius: 6, color: 'white', cursor: 'pointer' }}
          >
            Create Project
          </button>
        </div>
      )}

      {activeTab === 'config' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
          <div style={{ background: '#2d2d44', padding: 15, borderRadius: 8 }}>
            <h4 style={{ marginBottom: 10 }}>Detected Engines</h4>
            {engines.unreal.length === 0 && engines.unity.length === 0 ? (
              <p style={{ color: '#888', fontSize: 12 }}>No engines detected. Configure paths below.</p>
            ) : (
              <div>
                {engines.unreal.map((e, i) => (
                  <div key={i} style={{ fontSize: 12, marginBottom: 4 }}>🎮 Unreal {e.version}: {e.path}</div>
                ))}
                {engines.unity.map((e, i) => (
                  <div key={i} style={{ fontSize: 12, marginBottom: 4 }}>🔷 Unity {e.version}: {e.path}</div>
                ))}
              </div>
            )}
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Unreal Engine Path</label>
            <input
              value={unrealPath}
              onChange={e => setUnrealPath(e.target.value)}
              placeholder="C:/Program Files/Epic Games/UE_5.4"
              style={{ width: '100%', padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white', marginTop: 4 }}
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Unity Path</label>
            <input
              value={unityPath}
              onChange={e => setUnityPath(e.target.value)}
              placeholder="C:/Program Files/Unity/Hub/Editor/2023.2"
              style={{ width: '100%', padding: 12, background: '#2d2d44', border: 'none', borderRadius: 6, color: 'white', marginTop: 4 }}
            />
          </div>
          <button
            onClick={savePaths}
            style={{ padding: 12, background: '#10b981', border: 'none', borderRadius: 6, color: 'white', cursor: 'pointer' }}
          >
            Save Configuration
          </button>
        </div>
      )}
    </div>
  );
};

export default GameEnginePanel;
