import React, { useState, useEffect } from 'react';
import { brochureAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import './RecentBrochurePage.css';

function RecentBrochurePage() {
  const [brochures, setBrochures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecentBrochures();
  }, []);

  const fetchRecentBrochures = async () => {
    try {
      setLoading(true);
      const response = await brochureAPI.getRecentBrochures();
      setBrochures(response || []); // Set empty array if response is null/undefined
    } catch (err) {
      console.error('Error fetching brochures:', err);
      setError('Failed to load recent brochures. Please try again later.');
      setBrochures([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (brochure) => {
    try {
      const response = await fetch(brochure.filePath);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${brochure.hotelName}_brochure.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      alert('Error downloading brochure. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="recent-brochures-page loading">
        <div className="spinner"></div>
        <p>Loading your brochures...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="recent-brochures-page error">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={fetchRecentBrochures} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="recent-brochures-page">
      <div className="page-header">
        
        <h1>Your Recent Brochures</h1>
        <p>View and manage your recently created brochures</p>
      </div>

      {brochures.length === 0 ? (
        <div className="no-brochures">
          <h2>No Brochures Found</h2>
          <p>You haven't created any brochures yet. Start by generating a new brochure!</p>
        </div>
      ) : (
        <div className="brochures-grid">
          {brochures.map((brochure) => (
            <div key={brochure.id} className="brochure-card">
              <div className="brochure-preview">
                <img 
                  src={brochure.exteriorImage || 'https://via.placeholder.com/400x300?text=No+Preview'} 
                  alt={`${brochure.hotelName} exterior`}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'https://via.placeholder.com/400x300?text=No+Preview';
                  }}
                />
              </div>
              <div className="brochure-details">
                <h3>{brochure.hotelName}</h3>
                <p className="location">{brochure.location}</p>
                <p className="date">Created: {new Date(brochure.createdAt).toLocaleDateString()}</p>
                <div className="brochure-actions">
                  <a
                    href={brochure.filePath}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-button"
                  >
                    View Brochure
                  </a>
                  <button
                    onClick={() => handleDownload(brochure)}
                    className="download-button"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecentBrochurePage;
