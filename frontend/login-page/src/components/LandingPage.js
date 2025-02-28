import { motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { FaArrowLeft, FaBars, FaSignOutAlt, FaUser } from 'react-icons/fa';
import Lottie from 'react-lottie-player';
import './LandingPage.css';
import './Menu.css';

// Import Lottie animations
import { useNavigate } from 'react-router-dom';
import generateAnimation from './assets/Animation - 1730313415762.json';
import editAnimation from './assets/Animation - 1730314214970.json';
import recentAnimation from './assets/Animation - 1730365332462.json';
import profileAnimation from './assets/Animation - 1731136886462.json';
import { default as editVideo, default as generateVideo, default as profileVideo, default as recentVideo } from './assets/white graph paper - SewBosse (1080p, h264, youtube).mp4';
import { authAPI } from '../services/auth';

const menuItems = [
  { id: 1, title: 'Generate Brochure', desc: 'CREATE NEW BROCHURE', longDesc: 'Create customized brochures from scratch with ease. Our tool guides you through every step, offering a range of templates, fonts, and design elements tailored to your needs. Whether its for marketing, events, or personal projects, generate a high-quality brochure that captures your brands voice. Ideal for beginners and experts. ', video: generateVideo, lottieAnimation: generateAnimation },
  { id: 2, title: 'Recent Brochure', desc: 'VIEW YOUR RECENT BROCHURE', longDesc: 'Quickly revisit and review your recently created brochures for easy updates and refinements. This feature helps you pick up where you left off, ensuring continuity and convenience. Access all recently edited brochures with just one click, making it simple to make minor adjustments or save and share your finished product.', video: recentVideo, lottieAnimation : recentAnimation },
  { id: 3, title: 'Profile', desc: 'MANAGE YOUR PROFILE', longDesc: 'Manage your account, preferences, and saved projects in one place. The Profile section allows you to update personal information, adjust design preferences, and easily track your project history. Streamline your brochure creation process by personalizing your settings to suit your design style and workflow.Login with Google & Facebook', video: profileVideo, lottieAnimation: profileAnimation },
];

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const [userName, setUserName] = useState('');
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    // Get user info from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      setUserName(user.name || user.email.split('@')[0]);
    }
  }, []);

  useEffect(() => {
    const menuWasOpen = localStorage.getItem('menuWasOpen');
    if (menuWasOpen === 'true') {
      setIsMenuOpen(true);
      localStorage.removeItem('menuWasOpen');
    }
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen((prev) => !prev);
  };

  const goToLogin = () => navigate('/LoginPage');
  
  const handleLogout = () => {
    authAPI.logout();
    navigate('/LoginPage');
  };

  useEffect(() => {
    document.body.style.overflow = isMenuOpen ? 'hidden' : 'auto';
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isMenuOpen]);

  const handleMenuItemClick = (item) => {
    // Store menu state in localStorage before navigating
    localStorage.setItem('menuWasOpen', 'true');
    setIsMenuOpen(false);
    switch(item.title) {
      case 'Generate Brochure':
        navigate('/generate-brochure');
        break;
      case 'Recent Brochure':
        navigate('/recent-brochures');
        break;
      case 'Profile':
        navigate('/profile');
        break;
      default:
        break;
    }
  };

  return (
    <div className="landing-page">
      <motion.div className="nav-icons">
        <motion.div 
          className='login-icon'
          onClick={goToLogin}
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.9 }}
        >
          <img src={require('./assets/pngwing.com.png')} alt="Login Logo" style={{ width: 40, height: 40 }} />
        </motion.div>

        <motion.button
          className="logout-button"
          onClick={handleLogout}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            marginRight: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '16px'
          }}
        >
          <FaSignOutAlt size={20} />
          Logout
        </motion.button>

        <motion.button 
          className="menu-icon" 
          onClick={toggleMenu}
          whileHover={{ rotate: 180 }}
          transition={{ duration: 0.3 }}
        >
          <FaBars size={30} />
        </motion.button>
      </motion.div>

      <motion.div 
        className="video-background"
        animate={{
          scale: 1.05,
          filter: `brightness(${mousePosition.y / window.innerHeight + 0.7})`
        }}
        transition={{ duration: 0.5 }}
      >
        <video autoPlay loop muted>
          <source src={require('./assets/white graph paper - SewBosse (1080p, h264, youtube).mp4')} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </motion.div>

      <motion.div 
        className="hero"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.div 
          className="hero-content"
          animate={{
            x: (mousePosition.x - window.innerWidth / 2) * 0.02,
            y: (mousePosition.y - window.innerHeight / 2) * 0.02
          }}
          transition={{ type: "spring", stiffness: 150, damping: 15 }}
        >
          <motion.h3 
            className="logo"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            BROCHURA
          </motion.h3>
          
          <motion.p 
            className="subtitle"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
          >
            Welcome, {userName}!
          </motion.p>

          <motion.button 
            className="learn-more-button"
            onClick={toggleMenu}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6 }}
          >
            LEARN MORE
          </motion.button>
        </motion.div>
      </motion.div>

      {isMenuOpen && (
        <motion.div
          className="menu-overlay"
          initial={{ opacity: 0, y: '100%' }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: '100%' }}
          transition={{ 
            duration: 0.7, 
            ease: [0.6, -0.05, 0.01, 0.99] 
          }}
        >
          <motion.div 
            className="back-button-container" 
            onClick={toggleMenu}
            whileHover={{ x: -5 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaArrowLeft className="back-arrow" />
            <span className="back-text">BACK</span>
          </motion.div>

          <motion.div 
            className="menu"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {menuItems.map((item, index) => (
              <MenuItem key={item.id} item={item} index={index} handleMenuItemClick={handleMenuItemClick} />
            ))}
          </motion.div>
        </motion.div>
      )}

      <motion.footer 
        className="footer"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.8 }}
      >
        <p>&copy; 2024 BROCHURA. All rights reserved.</p>
      </motion.footer>
    </div>
  );
};

const MenuItem = ({ item, index, handleMenuItemClick }) => {
  const videoRef = useRef(null);
  const navigate = useNavigate();

  const handleMouseEnter = () => {
    if (videoRef.current) {
      videoRef.current.play();
    }
  };

  const handleMouseLeave = () => {
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    }
  };

  const handleLearnMoreClick = () => {
    handleMenuItemClick(item);
  };

  return (
    <motion.div 
      className="menu-item" 
      onMouseEnter={handleMouseEnter} 
      onMouseLeave={handleMouseLeave}
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay: index * 0.1,
        ease: [0.6, -0.05, 0.01, 0.99]
      }}
      whileHover={{ 
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
    >
      <motion.div className="menu-item-content">
        <motion.div 
          className="menu-item-number"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: index * 0.1 + 0.2 }}
        >
          0{item.id}
        </motion.div>

        <motion.div 
          className="menu-item-icon-circle"
          whileHover={{ rotate: 360 }}
          transition={{ duration: 1 }}
        >
          <Lottie
            loop
            animationData={item.lottieAnimation}
            play
            style={{ width: 60, height: 100 }}
          />
        </motion.div>

        <motion.h3 
          className="menu-item-title"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: index * 0.1 + 0.3 }}
        >
          {item.title}
        </motion.h3>
        
        <motion.p 
          className="menu-item-desc"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: index * 0.1 + 0.4 }}
        >
          {item.desc}
        </motion.p>
        
        <motion.p 
          className="menu-item-long-desc"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: index * 0.1 + 0.5 }}
        >
          {item.longDesc}
        </motion.p>

        <video
          className="menu-item-video"
          muted
          loop
          playsInline
          ref={videoRef}
          src={item.video}
        />
        
        <motion.button 
          className="menu-learn-more-button" 
          onClick={handleLearnMoreClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          LEARN MORE
        </motion.button>
      </motion.div>
    </motion.div>
  );
};

export default LandingPage;
