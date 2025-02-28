import React, { useState, useEffect } from 'react';
import { brochureAPI } from '../services/api';
import RecentBrochures from './RecentBrochures';
import { useNavigate } from 'react-router-dom';
import './GenerateBrochure.css';

// Background images for parallax effect
const bgImages = [
  'https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1920&q=80', // Beachfront resort
  'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1920&q=80',  // Mountain retreat
  'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1920&q=80' // Luxury hotel lobby
];

function GenerateBrochure() {
  const navigate = useNavigate();
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

  const parsePromptWithNLP = async (prompt) => {
    try {
      const response = await fetch('http://localhost:8010/parse-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt })
      });

      if (!response.ok) {
        throw new Error('NLP parsing failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.warn('NLP parsing failed, falling back to regex:', error);
      // Fallback to regex parsing
      const hotelName = extractHotelNameFromPrompt(prompt);
      const location = prompt.split(' in ').length > 1 ? prompt.split(' in ')[1].split(' ')[0] : '';
      return {
        hotel_name: hotelName,
        location: location,
        confidence: 0.3
      };
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setStatus('generating');
    setStatusMessage('Starting brochure generation...');
    setError(null);
    setGeneratedBrochure(null);

    try {
      // Parse prompt using NLP with fallback to regex
      const parsedInfo = await parsePromptWithNLP(prompt);
      console.log('Parsed prompt info:', parsedInfo);

      // Choose endpoint based on layout
      const endpoint = layout === 'trifold' 
        ? 'http://localhost:8009/generate-trifold'
        : 'http://localhost:8006/generate-brochure-from-prompt';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(
          layout === 'trifold' 
            ? {
                hotel_name: parsedInfo.hotel_name,
                location: parsedInfo.location || prompt.split(' in ').pop().split(' ')[0],
                amenities: null,  // Will use default amenities
                experience_text: prompt,
                contact_info: null  // Will use default contact info
              }
            : { prompt, layout }
        )
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate brochure');
      }

      const data = await response.json();
      
      if (data.status === 'success' || data.status === 'completed') {
        // Handle different response formats
        const filePath = layout === 'trifold'
          ? data.files.pdf
          : data.file_path;
        
        const brochurePath = layout === 'trifold'
          ? `http://localhost:8009/brochures/${filePath}`
          : `http://localhost:8006/brochures/${filePath}`;

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
              filePath: brochurePath,
              prompt: prompt
            })
          });
        } catch (saveError) {
          console.error('Error saving brochure history:', saveError);
        }

        setStatus('completed');
        setStatusMessage('Brochure generated successfully!');
        setGeneratedBrochure({
          brochurePath: brochurePath
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
      <button 
        className="back-button" 
        onClick={() => {
          localStorage.setItem('menuWasOpen', 'true');
          navigate('/');
        }}
      >
        ← Back
      </button>
      <div className="content-overlay">
        <h1 className="title">AI BROCHURE GENERATOR</h1>
        
        <div className="floating-card">
          <div className="prompt-guide">
            Choose a layout and describe your hotel to create a beautiful brochure!
            <span className="example">Example: "Generate a brochure for Sunset Paradise Resort in Maldives"</span>
          </div>

          <form onSubmit={handleSubmit} className="generate-form">
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
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., Generate a brochure for Marriott Hotel in Mumbai"
                className="prompt-input"
                aria-label="Hotel brochure prompt"
              />
              <small className="helper-text">
                Tip: Include both hotel name and location (e.g., "Taj Hotel in Delhi" or "Hilton Resort Goa")
              </small>
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
