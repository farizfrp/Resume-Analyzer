import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import { Edit, Save, SkipNext } from '@mui/icons-material';
import axios from 'axios';

const RequirementsEditor = ({ 
  requirements, 
  onRequirementsUpdated, 
  onSkip, 
  setError, 
  setLoading, 
  clearMessages 
}) => {
  const [mustHaveText, setMustHaveText] = useState('');
  const [preferredText, setPreferredText] = useState('');
  const [additionalText, setAdditionalText] = useState('');

  useEffect(() => {
    if (requirements) {
      formatRequirementsForEditing();
    }
  }, [requirements]);

  const formatRequirementsForEditing = () => {
    let mustHave = [];
    if (requirements.must_have_requirements) {
      const must = requirements.must_have_requirements;
      mustHave.push("Technical Skills:");
      must.technical_skills?.forEach(skill => mustHave.push(`- ${skill}`));
      mustHave.push("\nExperience:");
      mustHave.push(`- ${must.experience || ''}`);
      mustHave.push("\nQualifications:");
      must.qualifications?.forEach(qual => mustHave.push(`- ${qual}`));
      mustHave.push("\nCore Responsibilities:");
      must.core_responsibilities?.forEach(resp => mustHave.push(`- ${resp}`));
    }

    let preferred = [];
    if (requirements.good_to_have_requirements) {
      const good = requirements.good_to_have_requirements;
      preferred.push("Additional Skills:");
      good.additional_skills?.forEach(skill => preferred.push(`- ${skill}`));
      preferred.push("\nExtra Qualifications:");
      good.extra_qualifications?.forEach(qual => preferred.push(`- ${qual}`));
      preferred.push("\nBonus Experience:");
      good.bonus_experience?.forEach(exp => preferred.push(`- ${exp}`));
    }

    let additional = [];
    if (requirements.additional_screening_criteria) {
      requirements.additional_screening_criteria.forEach(criteria => 
        additional.push(`- ${criteria}`)
      );
    }

    setMustHaveText(mustHave.join('\n'));
    setPreferredText(preferred.join('\n'));
    setAdditionalText(additional.join('\n'));
  };

  const handleUpdateRequirements = async () => {
    clearMessages();
    setLoading(true);

    try {
      const response = await axios.post('/api/update-requirements', {
        must_have_text: mustHaveText,
        preferred_text: preferredText,
        additional_text: additionalText
      });

      if (response.data.success) {
        onRequirementsUpdated(response.data.requirements);
      } else {
        setError(response.data.message || 'Failed to update requirements');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Error updating requirements. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Edit /> Edit Requirements
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Review and edit the extracted requirements. You can modify the text to better match your needs, 
        or skip this step to proceed with the current requirements.
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="error">
                Must-Have Requirements
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={12}
                value={mustHaveText}
                onChange={(e) => setMustHaveText(e.target.value)}
                variant="outlined"
                placeholder="Technical Skills:
- Skill 1
- Skill 2

Experience:
- Minimum years required

Qualifications:
- Degree requirements
- Certifications

Core Responsibilities:
- Key responsibilities"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="warning.main">
                Preferred Requirements
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={12}
                value={preferredText}
                onChange={(e) => setPreferredText(e.target.value)}
                variant="outlined"
                placeholder="Additional Skills:
- Nice to have skill 1
- Nice to have skill 2

Extra Qualifications:
- Bonus certifications

Bonus Experience:
- Additional experience"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="info.main">
                Additional Screening Criteria
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={12}
                value={additionalText}
                onChange={(e) => setAdditionalText(e.target.value)}
                variant="outlined"
                placeholder="- Work authorization requirements
- Location constraints
- Availability requirements
- Other screening criteria"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          onClick={handleUpdateRequirements}
          size="large"
          startIcon={<Save />}
        >
          Update Requirements
        </Button>
        
        <Button
          variant="outlined"
          onClick={onSkip}
          size="large"
          startIcon={<SkipNext />}
        >
          Skip & Continue
        </Button>
      </Box>
    </Box>
  );
};

export default RequirementsEditor; 