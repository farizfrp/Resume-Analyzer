import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Button
} from '@mui/material';
import { Work, Analytics } from '@mui/icons-material';
import axios from 'axios';

const JobDescriptionAnalysis = ({ 
  jobDescription, 
  setJobDescription, 
  onJobAnalyzed, 
  selectedModels, 
  setError, 
  setLoading, 
  clearMessages 
}) => {

  const handleAnalyzeJobDescription = async () => {
    if (!jobDescription.trim()) {
      setError('Please provide a job description');
      return;
    }

    clearMessages();
    setLoading(true);

    try {
      const response = await axios.post('/api/analyze-job-description', {
        job_description: jobDescription,
        model: selectedModels.primary
      });

      if (response.data.success) {
        onJobAnalyzed(response.data.requirements);
      } else {
        setError(response.data.message || 'Failed to analyze job description');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Error analyzing job description. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Work /> Job Description Analysis
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Enter the job description to extract and analyze the requirements. 
        The AI will identify must-have skills, preferred qualifications, and screening criteria.
      </Typography>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={12}
          label="Job Description"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the complete job description here..."
          variant="outlined"
        />
      </Box>

      <Button
        variant="contained"
        onClick={handleAnalyzeJobDescription}
        disabled={!jobDescription.trim()}
        size="large"
        startIcon={<Analytics />}
      >
        Analyze Job Description
      </Button>
    </Box>
  );
};

export default JobDescriptionAnalysis; 