import React, { useState } from 'react';
import './RecentBrochures.css';

const RecentBrochures = ({ brochures, loading, error }) => {
  const [imageErrors, setImageErrors] = useState({});

  const getImageUrl = (imagePath) => {
    if (!imagePath) return 'https://via.placeholder.com/300x200?text=No+Image';
    return `http://localhost:8007/images/${imagePath}`;
  };

  const getBrochureUrl = (brochurePath) => {
    if (!brochurePath) return '#';
    return `http://localhost:8007/brochures/${brochurePath}`;
  };

  const handleImageError = (brochureId, e) => {
    console.error(`Image load error for brochure ${brochureId}:`, e);
    setImageErrors(prev => ({ ...prev, [brochureId]: true }));
    e.target.onerror = null;
    e.target.src = 'https://via.placeholder.com/400x300?text=No+Preview';
  };

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
        {brochures.map((brochure) => {
          console.log('Rendering brochure:', {
            id: brochure.id,
            hotelName: brochure.hotelName,
            imagePath: brochure.exteriorImage
          });

          return (
            <div key={brochure.id} className="brochure-card">
              <div className="brochure-image">
                <img 
                  src={getImageUrl(brochure.exteriorImage) || 'https://via.placeholder.com/400x300?text=No+Preview'}
                  alt={`${brochure.hotelName} exterior`}
                  onError={(e) => handleImageError(brochure.id, e)}
                  style={{ opacity: imageErrors[brochure.id] ? 0.5 : 1 }}
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
                    href={getBrochureUrl(brochure.filePath)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-button"
                  >
                    View Brochure
                  </a>
                  <a
                    href={getBrochureUrl(brochure.filePath)}
                    download
                    className="download-button"
                  >
                    Download
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RecentBrochures;
