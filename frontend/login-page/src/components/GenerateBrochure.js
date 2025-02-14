import React, { useState, useEffect } from 'react';
import { brochureAPI } from '../services/api';
import RecentBrochures from './RecentBrochures';
import './GenerateBrochure.css';

// Background images for parallax effect
const bgImages = [
  'https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1920&q=80', // Beachfront resort
  'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1920&q=80',  // Mountain retreat
  'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1920&q=80' // Luxury hotel lobby
];

function GenerateBrochure() {
  const [prompt, setPrompt] = useState('');
  const [layout, setLayout] = useState('trifold');
  const [status, setStatus] = useState('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [generatedBrochure, setGeneratedBrochure] = useState(null);
  const [error, setError] = useState(null);
  const [currentBg, setCurrentBg] = useState(0);
  const [recentBrochures, setRecentBrochures] = useState([]);
  const [loadingRecent, setLoadingRecent] = useState(false);
  const [recentError, setRecentError] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentBg((prev) => (prev + 1) % bgImages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Fetch recent brochures
  useEffect(() => {
    fetchRecentBrochures();
  }, []);

  const fetchRecentBrochures = async () => {
    setLoadingRecent(true);
    setRecentError(null);
    try {
      const data = await brochureAPI.getRecentBrochures();
      setRecentBrochures(data.brochures);
    } catch (err) {
      console.error('Error fetching recent brochures:', err);
      setRecentError(err.message);
    } finally {
      setLoadingRecent(false);
    }
  };

  // Refresh recent brochures after generating a new one
  useEffect(() => {
    if (status === 'completed') {
      fetchRecentBrochures();
    }
  }, [status]);

  const extractHotelNameFromPrompt = (prompt) => {
    // Remove common prefixes
    const cleanPrompt = prompt.replace(/^(generate|create|make|design)\s+(a|an)\s+brochure\s+(for|of|about)?\s*/i, '');
    
    // Try to get hotel name before "in" location
    const beforeIn = cleanPrompt.split(' in ')[0];
    
    // Take first part but limit to reasonable length
    return beforeIn.split(' ').slice(0, 4).join(' ');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setStatus('generating');
    setStatusMessage('Starting brochure generation...');
    setError(null);
    setGeneratedBrochure(null);

    try {
      const response = await fetch('http://localhost:8006/generate-brochure-from-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ prompt, layout })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate brochure');
      }

      const data = await response.json();
      if (data.status === 'completed') {
        // Save to brochure history
        try {
          await fetch('http://localhost:8080/api/brochures/save', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': localStorage.getItem('token')
            },
            body: JSON.stringify({
              hotelName: data.hotel_name || extractHotelNameFromPrompt(prompt),
              location: data.location || prompt.split(' in ').pop().split(' ')[0],
              filePath: `http://localhost:8006/brochures/${data.file_path}`,
              exteriorImage: `http://localhost:8006/images/${data.images.exterior}`,
              roomImage: `http://localhost:8006/images/${data.images.room}`,
              restaurantImage: `http://localhost:8006/images/${data.images.restaurant}`,
              prompt: prompt
            })
          });
        } catch (saveError) {
          console.error('Error saving brochure history:', saveError);
        }

        setStatus('completed');
        setStatusMessage('Brochure generated successfully!');
        setGeneratedBrochure({
          brochurePath: `http://localhost:8006/brochures/${data.file_path}`,
          images: {
            exterior: `http://localhost:8006/images/${data.images.exterior}`,
            room: `http://localhost:8006/images/${data.images.room}`,
            restaurant: `http://localhost:8006/images/${data.images.restaurant}`
          }
        });
      } else {
        setStatus('error');
        setStatusMessage('Failed to generate brochure');
        setError('Unexpected response from server');
      }
    } catch (err) {
      setStatus('error');
      setStatusMessage('Error generating brochure');
      setError(err.message);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(generatedBrochure.brochurePath);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const blob = await response.blob();
      if (blob.size === 0) {
        throw new Error('Downloaded file is empty');
      }
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const fileName = generatedBrochure.brochurePath.split('/').pop() || 'hotel_brochure.pdf';
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      setError('Error downloading brochure: ' + err.message);
    }
  };

  return (
    <div 
      className="brochure-generator-wrapper"
      style={{
        backgroundImage: `url(${bgImages[currentBg]})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        transition: 'background-image 1s ease-in-out'
      }}
    >
      <div className="content-overlay">
        <h1 className="title">AI BROCHURE GENERATOR</h1>
        
        <div className="floating-card">
          <div className="prompt-guide">
            Choose a layout and describe your hotel to create a beautiful brochure!
            <span className="example">Example: "Generate a brochure for Sunset Paradise Resort in Maldives"</span>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="layout-selector">
              <label>Select Layout:</label>
              <div className="layout-options">
                <label className={`layout-option ${layout === 'trifold' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="layout"
                    value="trifold"
                    checked={layout === 'trifold'}
                    onChange={(e) => setLayout(e.target.value)}
                  />
                  <div className="layout-preview trifold-preview">
                    <span>Tri-fold Layout</span>
                    <p>Classic three-panel design perfect for physical distribution</p>
                  </div>
                </label>
                <label className={`layout-option ${layout === 'full_bleed' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="layout"
                    value="full_bleed"
                    checked={layout === 'full_bleed'}
                    onChange={(e) => setLayout(e.target.value)}
                  />
                  <div className="layout-preview full-bleed-preview">
                    <span>Full Bleed Layout</span>
                    <p>Modern single-page design ideal for digital viewing</p>
                  </div>
                </label>
              </div>
            </div>

            <div className="input-group">
              <textarea
                className="prompt-input"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your hotel description here..."
                required
              />
            </div>

            <button 
              type="submit" 
              className="generate-button"
              disabled={status === 'generating'}
            >
              {status === 'generating' ? 'Generating...' : 'Generate Brochure'}
            </button>
          </form>

          {status === 'generating' && (
            <div className="status-message generating">
              <div className="spinner"></div>
              <p>{statusMessage}</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>{error}</p>
            </div>
          )}

          {generatedBrochure && (
            <div className="generated-content">
              <div className="pdf-preview">
                <h2>Brochure Preview</h2>
                <div className="pdf-container">
                  <iframe
                    src={generatedBrochure.brochurePath}
                    title="Brochure Preview"
                    width="100%"
                    height="600px"
                    style={{ border: 'none', borderRadius: '8px' }}
                  />
                </div>
              </div>

              <div className="download-section">
                <button onClick={handleDownload} className="download-button">
                  Download Brochure PDF
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default GenerateBrochure;
