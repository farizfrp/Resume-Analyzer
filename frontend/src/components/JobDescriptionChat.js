import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Avatar,
  IconButton,
  CircularProgress,
  Chip
} from '@mui/material';
import { 
  Send, 
  Person, 
  SmartToy, 
  ContentCopy,
  CheckCircle 
} from '@mui/icons-material';
import axios from 'axios';

const JobDescriptionChat = ({ onJobDescriptionGenerated, onApplyJobDescription, clearMessages }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hi! I'm here to help you create a comprehensive job description. Let's start with some basic information. What's the job title you're looking to hire for? You can also choose from our predefined company profiles below.",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState({
    jobTitle: '',
    company: '',
    department: '',
    requirements: [],
    responsibilities: [],
    benefits: [],
    experience: '',
    skills: [],
    step: 'job_title'
  });
  const messagesEndRef = useRef(null);

  // Predefined company profiles
  const companyProfiles = {
    'Boga Group': {
      overview: `Boga Group currently operates hundreds of restaurants with a workforce of thousands of highly trained professionals. This rapid and successful expansion is attributed to a steadfast commitment to utilizing only high-quality ingredients paired with exceptional service. These distinguishing characteristics set Boga apart within the industry. Each brand under Boga Group is renowned for understanding customers' needs and delivering memorable dining experiences.

Boga Group's diverse portfolio includes 9 Bakerzin, 86 Pepper Lunch, 71 Kimukatsu, 7 Paradise Dynasty, 1 Shaburi, 4 Kintan Buffet, 15 Shaburi Kintan, 3 Putu Made, 24 Yakiniku Like, 2 Ocean8, 6 Ebiga, 2 Leten and 13 Loaf Bun. These spreads across various cities in Indonesia, including Greater Jakarta, Bandung, Surabaya, Malang, Jember, Jogja, Solo, Semarang, Medan, Batam, Pekanbaru, Balikpapan, Samarinda, Pontianak, Palembang, Makassar, Manado and Bali. Boga Group also operates Boga Catering, a premium catering service and Creative Culinary, a central production facility that supports brand operations.`,
      benefits: 'Benefit cuti 12 hari, BPJS, THR, Diskon karyawan'
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/job-description-chat', {
        message: inputMessage.trim(),
        context: conversationContext,
        messages: messages
      });

      if (response.data.success) {
        const assistantMessage = {
          id: messages.length + 2,
          type: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          jobDescription: response.data.jobDescription || null
        };

        setMessages(prev => [...prev, assistantMessage]);
        setConversationContext(response.data.context);
      }
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: "I apologize, but I'm having trouble processing your request. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUseJobDescription = (jobDescription) => {
    onJobDescriptionGenerated(jobDescription);
  };

  const handleApplyJobDescription = (jobDescription) => {
    if (onApplyJobDescription) {
      onApplyJobDescription(jobDescription);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleCompanyProfileSelection = (companyName) => {
    const profile = companyProfiles[companyName];
    if (profile) {
      setInputMessage(`I want to create a job description for ${companyName}. Here's our company overview: ${profile.overview}. Our benefits include: ${profile.benefits}`);
      
      // Update context with company info
      setConversationContext(prev => ({
        ...prev,
        company: companyName,
        companyOverview: profile.overview,
        benefits: [profile.benefits]
      }));
    }
  };

  const suggestedPrompts = [
    "Software Engineer at a tech startup",
    "Marketing Manager for an e-commerce company",
    "Data Analyst for a healthcare organization",
    "Product Manager for a SaaS company"
  ];

  const companyPrompts = Object.keys(companyProfiles);

  return (
    <Box sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SmartToy /> Job Description Assistant
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Chat with AI to create a detailed job description step by step
      </Typography>

      {/* Suggested Prompts - only show initially */}
      {messages.length === 1 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>Company profiles:</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            {companyPrompts.map((company, index) => (
              <Chip
                key={index}
                label={company}
                onClick={() => handleCompanyProfileSelection(company)}
                variant="contained"
                color="primary"
                size="small"
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
          
          <Typography variant="body2" sx={{ mb: 1 }}>Quick starts:</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {suggestedPrompts.map((prompt, index) => (
              <Chip
                key={index}
                label={prompt}
                onClick={() => setInputMessage(prompt)}
                variant="outlined"
                size="small"
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Messages Container */}
      <Paper 
        sx={{ 
          flex: 1, 
          p: 2, 
          mb: 2, 
          overflowY: 'auto',
          bgcolor: 'background.default',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 2,
              mb: 2,
              flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
            }}
          >
            <Avatar sx={{ width: 32, height: 32 }}>
              {message.type === 'user' ? <Person /> : <SmartToy />}
            </Avatar>
            
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: message.type === 'user' ? 'primary.main' : 'background.paper',
                  color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                  borderRadius: 2,
                  maxWidth: '80%',
                  marginLeft: message.type === 'user' ? 'auto' : 0,
                  marginRight: message.type === 'user' ? 0 : 'auto'
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
                
                {message.jobDescription && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Generated Job Description:
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 2 }}>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                        {message.jobDescription}
                      </Typography>
                    </Paper>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<CheckCircle />}
                        onClick={() => handleApplyJobDescription(message.jobDescription)}
                        sx={{ bgcolor: 'success.main', '&:hover': { bgcolor: 'success.dark' } }}
                      >
                        Apply & Analyze
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleUseJobDescription(message.jobDescription)}
                      >
                        Use Job Description
                      </Button>
                      <IconButton
                        size="small"
                        onClick={() => copyToClipboard(message.jobDescription)}
                        title="Copy to clipboard"
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                )}
              </Paper>
              
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {message.timestamp.toLocaleTimeString()}
              </Typography>
            </Box>
          </Box>
        ))}
        
        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Avatar sx={{ width: 32, height: 32 }}>
              <SmartToy />
            </Avatar>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                AI is thinking...
              </Typography>
            </Box>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Paper>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          variant="outlined"
          disabled={isLoading}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
          sx={{ minWidth: 'auto', px: 2 }}
        >
          <Send />
        </Button>
      </Box>
    </Box>
  );
};

export default JobDescriptionChat; 