import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Button,
  Divider,
  Link
} from '@mui/material';
import { 
  ExpandMore, 
  Download, 
  CheckCircle, 
  Cancel, 
  Person,
  Email,
  Phone,
  LocationOn,
  LinkedIn,
  Business
} from '@mui/icons-material';
import axios from 'axios';

const ResultsDisplay = ({ results, setError, setLoading }) => {

  const handleExportCSV = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/export-csv', {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'resume_analysis_results.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError('Failed to export CSV');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };

  const getQualitativeColor = (value) => {
    const lowerValue = value?.toLowerCase() || '';
    if (lowerValue.includes('high') || lowerValue.includes('strong')) return 'success';
    if (lowerValue.includes('medium') || lowerValue.includes('moderate')) return 'warning';
    return 'error';
  };

  const ContactInfo = ({ contactInfo }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Person /> {contactInfo?.full_name || 'No Name Available'}
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            {contactInfo?.email && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Email fontSize="small" />
                <Link href={`mailto:${contactInfo.email}`}>{contactInfo.email}</Link>
              </Box>
            )}
            {contactInfo?.phone && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Phone fontSize="small" />
                <Typography variant="body2">{contactInfo.phone}</Typography>
              </Box>
            )}
            {contactInfo?.location && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <LocationOn fontSize="small" />
                <Typography variant="body2">{contactInfo.location}</Typography>
              </Box>
            )}
          </Grid>
          
          <Grid item xs={12} md={6}>
            {contactInfo?.linkedin && contactInfo.linkedin !== 'N/A' && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <LinkedIn fontSize="small" />
                <Link href={contactInfo.linkedin} target="_blank">LinkedIn Profile</Link>
              </Box>
            )}
            {contactInfo?.total_work_experience && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Business fontSize="small" />
                <Typography variant="body2">{contactInfo.total_work_experience}</Typography>
              </Box>
            )}
            {contactInfo?.last_position && (
              <Typography variant="body2" color="text.secondary">
                Last Position: {contactInfo.last_position}
              </Typography>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const RequirementSection = ({ title, items, color = 'primary' }) => {
    const matchedCount = Object.values(items || {}).filter(Boolean).length;
    const totalCount = Object.keys(items || {}).length;
    const percentage = totalCount > 0 ? (matchedCount / totalCount) * 100 : 0;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom color={`${color}.main`}>
            {title}: {matchedCount}/{totalCount}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={percentage}
            color={color}
            sx={{ mb: 2 }}
          />
          <Box>
            {Object.entries(items || {}).map(([key, value]) => (
              <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                {value ? (
                  <CheckCircle color="success" fontSize="small" />
                ) : (
                  <Cancel color="error" fontSize="small" />
                )}
                <Typography variant="body2">{key}</Typography>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  };

  const QualitativeFactors = ({ assessment }) => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Qualitative Assessment
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={4}>
            <Chip
              label={`Project Gravity: ${assessment?.project_gravity || 'N/A'}`}
              color={getQualitativeColor(assessment?.project_gravity)}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Chip
              label={`Ownership: ${assessment?.ownership_and_initiative || 'N/A'}`}
              color={getQualitativeColor(assessment?.ownership_and_initiative)}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Chip
              label={`Fit for Role: ${assessment?.transferability_to_role || 'N/A'}`}
              color={getQualitativeColor(assessment?.transferability_to_role)}
              variant="outlined"
              size="small"
            />
          </Grid>
        </Grid>

        {assessment?.recruiter_style_summary && (
          <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 2 }}>
            {assessment.recruiter_style_summary}
          </Typography>
        )}

        {assessment?.strengths && assessment.strengths.length > 0 && (
          <Box sx={{ mb: 1 }}>
            <Typography variant="subtitle2" color="success.main">Strengths:</Typography>
            {assessment.strengths.map((strength, index) => (
              <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                • {strength}
              </Typography>
            ))}
          </Box>
        )}

        {assessment?.weaknesses && assessment.weaknesses.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="error.main">Weaknesses:</Typography>
            {assessment.weaknesses.map((weakness, index) => (
              <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                • {weakness}
              </Typography>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          Analysis Results ({results.length} candidates)
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={handleExportCSV}
        >
          Export CSV
        </Button>
      </Box>

      {results.map((result, index) => (
        <Accordion key={index} defaultExpanded={index === 0}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Typography variant="h6">
                {result.filename}
              </Typography>
              <Chip
                label={`${result.semantic_percentage}%`}
                color={getScoreColor(result.semantic_percentage)}
                size="small"
              />
              <Typography variant="body2" color="text.secondary">
                Semantic: {result.semantic_percentage}% | Quantitative: {result.quantitative_percentage}%
              </Typography>
            </Box>
          </AccordionSummary>
          
          <AccordionDetails>
            {/* Contact Information */}
            {result.analysis?.contact_info && (
              <ContactInfo contactInfo={result.analysis.contact_info} />
            )}

            {/* Requirements Match */}
            <Typography variant="h6" gutterBottom>
              Requirements Match
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <RequirementSection
                  title="Technical Skills"
                  items={result.analysis?.requirement_match?.must_have_requirements?.technical_skills}
                  color="error"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <RequirementSection
                  title="Core Responsibilities"
                  items={result.analysis?.requirement_match?.must_have_requirements?.core_responsibilities}
                  color="error"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <RequirementSection
                  title="Additional Skills"
                  items={result.analysis?.requirement_match?.good_to_have_requirements?.additional_skills}
                  color="warning"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <RequirementSection
                  title="Screening Criteria"
                  items={result.analysis?.requirement_match?.additional_screening_criteria}
                  color="info"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            {/* Qualitative Assessment */}
            <QualitativeFactors assessment={result.analysis?.qualitative_assessment} />

            <Divider sx={{ my: 2 }} />

            {/* Final Recommendation */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Final Recommendation
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {result.analysis?.final_recommendation}
                </Typography>
                
                <Typography variant="subtitle2" gutterBottom>
                  Key Factors:
                </Typography>
                {result.analysis?.summary_of_key_factors?.map((factor, index) => (
                  <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                    • {factor}
                  </Typography>
                ))}
              </CardContent>
            </Card>
          </AccordionDetails>
        </Accordion>
      ))}
    </Paper>
  );
};

export default ResultsDisplay; 