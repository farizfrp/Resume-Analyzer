import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Alert
} from '@mui/material';
import { CloudUpload, Delete, Assessment } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const ResumeAnalysis = ({ 
  requirements, 
  onResumeAnalyzed, 
  selectedModels, 
  setError, 
  setLoading, 
  clearMessages 
}) => {
  const [files, setFiles] = useState([]);

  const onDrop = (acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    multiple: true
  });

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyzeResumes = async () => {
    if (files.length === 0) {
      setError('Please upload at least one resume');
      return;
    }

    if (!requirements) {
      setError('Please analyze job description first');
      return;
    }

    clearMessages();
    setLoading(true);

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      formData.append('model', selectedModels.reasoning);

      const response = await axios.post('/api/analyze-resumes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        onResumeAnalyzed(response.data.results);
      } else {
        setError(response.data.message || 'Failed to analyze resumes');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Error analyzing resumes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Assessment /> Resume Analysis
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Upload resume files (PDF, DOCX, or TXT) to analyze against the job requirements. 
        The system will extract contact information, match requirements, and provide detailed analysis.
      </Typography>

      {/* File Upload Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.500',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          textAlign: 'center',
          '&:hover': {
            bgcolor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the files here...' : 'Drag & drop resume files here'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          or click to select files (PDF, DOCX, TXT)
        </Typography>
      </Paper>

      {/* Uploaded Files List */}
      {files.length > 0 && (
        <Paper sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            Uploaded Files ({files.length})
          </Typography>
          <List>
            {files.map((file, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={file.name}
                  secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={() => removeFile(index)}>
                    <Delete />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Analysis Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          onClick={handleAnalyzeResumes}
          disabled={files.length === 0}
          size="large"
          startIcon={<Assessment />}
        >
          Analyze {files.length} Resume{files.length !== 1 ? 's' : ''}
        </Button>
      </Box>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Analysis Process:</strong>
          <br />• Contact information extraction
          <br />• Quantitative requirement matching  
          <br />• Qualitative assessment (project gravity, ownership, transferability)
          <br />• Semantic scoring and ranking
        </Typography>
      </Alert>
    </Box>
  );
};

export default ResumeAnalysis; 