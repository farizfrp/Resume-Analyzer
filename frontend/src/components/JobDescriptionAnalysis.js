import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import { Work, Analytics, Chat, Create } from '@mui/icons-material';
import axios from 'axios';
import JobDescriptionChat from './JobDescriptionChat';

const JobDescriptionAnalysis = ({ 
  jobDescription, 
  setJobDescription, 
  onJobAnalyzed, 
  selectedModels, 
  setError, 
  setLoading, 
  clearMessages 
}) => {
  const [activeTab, setActiveTab] = useState(0);

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

  const handleJobDescriptionGenerated = (generatedJobDescription) => {
    setJobDescription(generatedJobDescription);
    setActiveTab(1); // Switch to manual editing tab
  };

  const handleApplyJobDescription = async (generatedJobDescription) => {
    setJobDescription(generatedJobDescription);
    clearMessages();
    setLoading(true);

    try {
      const response = await axios.post('/api/analyze-job-description', {
        job_description: generatedJobDescription,
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

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Work /> Job Description Analysis
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Create or paste a job description to extract and analyze the requirements. 
        The AI will identify must-have skills, preferred qualifications, and screening criteria.
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<Chat />} 
            label="AI Assistant" 
            iconPosition="start"
            sx={{ textTransform: 'none' }}
          />
          <Tab 
            icon={<Create />} 
            label="Manual Entry" 
            iconPosition="start"
            sx={{ textTransform: 'none' }}
          />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {activeTab === 0 && (
            <JobDescriptionChat
              onJobDescriptionGenerated={handleJobDescriptionGenerated}
              onApplyJobDescription={handleApplyJobDescription}
              clearMessages={clearMessages}
            />
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Paste or type your job description here:
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
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default JobDescriptionAnalysis; 