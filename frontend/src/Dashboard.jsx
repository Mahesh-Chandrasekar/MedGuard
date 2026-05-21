import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { LogOut, Activity, CheckSquare } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [drug1, setDrug1] = useState('');
  const [drug2, setDrug2] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    const user = localStorage.getItem('medguard_user');
    if (!user) navigate('/login');
    else setUsername(user);
  }, [navigate]);

  const handleAnalyze = async () => {
    if (!drug1 || !drug2) return;
    setLoading(true);
    setResults(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/analyze_drugs', {
        drug_1: drug1,
        drug_2: drug2
      });
      setResults(response.data.interaction);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <nav style={styles.navbar}>
        <div style={styles.navBrand}>
          <Activity size={24} color="#2563EB" />
          <h2 style={{ margin: 0, color: '#1E293B', fontSize: '18px', fontWeight: '600' }}>MedGuard AI | Clinical Portal</h2>
        </div>
        <div style={styles.userInfo}>
          <span style={{color: '#64748B', fontSize: '13px', marginRight: '20px', fontWeight: '500'}}>Active Session: Dr. {username.replace('dr_', '').toUpperCase()}</span>
          <button onClick={() => navigate('/login')} style={styles.logoutBtn}><LogOut size={16} /> Logout</button>
        </div>
      </nav>

      <div style={styles.container}>
        {/* LEFT COLUMN: Input Parameters */}
        <div style={styles.inputPanel}>
          <h3 style={styles.panelTitle}>Input Parameters</h3>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>DRUG 1 (PRIMARY AGENT)</label>
            <input style={styles.input} value={drug1} onChange={e => setDrug1(e.target.value)} placeholder="e.g. aspirin" />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>DRUG 2 (SECONDARY AGENT)</label>
            <input style={styles.input} value={drug2} onChange={e => setDrug2(e.target.value)} placeholder="e.g. warfarin" />
          </div>

          <button onClick={handleAnalyze} style={styles.analyzeBtn} disabled={loading || !drug1 || !drug2}>
            {loading ? 'Analyzing...' : 'Analyze Interaction'}
          </button>
        </div>

        {/* RIGHT COLUMN: Results */}
        <div style={styles.resultsPanel}>
          {results ? (
            <>
              <div style={styles.headerRow}>
                <div style={styles.titleWrapper}>
                  {results.severity === 'Major' && <CheckSquare size={20} color="#DC2626" style={{marginRight: '8px'}}/>}
                  <h2 style={{ color: results.severity === 'Major' ? '#DC2626' : results.severity === 'Moderate' ? '#D97706' : '#059669', margin: 0, fontSize: '22px', fontWeight: '700', letterSpacing: '0.5px' }}>
                    {results.severity.toUpperCase()} INTERACTION
                  </h2>
                </div>
                <div style={styles.confidenceBox}>
                  <span style={{ fontSize: '11px', color: '#64748B', fontWeight: '700', letterSpacing: '0.5px' }}>CLINICAL CONFIDENCE</span>
                  <strong style={{ fontSize: '28px', color: '#1E293B', lineHeight: '1.2' }}>{results.confidence}%</strong>
                  <span style={{ fontSize: '10px', color: '#94A3B8' }}>Confidence adjusted due to<br/>limited or unseen data.</span>
                </div>
              </div>

              <div style={styles.section}>
                <h4 style={styles.sectionTitle}>IDENTIFIED SIDE EFFECT</h4>
                <p style={styles.sideEffectText}>{results.known_history}</p>
              </div>

              {/* CHEMICAL ANALYSIS IMAGES (Moved up, borders adjusted) */}
              <div style={{...styles.section, borderBottom: 'none', paddingTop: '10px'}}>
                <h4 style={styles.sectionTitle}>CHEMICAL ANALYSIS</h4>
                <div style={styles.chemContainer}>
                    <div style={styles.chemBox}>
                        <img 
                            src={`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${drug1}/PNG`} 
                            alt={drug1} 
                            style={styles.chemImage}
                            onError={(e) => e.target.style.display = 'none'} 
                        />
                        <p style={styles.chemLabel}>{drug1.toUpperCase()}</p>
                    </div>
                    <div style={styles.chemBox}>
                        <img 
                            src={`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${drug2}/PNG`} 
                            alt={drug2} 
                            style={styles.chemImage}
                            onError={(e) => e.target.style.display = 'none'}
                        />
                        <p style={styles.chemLabel}>{drug2.toUpperCase()}</p>
                    </div>
                </div>
              </div>

            </>
          ) : (
            <div style={styles.emptyState}>Enter drug parameters to view clinical diagnostics.</div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', backgroundColor: '#F8FAFC', fontFamily: '"Inter", system-ui, sans-serif' },
  navbar: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 30px', backgroundColor: 'white', borderBottom: '1px solid #E2E8F0', boxShadow: '0 1px 2px rgba(0,0,0,0.02)' },
  navBrand: { display: 'flex', alignItems: 'center', gap: '10px' },
  userInfo: { display: 'flex', alignItems: 'center' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', border: '1px solid #E2E8F0', borderRadius: '4px', background: 'white', cursor: 'pointer', color: '#64748B', fontSize: '13px', fontWeight: '500' },
  container: { display: 'flex', gap: '24px', padding: '30px 20px', maxWidth: '1050px', margin: '0 auto', alignItems: 'flex-start' },
  inputPanel: { flex: '0 0 320px', backgroundColor: 'white', padding: '24px', borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' },
  resultsPanel: { flex: 1, backgroundColor: 'white', padding: '32px', borderRadius: '8px', border: '1px solid #E2E8F0', minHeight: '500px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' },
  panelTitle: { margin: '0 0 24px 0', fontSize: '15px', color: '#0F172A', borderBottom: '2px solid #F1F5F9', paddingBottom: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.5px' },
  inputGroup: { marginBottom: '20px' },
  label: { display: 'block', fontSize: '11px', fontWeight: '700', color: '#64748B', marginBottom: '8px', letterSpacing: '0.5px' },
  input: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #CBD5E1', boxSizing: 'border-box', backgroundColor: '#F8FAFC', fontSize: '14px', color: '#0F172A', fontWeight: '500' },
  analyzeBtn: { width: '100%', padding: '14px', marginTop: '10px', backgroundColor: '#2563EB', color: 'white', border: 'none', borderRadius: '6px', fontWeight: '600', cursor: 'pointer', fontSize: '14px', transition: 'background-color 0.2s' },
  headerRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px', paddingBottom: '20px', borderBottom: '1px solid #E2E8F0' },
  titleWrapper: { display: 'flex', alignItems: 'center' },
  confidenceBox: { textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' },
  section: { marginBottom: '24px', paddingBottom: '24px', borderBottom: '1px dashed #E2E8F0' },
  sectionTitle: { margin: '0 0 12px 0', fontSize: '11px', color: '#64748B', letterSpacing: '1px', fontWeight: '700' },
  sideEffectText: { fontSize: '15px', color: '#0F172A', fontWeight: '500', margin: 0, lineHeight: '1.5', textAlign: 'left' },
  chemContainer: { display: 'flex', gap: '20px', justifyContent: 'space-around', marginTop: '15px' },
  chemBox: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '15px', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', width: '45%' },
  chemImage: { width: '100%', height: 'auto', maxHeight: '180px', objectFit: 'contain' },
  chemLabel: { marginTop: '12px', fontSize: '12px', fontWeight: '700', color: '#475569', letterSpacing: '1px', margin: '12px 0 0 0' },
  emptyState: { height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94A3B8', fontSize: '15px' }
};