import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaUser, FaEnvelope, FaFileAlt, FaClock, FaCalendarAlt, FaEdit, FaSave, FaTimes, FaArrowLeft } from 'react-icons/fa';
import { brochureAPI, userAPI } from '../services/api';
import './ProfilePage.css';

function ProfilePage() {
    const [activeTab, setActiveTab] = useState('overview');
    const [isEditing, setIsEditing] = useState(false);
    const [userData, setUserData] = useState({
        name: '',
        email: '',
        totalBrochures: 0,
        lastLogin: '',
        memberSince: '',
        recentBrochures: []
    });
    const [editForm, setEditForm] = useState({
        name: '',
        email: ''
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Get user data from local storage first
            const token = localStorage.getItem('token');
            const storedUser = JSON.parse(localStorage.getItem('user'));
            
            if (!token || !storedUser) {
                throw new Error('User not logged in');
            }

            // Fetch recent brochures
            const brochuresResponse = await brochureAPI.getRecentBrochures();
            
            setUserData({
                name: storedUser.name || '',
                email: storedUser.email || '',
                totalBrochures: brochuresResponse?.length || 0,
                lastLogin: storedUser.lastLoginDate || new Date().toISOString(),
                memberSince: storedUser.createdDate || new Date().toISOString(),
                recentBrochures: brochuresResponse || []
            });

            setEditForm({
                name: storedUser.name || '',
                email: storedUser.email || ''
            });
        } catch (err) {
            console.error('Error fetching user data:', err);
            setError('Failed to load user data. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleEditSubmit = async (e) => {
        e.preventDefault();
        try {
            // Update local storage
            const storedUser = JSON.parse(localStorage.getItem('user'));
            const updatedUser = {
                ...storedUser,
                name: editForm.name,
                email: editForm.email
            };
            localStorage.setItem('user', JSON.stringify(updatedUser));

            setUserData(prev => ({
                ...prev,
                name: editForm.name,
                email: editForm.email
            }));
            setIsEditing(false);
        } catch (err) {
            console.error('Error updating profile:', err);
            setError('Failed to update profile. Please try again.');
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
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
            setError('Error downloading brochure. Please try again.');
        }
    };

    if (loading) {
        return (
            <div className="profile-page">
                <div className="profile-container">
                    <div className="loading">Loading...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="profile-page">
            <motion.div
                className="profile-container"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                {error && <div className="error-message">{error}</div>}
                
                <div className="profile-header">
                    <motion.div
                        className="profile-avatar"
                        whileHover={{ scale: 1.1 }}
                        transition={{ type: "spring", stiffness: 300 }}
                    >
                        <FaUser size="2em" />
                    </motion.div>
                    <h1>{userData.name || 'User Profile'}</h1>
                </div>

                <div className="tab-navigation">
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Overview
                    </motion.button>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
                        onClick={() => setActiveTab('profile')}
                    >
                        Profile Settings
                    </motion.button>
                </div>

                {activeTab === 'overview' ? (
                    <div className="dashboard-overview">
                        <div className="stats-grid">
                            <motion.div
                                className="stat-card"
                                whileHover={{ y: -5 }}
                                transition={{ type: "spring", stiffness: 300 }}
                            >
                                <FaFileAlt className="stat-icon" />
                                <div className="stat-content">
                                    <h3>Total Brochures</h3>
                                    <p>{userData.totalBrochures}</p>
                                </div>
                            </motion.div>
                            <motion.div
                                className="stat-card"
                                whileHover={{ y: -5 }}
                                transition={{ type: "spring", stiffness: 300 }}
                            >
                                <FaClock className="stat-icon" />
                                <div className="stat-content">
                                    <h3>Last Login</h3>
                                    <p>{formatDate(userData.lastLogin)}</p>
                                </div>
                            </motion.div>
                            <motion.div
                                className="stat-card"
                                whileHover={{ y: -5 }}
                                transition={{ type: "spring", stiffness: 300 }}
                            >
                                <FaCalendarAlt className="stat-icon" />
                                <div className="stat-content">
                                    <h3>Member Since</h3>
                                    <p>{formatDate(userData.memberSince)}</p>
                                </div>
                            </motion.div>
                        </div>

                        <div className="recent-activity">
                            <h2>Recent Brochures</h2>
                            <div className="activity-list">
                                {userData.recentBrochures.length > 0 ? (
                                    userData.recentBrochures.map((brochure, index) => (
                                        <motion.div
                                            key={index}
                                            className="activity-item"
                                            whileHover={{ x: 10 }}
                                            onClick={() => handleDownload(brochure)}
                                        >
                                            <FaFileAlt className="activity-icon" />
                                            <div className="activity-content">
                                                <h4>{brochure.hotelName}</h4>
                                                <p>Created on {formatDate(brochure.createdAt)}</p>
                                            </div>
                                        </motion.div>
                                    ))
                                ) : (
                                    <p>No brochures created yet</p>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="profile-content">
                        <form onSubmit={handleEditSubmit}>
                            <div className="profile-field">
                                <FaUser className="field-icon" />
                                <div className="field-content">
                                    <label>Full Name</label>
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            value={editForm.name}
                                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                            required
                                        />
                                    ) : (
                                        <p>{userData.name}</p>
                                    )}
                                </div>
                            </div>

                            <div className="profile-field">
                                <FaEnvelope className="field-icon" />
                                <div className="field-content">
                                    <label>Email Address</label>
                                    {isEditing ? (
                                        <input
                                            type="email"
                                            value={editForm.email}
                                            onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                                            required
                                        />
                                    ) : (
                                        <p>{userData.email}</p>
                                    )}
                                </div>
                            </div>

                            <div className="profile-actions">
                                {isEditing ? (
                                    <>
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            type="submit"
                                            className="save-button"
                                        >
                                            <FaSave /> Save Changes
                                        </motion.button>
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            type="button"
                                            className="cancel-button"
                                            onClick={() => {
                                                setIsEditing(false);
                                                setEditForm({
                                                    name: userData.name,
                                                    email: userData.email
                                                });
                                            }}
                                        >
                                            <FaTimes /> Cancel
                                        </motion.button>
                                    </>
                                ) : (
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        type="button"
                                        className="edit-button"
                                        onClick={() => setIsEditing(true)}
                                    >
                                        <FaEdit /> Edit Profile
                                    </motion.button>
                                )}
                            </div>
                        </form>
                    </div>
                )}

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="back-button"
                    onClick={() => window.history.back()}
                >
                    <FaArrowLeft /> Back to Dashboard
                </motion.button>
            </motion.div>
        </div>
    );
}

export default ProfilePage;
