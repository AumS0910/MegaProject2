import React from 'react';
import './RecentBrochures.css';

function RecentBrochures({ brochures, loading, error }) {
  if (loading) {
    return (
      <div className="recent-brochures-loading">
        <div className="spinner"></div>
        <p>Loading recent brochures...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="recent-brochures-error">
        <p>Error loading recent brochures: {error}</p>
      </div>
    );
  }

  if (!brochures || brochures.length === 0) {
    return (
      <div className="recent-brochures-empty">
        <p>No recent brochures found</p>
      </div>
    );
  }

  return (
    <div className="recent-brochures">
      <h2>Recent Brochures</h2>
      <div className="brochures-grid">
        {brochures.map((brochure) => (
          <div key={brochure.id} className="brochure-card">
            <div className="brochure-image">
              <img 
                src={brochure.exteriorImage} 
                alt={`${brochure.hotelName} exterior`}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
                }}
              />
            </div>
            <div className="brochure-info">
              <h3>{brochure.hotelName}</h3>
              <p className="location">{brochure.location}</p>
              <p className="created-at">
                Created: {new Date(brochure.createdAt).toLocaleDateString()}
              </p>
              <div className="brochure-actions">
                <a
                  href={brochure.filePath}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="view-button"
                >
                  View Brochure
                </a>
                <a
                  href={brochure.filePath}
                  download
                  className="download-button"
                >
                  Download
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RecentBrochures;
