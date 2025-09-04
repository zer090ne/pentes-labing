import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Build as BuildIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { scanApi } from '../services/api';
import { useWebSocket } from '../contexts/WebSocketContext';
import { aiApi } from '../services/aiApi';

interface ScanStats {
  total: number;
  running: number;
  completed: number;
  failed: number;
}

export default function Dashboard() {
  const [scanForm, setScanForm] = useState({
    name: '',
    target: '',
    scan_type: 'nmap',
  });
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const { lastMessage } = useWebSocket();
  const queryClient = useQueryClient();

  // Get AI status
  const { data: aiStatus } = useQuery(
    'ai-status',
    () => aiApi.getStatus(),
    {
      select: (response) => response.data,
    }
  );

  // Fetch scan statistics
  const { data: scans, isLoading: scansLoading } = useQuery(
    'scans',
    () => scanApi.getAll({ limit: 100 }),
    {
      select: (response) => response.data,
    }
  );

  // Create scan mutation
  const createScanMutation = useMutation(scanApi.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('scans');
      setSnackbarMessage('Scan started successfully!');
      setShowSnackbar(true);
      setScanForm({ name: '', target: '', scan_type: 'nmap' });
    },
    onError: () => {
      setSnackbarMessage('Failed to start scan');
      setShowSnackbar(true);
    },
  });

  // Calculate statistics
  const stats: ScanStats = scans?.reduce(
    (acc, scan) => {
      acc.total++;
      if (scan.status === 'running') acc.running++;
      else if (scan.status === 'completed') acc.completed++;
      else if (scan.status === 'failed') acc.failed++;
      return acc;
    },
    { total: 0, running: 0, completed: 0, failed: 0 }
  ) || { total: 0, running: 0, completed: 0, failed: 0 };

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'scan_update') {
        queryClient.invalidateQueries('scans');
        setSnackbarMessage(`Scan ${lastMessage.data.scan_id} ${lastMessage.data.status}`);
        setShowSnackbar(true);
      }
    }
  }, [lastMessage, queryClient]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!scanForm.name || !scanForm.target) {
      setSnackbarMessage('Please fill in all fields');
      setShowSnackbar(true);
      return;
    }
    createScanMutation.mutate(scanForm);
  };

  const StatCard = ({ title, value, icon, color }: any) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box color={color} fontSize="large">
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Dashboard
        </Typography>
        {aiStatus?.ai_enabled && (
          <Chip
            icon={<PsychologyIcon />}
            label={`AI Powered - ${aiStatus.model}`}
            color="primary"
            variant="outlined"
          />
        )}
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Scans"
            value={stats.total}
            icon={<AssessmentIcon />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Running"
            value={stats.running}
            icon={<PlayIcon />}
            color="warning.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={stats.completed}
            icon={<SecurityIcon />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Failed"
            value={stats.failed}
            icon={<BuildIcon />}
            color="error.main"
          />
        </Grid>
      </Grid>

      {/* Quick Scan Form */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Scan
          </Typography>
          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={3}>
                <TextField
                  fullWidth
                  label="Scan Name"
                  value={scanForm.name}
                  onChange={(e) => setScanForm({ ...scanForm, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  fullWidth
                  label="Target (IP/Domain)"
                  value={scanForm.target}
                  onChange={(e) => setScanForm({ ...scanForm, target: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <FormControl fullWidth>
                  <InputLabel>Scan Type</InputLabel>
                  <Select
                    value={scanForm.scan_type}
                    label="Scan Type"
                    onChange={(e) => setScanForm({ ...scanForm, scan_type: e.target.value })}
                  >
                    <MenuItem value="nmap">Nmap (Port Scan)</MenuItem>
                    <MenuItem value="nikto">Nikto (Web Vuln)</MenuItem>
                    <MenuItem value="comprehensive">Comprehensive</MenuItem>
                    <MenuItem value="hydra">Hydra (Brute Force)</MenuItem>
                    <MenuItem value="sqlmap">SQLMap (SQL Injection)</MenuItem>
                    <MenuItem value="gobuster">Gobuster (Dir Enum)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={<PlayIcon />}
                  disabled={createScanMutation.isLoading}
                  fullWidth
                >
                  Start Scan
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>

      {/* Recent Scans */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Scans
          </Typography>
          {scansLoading ? (
            <LinearProgress />
          ) : (
            <Box>
              {scans?.slice(0, 5).map((scan: any) => (
                <Box
                  key={scan.id}
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  py={1}
                  borderBottom="1px solid #eee"
                >
                  <Box>
                    <Typography variant="subtitle1">{scan.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {scan.target} • {scan.scan_type}
                    </Typography>
                  </Box>
                  <Chip
                    label={scan.status}
                    color={
                      scan.status === 'completed'
                        ? 'success'
                        : scan.status === 'running'
                        ? 'warning'
                        : scan.status === 'failed'
                        ? 'error'
                        : 'default'
                    }
                    size="small"
                  />
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      <Snackbar
        open={showSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowSnackbar(false)}
      >
        <Alert onClose={() => setShowSnackbar(false)} severity="info">
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}
