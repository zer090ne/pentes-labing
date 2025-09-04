import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from 'react-query';
import { aiApi } from '../services/aiApi';

interface AIAnalysisProps {
  scanId: number;
  onAnalysisComplete?: (analysis: any) => void;
}

export default function AIAnalysis({ scanId, onAnalysisComplete }: AIAnalysisProps) {
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);

  // Get AI status
  const { data: aiStatus } = useQuery(
    'ai-status',
    () => aiApi.getStatus(),
    {
      select: (response) => response.data,
    }
  );

  // Get AI insights
  const { data: insights, isLoading: insightsLoading } = useQuery(
    ['ai-insights', scanId],
    () => aiApi.getInsights(scanId),
    {
      enabled: !!scanId,
      select: (response) => response.data,
    }
  );

  // AI analysis mutation
  const analysisMutation = useMutation(
    () => aiApi.analyzeScan(scanId),
    {
      onSuccess: (response) => {
        if (onAnalysisComplete) {
          onAnalysisComplete(response.data);
        }
      },
    }
  );

  // AI report generation mutation
  const reportMutation = useMutation(
    () => aiApi.generateReport(scanId),
    {
      onSuccess: (response) => {
        // Handle report generation success
        console.log('AI report generated:', response.data);
      },
    }
  );

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return <WarningIcon color="error" />;
      case 'high': return <WarningIcon color="warning" />;
      case 'medium': return <SecurityIcon color="info" />;
      case 'low': return <CheckCircleIcon color="success" />;
      default: return <SecurityIcon />;
    }
  };

  if (!aiStatus?.ai_enabled) {
    return (
      <Card>
        <CardContent>
          <Alert severity="warning">
            AI Analysis is not available. Please check your Groq API configuration.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box display="flex" alignItems="center">
              <PsychologyIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">AI Security Analysis</Typography>
            </Box>
            <Chip
              label={`Model: ${aiStatus?.model || 'N/A'}`}
              color="primary"
              size="small"
            />
          </Box>

          {insightsLoading ? (
            <Box display="flex" alignItems="center" justifyContent="center" py={4}>
              <CircularProgress />
              <Typography variant="body2" sx={{ ml: 2 }}>
                Analyzing with AI...
              </Typography>
            </Box>
          ) : insights ? (
            <Box>
              {/* Risk Assessment */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={1}>
                        {getRiskIcon(insights.insights?.risk_level)}
                        <Typography variant="h6" sx={{ ml: 1 }}>
                          Risk Level
                        </Typography>
                      </Box>
                      <Chip
                        label={insights.insights?.risk_level?.toUpperCase() || 'UNKNOWN'}
                        color={getRiskColor(insights.insights?.risk_level)}
                        size="large"
                      />
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Score: {insights.insights?.risk_score || 0}/100
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Vulnerabilities
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        <Chip
                          label={`${insights.insights?.critical_vulnerabilities || 0} Critical`}
                          color="error"
                          size="small"
                        />
                        <Chip
                          label={`${insights.insights?.high_vulnerabilities || 0} High`}
                          color="warning"
                          size="small"
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Actions Required
                      </Typography>
                      <Chip
                        label={`${insights.insights?.immediate_actions || 0} Immediate`}
                        color="error"
                        size="small"
                      />
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* AI Confidence */}
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="body2" sx={{ mr: 1 }}>
                  AI Confidence:
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={insights.insights?.ai_confidence || 0}
                  sx={{ flexGrow: 1, mr: 1 }}
                />
                <Typography variant="body2">
                  {insights.insights?.ai_confidence || 0}%
                </Typography>
              </Box>

              {/* Top Recommendation */}
              {insights.insights?.top_recommendation && (
                <Card variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🎯 Top AI Recommendation
                    </Typography>
                    <Typography variant="body1">
                      {insights.insights.top_recommendation.title || 'No recommendation available'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {insights.insights.top_recommendation.description || ''}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {/* Action Buttons */}
              <Box display="flex" gap={2} flexWrap="wrap">
                <Button
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => analysisMutation.mutate()}
                  disabled={analysisMutation.isLoading}
                >
                  {analysisMutation.isLoading ? 'Analyzing...' : 'Run Full AI Analysis'}
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<PsychologyIcon />}
                  onClick={() => reportMutation.mutate()}
                  disabled={reportMutation.isLoading}
                >
                  {reportMutation.isLoading ? 'Generating...' : 'Generate AI Report'}
                </Button>

                <Button
                  variant="text"
                  onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                >
                  {showFullAnalysis ? 'Hide' : 'Show'} Full Analysis
                </Button>
              </Box>

              {/* Full Analysis */}
              {showFullAnalysis && (
                <Box sx={{ mt: 3 }}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Full AI Analysis
                  </Typography>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>AI Analysis Details</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box
                        component="pre"
                        sx={{
                          backgroundColor: '#f5f5f5',
                          p: 2,
                          borderRadius: 1,
                          overflow: 'auto',
                          maxHeight: 400,
                          fontSize: '0.875rem',
                        }}
                      >
                        {JSON.stringify(insights, null, 2)}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                </Box>
              )}
            </Box>
          ) : (
            <Box textAlign="center" py={4}>
              <PsychologyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No AI Analysis Available
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Run a scan first to get AI-powered security analysis
              </Typography>
              <Button
                variant="contained"
                startIcon={<PlayArrowIcon />}
                onClick={() => analysisMutation.mutate()}
                disabled={analysisMutation.isLoading}
              >
                {analysisMutation.isLoading ? 'Analyzing...' : 'Start AI Analysis'}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Error Handling */}
      {analysisMutation.error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          AI Analysis failed: {(analysisMutation.error as any)?.response?.data?.detail || 'Unknown error'}
        </Alert>
      )}

      {reportMutation.error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          AI Report generation failed: {(reportMutation.error as any)?.response?.data?.detail || 'Unknown error'}
        </Alert>
      )}
    </Box>
  );
}
