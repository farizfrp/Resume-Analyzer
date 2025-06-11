import React, { useState } from 'react';
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import { Settings, Psychology, Speed } from '@mui/icons-material';

const ModelSelection = ({ selectedModels, onModelsUpdated, setError, clearMessages }) => {
  const [primaryModel, setPrimaryModel] = useState(selectedModels.primary);
  const [reasoningModel, setReasoningModel] = useState(selectedModels.reasoning);

  const primaryModelOptions = [
    { value: 'gpt-4.1', label: 'GPT-4.1', description: 'Latest and most capable model' },
    { value: 'gpt-4.0', label: 'GPT-4.0', description: 'Balanced performance and cost' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo', description: 'Fast and cost-effective' }
  ];

  const reasoningModelOptions = [
    { value: 'o4-mini', label: 'O4-Mini', description: 'Optimized for reasoning tasks' },
    { value: 'o1-mini', label: 'O1-Mini', description: 'Advanced reasoning capabilities' },
    { value: 'o1-preview', label: 'O1-Preview', description: 'Latest reasoning model (preview)' }
  ];

  const handleUpdateModels = () => {
    clearMessages();
    
    const updatedModels = {
      primary: primaryModel,
      reasoning: reasoningModel
    };
    
    onModelsUpdated(updatedModels);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Settings /> Model Selection
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Choose the AI models for different tasks. The primary model handles general analysis, 
        while the reasoning model focuses on complex evaluation tasks.
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Speed /> Primary Model
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Used for job description analysis and general tasks
              </Typography>
              
              <FormControl fullWidth>
                <InputLabel>Primary Model</InputLabel>
                <Select
                  value={primaryModel}
                  onChange={(e) => setPrimaryModel(e.target.value)}
                  label="Primary Model"
                >
                  {primaryModelOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box>
                        <Typography variant="body1">{option.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Psychology /> Reasoning Model
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Used for complex resume analysis and evaluation
              </Typography>
              
              <FormControl fullWidth>
                <InputLabel>Reasoning Model</InputLabel>
                <Select
                  value={reasoningModel}
                  onChange={(e) => setReasoningModel(e.target.value)}
                  label="Reasoning Model"
                >
                  {reasoningModelOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box>
                        <Typography variant="body1">{option.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Button
        variant="contained"
        onClick={handleUpdateModels}
        size="large"
      >
        Update Models
      </Button>
    </Box>
  );
};

export default ModelSelection; 