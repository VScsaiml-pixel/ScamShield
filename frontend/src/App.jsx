import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import MessageScanner from './components/MessageScanner';
import URLScanner from './components/URLScanner';
import ScanHistory from './components/ScanHistory';
import Education from './components/Education';
import Settings from './components/Settings';
import Footer from './components/Footer';
import { checkBackendHealth } from './services/api';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'message' | 'url' | 'history' | 'education' | 'settings'
  const [sharedMessage, setSharedMessage] = useState('');
  const [healthData, setHealthData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleNavigate = (tab, payload) => {
    if (tab === 'message' && typeof payload === 'string') {
      setSharedMessage(payload);
    }
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const fetchStatus = async () => {
    setIsLoading(true);
    try {
      const healthRes = await checkBackendHealth();
      if (healthRes.success) {
        setHealthData(healthRes.data);
      } else {
        setHealthData(null);
      }
    } catch {
      setHealthData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="app-layout">
      {/* CLEAN TOP NAVBAR */}
      <Navbar 
        activeTab={activeTab} 
        onSelectTab={handleNavigate}
        backendConnected={!!healthData && healthData.status === 'healthy'} 
      />
      
      {/* MAIN CONTENT VIEW */}
      <main className="main-content">
        <div className="content-container">
          {activeTab === 'dashboard' && (
            <Dashboard onNavigate={handleNavigate} />
          )}

          {activeTab === 'message' && (
            <MessageScanner initialMessage={sharedMessage} />
          )}

          {activeTab === 'url' && (
            <URLScanner />
          )}

          {activeTab === 'history' && (
            <ScanHistory />
          )}

          {activeTab === 'education' && (
            <Education onNavigate={handleNavigate} />
          )}

          {activeTab === 'settings' && (
            <Settings onNavigate={handleNavigate} />
          )}
        </div>
      </main>

      {/* MINIMAL FOOTER */}
      <Footer />
    </div>
  );
}
