import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Paper,
  Box,
  Stepper,
  Step,
  StepLabel,
  Alert,
  LinearProgress,
  CssBaseline,
  ThemeProvider,
  createTheme
} from '@mui/material';
import axios from 'axios';

// Import components
import ModelSelection from './components/ModelSelection';
import JobDescriptionAnalysis from './components/JobDescriptionAnalysis';
import RequirementsEditor from './components/RequirementsEditor';
import ResumeAnalysis from './components/ResumeAnalysis';
import ResultsDisplay from './components/ResultsDisplay';

// Create dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
});

const steps = [
  'Model Selection',
  'Job Analysis',
  'Requirements Review',
  'Resume Analysis'
];

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedModels, setSelectedModels] = useState({
    primary: 'gpt-4.1',
    reasoning: 'o4-mini'
  });
  const [jobDescription, setJobDescription] = useState('');
  const [requirements, setRequirements] = useState(null);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Check if API key is working on mount
  useEffect(() => {
    checkApiKeyStatus();
  }, []);

  const checkApiKeyStatus = async () => {
    try {
      const response = await axios.get('/api/check-api-key');
      if (response.data.success) {
        setSuccess('API key loaded and verified!');
      } else {
        setError('API key not working. Please check your .env file.');
      }
    } catch (error) {
      setError('Failed to connect to API. Please ensure the backend is running and API key is set in .env file.');
      console.error('Failed to check API status:', error);
    }
  };

  const handleModelsUpdated = (models) => {
    setSelectedModels(models);
    setActiveStep(1);
    setSuccess('Models updated successfully!');
  };

  const handleJobAnalyzed = (analyzedRequirements) => {
    setRequirements(analyzedRequirements);
    setActiveStep(2);
    setSuccess('Job description analyzed successfully!');
  };

  const handleRequirementsUpdated = (updatedRequirements) => {
    setRequirements(updatedRequirements);
    setActiveStep(3);
    setSuccess('Requirements updated successfully!');
  };

  const handleResumeAnalyzed = (results) => {
    setAnalysisResults(results);
    setSuccess(`Analyzed ${results.length} resumes successfully!`);
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  const getCurrentStepComponent = () => {
    switch (activeStep) {
      case 0:
        return (
          <ModelSelection
            selectedModels={selectedModels}
            onModelsUpdated={handleModelsUpdated}
            setError={setError}
            clearMessages={clearMessages}
          />
        );
      case 1:
        return (
          <JobDescriptionAnalysis
            jobDescription={jobDescription}
            setJobDescription={setJobDescription}
            onJobAnalyzed={handleJobAnalyzed}
            selectedModels={selectedModels}
            setError={setError}
            setLoading={setLoading}
            clearMessages={clearMessages}
          />
        );
      case 2:
        return (
          <RequirementsEditor
            requirements={requirements}
            onRequirementsUpdated={handleRequirementsUpdated}
            onSkip={() => setActiveStep(3)}
            setError={setError}
            setLoading={setLoading}
            clearMessages={clearMessages}
          />
        );
      case 3:
        return (
          <ResumeAnalysis
            requirements={requirements}
            onResumeAnalyzed={handleResumeAnalyzed}
            selectedModels={selectedModels}
            setError={setError}
            setLoading={setLoading}
            clearMessages={clearMessages}
          />
        );
      default:
        return null;
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Resume Ranking System
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          {/* Progress Stepper */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Stepper activeStep={activeStep} alternativeLabel>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Paper>

          {/* Loading Indicator */}
          {loading && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress />
            </Box>
          )}

          {/* Error Alert */}
          {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 2 }}
              onClose={() => setError('')}
            >
              {error}
            </Alert>
          )}

          {/* Success Alert */}
          {success && (
            <Alert 
              severity="success" 
              sx={{ mb: 2 }}
              onClose={() => setSuccess('')}
            >
              {success}
            </Alert>
          )}

          {/* Current Step Component */}
          <Paper sx={{ p: 3, mb: 3 }}>
            {getCurrentStepComponent()}
          </Paper>

          {/* Results Display */}
          {analysisResults.length > 0 && (
            <ResultsDisplay
              results={analysisResults}
              setError={setError}
              setLoading={setLoading}
            />
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App; 