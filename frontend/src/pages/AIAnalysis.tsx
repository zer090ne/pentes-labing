import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { scanApi } from '../services/api';
import { aiApi } from '../services/aiApi';
import AIAnalysis from '../components/AIAnalysis';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ai-tabpanel-${index}`}
      aria-labelledby={`ai-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function AIAnalysisPage() {
  const [selectedScan, setSelectedScan] = useState<number | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');

  const queryClient = useQueryClient();

  // Get AI status
  const { data: aiStatus, isLoading: statusLoading } = useQuery(
    'ai-status',
    () => aiApi.getStatus(),
    {
      select: (response) => response.data,
    }
  );

  // Get completed scans
  const { data: scans, isLoading: scansLoading } = useQuery(
    'completed-scans',
    () => scanApi.getAll({ limit: 100 }),
    {
      select: (response) => response.data?.filter((scan: any) => scan.status === 'completed') || [],
    }
  );

  // AI analysis mutation
  const analysisMutation = useMutation(
    () => aiApi.analyzeScan(selectedScan!),
    {
      onSuccess: () => {
        showMessage('AI analysis completed successfully!', 'success');
        queryClient.invalidateQueries(['ai-insights', selectedScan]);
      },
      onError: () => {
        showMessage('AI analysis failed', 'error');
      },
    }
  );

  // AI report generation mutation
  const reportMutation = useMutation(
    () => aiApi.generateReport(selectedScan!),
    {
      onSuccess: (response) => {
        // Download the report
        const blob = new Blob([response.data.report_content], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-report-scan-${selectedScan}.html`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showMessage('AI report downloaded successfully!', 'success');
      },
      onError: () => {
        showMessage('AI report generation failed', 'error');
      },
    }
  );

  const showMessage = (message: string, severity: 'success' | 'error' | 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setShowSnackbar(true);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (statusLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading AI status...</Typography>
      </Box>
    );
  }

  if (!aiStatus?.ai_enabled) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          AI Analysis
        </Typography>
        <Alert severity="warning">
          AI Analysis is not available. Please configure your Groq API key in the environment variables.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          AI Security Analysis
        </Typography>
        <Chip
          icon={<PsychologyIcon />}
          label={`Powered by ${aiStatus.model}`}
          color="primary"
          variant="outlined"
        />
      </Box>

      {/* Scan Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Scan for AI Analysis
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Completed Scans</InputLabel>
                <Select
                  value={selectedScan || ''}
                  label="Completed Scans"
                  onChange={(e) => setSelectedScan(Number(e.target.value))}
                >
                  {scans?.map((scan: any) => (
                    <MenuItem key={scan.id} value={scan.id}>
                      {scan.name} - {scan.target} ({scan.scan_type})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => analysisMutation.mutate()}
                  disabled={!selectedScan || analysisMutation.isLoading}
                >
                  {analysisMutation.isLoading ? 'Analyzing...' : 'Run AI Analysis'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => reportMutation.mutate()}
                  disabled={!selectedScan || reportMutation.isLoading}
                >
                  {reportMutation.isLoading ? 'Generating...' : 'Generate Report'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* AI Analysis Tabs */}
      {selectedScan && (
        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="AI analysis tabs"
            variant="fullWidth"
          >
            <Tab
              icon={<PsychologyIcon />}
              label="AI Analysis"
              iconPosition="start"
            />
            <Tab
              icon={<SecurityIcon />}
              label="Vulnerability Assessment"
              iconPosition="start"
            />
            <Tab
              icon={<AssessmentIcon />}
              label="Recommendations"
              iconPosition="start"
            />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <AIAnalysis
              scanId={selectedScan}
              onAnalysisComplete={(analysis) => {
                console.log('AI Analysis completed:', analysis);
                showMessage('AI analysis completed successfully!', 'success');
              }}
            />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Typography variant="h6" gutterBottom>
              Vulnerability Assessment
            </Typography>
            <Alert severity="info">
              Detailed vulnerability assessment will be available after running AI analysis.
            </Alert>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>
              AI Recommendations
            </Typography>
            <Alert severity="info">
              AI-powered recommendations will be available after running AI analysis.
            </Alert>
          </TabPanel>
        </Paper>
      )}

      {/* AI Features Overview */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Intelligent Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI-powered analysis of scan results with advanced pattern recognition and threat assessment.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <SecurityIcon sx={{ fontSize: 40, color: 'warning.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Risk Assessment
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Comprehensive risk scoring and vulnerability prioritization based on industry standards.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <AssessmentIcon sx={{ fontSize: 40, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Smart Recommendations
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Actionable recommendations with priority levels and implementation guidance.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={showSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowSnackbar(false)}
      >
        <Alert onClose={() => setShowSnackbar(false)} severity={snackbarSeverity}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}
