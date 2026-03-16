import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const HardwarePanel = () => {
  const [activeTab, setActiveTab] = useState('projects');
  const [projects, setProjects] = useState([]);
  const [platforms, setPlatforms] = useState({});
  const [sensors, setSensors] = useState({});
  const [loading, setLoading] = useState(true);
  
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('arduino_uno');
  const [selectedSensors, setSelectedSensors] = useState([]);
  const [generatedCode, setGeneratedCode] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [projectsRes, platformsRes, sensorsRes] = await Promise.all([
        axios.get(`${API}/api/hardware/projects`),
        axios.get(`${API}/api/hardware/platforms`),
        axios.get(`${API}/api/hardware/sensors`)
      ]);
      setProjects(projectsRes.data || []);
      setPlatforms(platformsRes.data || {});
      setSensors(sensorsRes.data || {});
    } catch (e) {}
    setLoading(false);
  };

  const createProject = async () => {
    if (!projectName) return;
    try {
      await axios.post(`${API}/api/hardware/projects`, {
        name: projectName,
        description: projectDesc,
        platform: selectedPlatform,
        sensors: selectedSensors
      });
      setProjectName('');
      setProjectDesc('');
      setSelectedSensors([]);
      fetchData();
    } catch (e) {}
  };

  const generateCode = async (projectId) => {
    try {
      const res = await axios.post(`${API}/api/hardware/generate`, { project_id: projectId });
      setGeneratedCode(res.data.code);
      setActiveTab('code');
    } catch (e) {}
  };

  const toggleSensor = (sensorId) => {
    setSelectedSensors(prev =>
      prev.includes(sensorId) ? prev.filter(s => s !== sensorId) : [...prev, sensorId]
    );
  };

  const platformGroups = {
    arduino: ['arduino_uno', 'arduino_mega', 'arduino_nano', 'esp32', 'esp8266'],
    raspberry: ['raspberry_pi_4', 'raspberry_pi_pico', 'raspberry_pi_pico_w'],
    stm32: ['stm32_bluepill', 'stm32_blackpill'],
    teensy: ['teensy_40', 'teensy_41']
  };

  return (
    <div style={{ padding: 20, background: '#1a1a2e', borderRadius: 12, color: 'white' }}>
      <h2 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 24 }}>🔧</span> Hardware Integration
        <span style={{ fontSize: 12, background: '#f59e0b', padding: '2px 8px', borderRadius: 4 }}>Arduino • Pi • STM32 • Teensy</span>
      </h2>

      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        {['projects', 'create', 'code'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              background: activeTab === tab ? '#f59e0b' : '#2d2d44',
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
            <p style={{ color: '#888' }}>No hardware projects yet.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {projects.map(p => (
                <div key={p.id} style={{ background: '#2d2d44', padding: 15, borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong>{p.name}</strong>
                      <span style={{ marginLeft: 10, fontSize: 12, color: '#888' }}>
                        {platforms[p.platform]?.name || p.platform}
                      </span>
                    </div>
                    <button
                      onClick={() => generateCode(p.id)}
                      style={{ padding: '6px 12px', background: '#f59e0b', border: 'none', borderRadius: 4, color: 'white', cursor: 'pointer' }}
                    >
                      Generate Code
                    </button>
                  </div>
                  {p.sensors && p.sensors.length > 0 && (
                    <div style={{ marginTop: 8, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {p.sensors.map(s => (
                        <span key={s} style={{ fontSize: 11, background: '#1a1a2e', padding: '2px 6px', borderRadius: 4 }}>
                          {sensors[s]?.name || s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'create' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
          <div>
            <label style={{ fontSize: 12, color: '#888', marginBottom: 8, display: 'block' }}>Platform</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
              {Object.entries(platformGroups).map(([group, items]) => (
                <div key={group}>
                  <div style={{ fontSize: 11, color: '#888', marginBottom: 4, textTransform: 'uppercase' }}>{group}</div>
                  {items.map(p => platforms[p] && (
                    <button
                      key={p}
                      onClick={() => setSelectedPlatform(p)}
                      style={{
                        display: 'block',
                        width: '100%',
                        padding: 8,
                        marginBottom: 4,
                        background: selectedPlatform === p ? '#f59e0b20' : '#2d2d44',
                        border: selectedPlatform === p ? '1px solid #f59e0b' : '1px solid transparent',
                        borderRadius: 4,
                        color: 'white',
                        cursor: 'pointer',
                        fontSize: 11,
                        textAlign: 'left'
                      }}
                    >
                      {platforms[p].name}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </div>

          <div>
            <label style={{ fontSize: 12, color: '#888', marginBottom: 8, display: 'block' }}>Sensors</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {Object.entries(sensors).map(([id, sensor]) => (
                <button
                  key={id}
                  onClick={() => toggleSensor(id)}
                  style={{
                    padding: '6px 10px',
                    background: selectedSensors.includes(id) ? '#f59e0b' : '#2d2d44',
                    border: 'none',
                    borderRadius: 4,
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: 11
                  }}
                >
                  {sensor.name}
                </button>
              ))}
            </div>
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
          <button
            onClick={createProject}
            disabled={!projectName}
            style={{ padding: 12, background: '#f59e0b', border: 'none', borderRadius: 6, color: 'white', cursor: 'pointer' }}
          >
            Create Hardware Project
          </button>
        </div>
      )}

      {activeTab === 'code' && (
        <div>
          {generatedCode ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                <span style={{ color: '#888', fontSize: 12 }}>Generated Code</span>
                <button
                  onClick={() => navigator.clipboard.writeText(generatedCode)}
                  style={{ padding: '4px 8px', background: '#2d2d44', border: 'none', borderRadius: 4, color: 'white', cursor: 'pointer', fontSize: 11 }}
                >
                  Copy
                </button>
              </div>
              <pre style={{
                background: '#0d0d1a',
                padding: 15,
                borderRadius: 8,
                overflow: 'auto',
                maxHeight: 400,
                fontSize: 12,
                fontFamily: 'monospace'
              }}>
                {generatedCode}
              </pre>
            </div>
          ) : (
            <p style={{ color: '#888' }}>Generate code from a project to view it here.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default HardwarePanel;
