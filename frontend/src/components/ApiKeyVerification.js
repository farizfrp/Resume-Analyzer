import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  InputAdornment,
  IconButton
} from '@mui/material';
import { Visibility, VisibilityOff, Key } from '@mui/icons-material';
import axios from 'axios';

const ApiKeyVerification = ({ onVerified, setError, setLoading, clearMessages }) => {
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);

  const handleVerifyApiKey = async () => {
    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }

    clearMessages();
    setLoading(true);

    try {
      const response = await axios.post('/api/verify-api-key', {
        api_key: apiKey
      });

      if (response.data.success) {
        onVerified();
      } else {
        setError(response.data.message || 'API key verification failed');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Invalid API key. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleVerifyApiKey();
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Key /> API Key Verification
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Enter your OpenAI API key to enable the resume analysis features.
      </Typography>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="OpenAI API Key"
          type={showApiKey ? 'text' : 'password'}
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="sk-..."
          variant="outlined"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowApiKey(!showApiKey)}
                  edge="end"
                >
                  {showApiKey ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Button
        variant="contained"
        onClick={handleVerifyApiKey}
        disabled={!apiKey.trim()}
        size="large"
      >
        Verify API Key
      </Button>
    </Box>
  );
};

export default ApiKeyVerification; 