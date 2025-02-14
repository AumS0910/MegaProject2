import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import '../GenerateBrochure.css';

const BrochureForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [templates, setTemplates] = useState([]);
  const [mode, setMode] = useState('brochure');
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    style: 'modern',
    imagePrompt: '',
    textPrompt: '',
    template: '',
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8080/api/brochures/templates', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8080/api/brochures/generate', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // Handle successful generation
      console.log('Brochure generated:', response.data);
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to generate brochure');
      setLoading(false);
    }
  };

  return (
    <div className="generate-brochure-container">
      {/* Left Sidebar for Recent Searches */}
      <div className="recent-searches">
        <h3>Recent Brochures</h3>
        {/* Add recent brochures list here */}
      </div>
      
      {/* Main Content Area */}
      <div className="content-area">
        {/* Centered Mode Toggle */}
        <div className="mode-toggle">
          <button onClick={() => setMode('chatbot')} className={mode === 'chatbot' ? 'active' : ''}>Normal Chatbot</button>
          <button onClick={() => setMode('brochure')} className={mode === 'brochure' ? 'active' : ''}>Brochure Generation</button>
        </div>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={mode}
            initial={{ opacity: 0, x: mode === 'chatbot' ? -50 : 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: mode === 'chatbot' ? 50 : -50 }}
            transition={{ duration: 0.5 }}
            className="chat-section"
          >
            {mode === 'brochure' && (
              <div className="brochure-interface">
                <h3>Generate Luxury Brochure</h3>
                <form onSubmit={handleSubmit} className="brochure-form">
                  <div className="form-group">
                    <label>Hotel Name</label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleChange}
                      placeholder="Enter hotel name..."
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Location</label>
                    <input
                      type="text"
                      name="description"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Enter hotel location..."
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Style</label>
                    <select name="style" value={formData.style} onChange={handleChange}>
                      <option value="modern">Modern</option>
                      <option value="classic">Classic</option>
                      <option value="full_bleed">Full Bleed</option>
                    </select>
                  </div>

                  {error && <div className="error-message">{error}</div>}
                  
                  <button type="submit" disabled={loading} className="generate-button">
                    {loading ? 'Generating...' : 'Generate Brochure'}
                  </button>
                </form>
              </div>
            )}

            {mode === 'chatbot' && (
              <div className="chatbot-interface">
                <h3>Normal Chatbot</h3>
                <div className="chat-display"></div>
                <div className="chat-input">
                  <input type="text" placeholder="Type a message..." />
                  <button>Send</button>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default BrochureForm;
