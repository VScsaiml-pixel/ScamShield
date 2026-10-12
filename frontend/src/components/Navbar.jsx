import React, { useState } from 'react';
import { 
  Shield, 
  Settings as SettingsIcon,
  Menu,
  X
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'message', label: 'Message Scanner' },
  { id: 'url', label: 'URL Scanner' },
  { id: 'history', label: 'History' },
  { id: 'education', label: 'Awareness' },
];

export default function Navbar({ activeTab, onSelectTab, backendConnected }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavClick = (tabId) => {
    onSelectTab(tabId);
    setMobileMenuOpen(false);
  };

  return (
    <header className="navbar">
      <div className="nav-container">
        {/* BRAND */}
        <div 
          className="brand" 
          onClick={() => handleNavClick('dashboard')} 
          role="button" 
          tabIndex={0}
        >
          <Shield size={18} className="brand-icon" />
          <span className="brand-name">ScamShield AI</span>
        </div>

        {/* PRIMARY NAVIGATION LINKS */}
        <nav className="nav-links">
          {NAV_ITEMS.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={`nav-link ${isActive ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* RIGHT SIDE: STATUS & SETTINGS */}
        <div className="nav-secondary">
          {/* UNOBTRUSIVE BACKEND STATUS */}
          <div className="status-indicator" title={backendConnected ? "Backend API is online and responding" : "Backend API is unreachable"}>
            <span className={`status-dot ${backendConnected ? 'connected' : 'offline'}`} />
            <span className="status-label">{backendConnected ? 'Connected' : 'Offline'}</span>
          </div>

          {/* SETTINGS (SECONDARY OPTION) */}
          <button
            type="button"
            className={`nav-settings-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => handleNavClick('settings')}
            title="Settings & System Status"
          >
            <SettingsIcon size={16} />
            <span className="settings-label">Settings</span>
          </button>

          {/* MOBILE TOGGLE */}
          <button 
            type="button" 
            className="mobile-toggle-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* MOBILE MENU */}
      {mobileMenuOpen && (
        <div className="mobile-menu">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`mobile-nav-link ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
            >
              {item.label}
            </button>
          ))}
          <button
            type="button"
            className={`mobile-nav-link ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => handleNavClick('settings')}
          >
            Settings
          </button>
        </div>
      )}
    </header>
  );
}
