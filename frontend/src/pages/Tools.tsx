import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Build as BuildIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useMutation } from 'react-query';
import { toolApi } from '../services/api';

interface ToolResult {
  task_id: string;
  tool: string;
  command: string;
  status: string;
  output?: string;
  parsed_data?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export default function Tools() {
  const [results, setResults] = useState<ToolResult[]>([]);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');

  const [toolForms, setToolForms] = useState({
    nmap: { target: '', options: '-sV -O' },
    nikto: { target: '', options: '' },
    hydra: { target: '', service: 'ssh', username: 'admin', password_list: '/usr/share/wordlists/rockyou.txt' },
    sqlmap: { target: '', options: '--forms --batch' },
    gobuster: { target: '', wordlist: '/usr/share/wordlists/dirb/common.txt' },
  });

  // Tool mutations
  const nmapMutation = useMutation(toolApi.runNmap, {
    onSuccess: (response) => {
      setResults(prev => [response.data, ...prev]);
      showMessage('Nmap scan completed!', 'success');
    },
    onError: () => showMessage('Nmap scan failed!', 'error'),
  });

  const niktoMutation = useMutation(toolApi.runNikto, {
    onSuccess: (response) => {
      setResults(prev => [response.data, ...prev]);
      showMessage('Nikto scan completed!', 'success');
    },
    onError: () => showMessage('Nikto scan failed!', 'error'),
  });

  const hydraMutation = useMutation(toolApi.runHydra, {
    onSuccess: (response) => {
      setResults(prev => [response.data, ...prev]);
      showMessage('Hydra attack completed!', 'success');
    },
    onError: () => showMessage('Hydra attack failed!', 'error'),
  });

  const sqlmapMutation = useMutation(toolApi.runSqlmap, {
    onSuccess: (response) => {
      setResults(prev => [response.data, ...prev]);
      showMessage('SQLMap test completed!', 'success');
    },
    onError: () => showMessage('SQLMap test failed!', 'error'),
  });

  const gobusterMutation = useMutation(toolApi.runGobuster, {
    onSuccess: (response) => {
      setResults(prev => [response.data, ...prev]);
      showMessage('Gobuster scan completed!', 'success');
    },
    onError: () => showMessage('Gobuster scan failed!', 'error'),
  });

  const showMessage = (message: string, severity: 'success' | 'error' | 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setShowSnackbar(true);
  };

  const handleToolSubmit = (tool: string) => {
    const form = toolForms[tool as keyof typeof toolForms];
    if (!form.target) {
      showMessage('Please enter a target', 'error');
      return;
    }

    switch (tool) {
      case 'nmap':
        nmapMutation.mutate({ target: form.target, options: form.options });
        break;
      case 'nikto':
        niktoMutation.mutate({ target: form.target, options: form.options });
        break;
      case 'hydra':
        hydraMutation.mutate({
          target: form.target,
          service: form.service,
          username: form.username,
          password_list: form.password_list,
        });
        break;
      case 'sqlmap':
        sqlmapMutation.mutate({ target: form.target, options: form.options });
        break;
      case 'gobuster':
        gobusterMutation.mutate({ target: form.target, wordlist: form.wordlist });
        break;
    }
  };

  const updateToolForm = (tool: string, field: string, value: string) => {
    setToolForms(prev => ({
      ...prev,
      [tool]: {
        ...prev[tool as keyof typeof prev],
        [field]: value,
      },
    }));
  };

  const ToolCard = ({ tool, title, description, icon, children }: any) => (
    <Card sx={{ mb: 2 }}>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" width="100%">
            <Box mr={2}>{icon}</Box>
            <Box flexGrow={1}>
              <Typography variant="h6">{title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {description}
              </Typography>
            </Box>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {children}
        </AccordionDetails>
      </Accordion>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Pentest Tools
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          {/* Nmap Tool */}
          <ToolCard
            tool="nmap"
            title="Nmap"
            description="Network mapper - port scanning and service detection"
            icon={<SecurityIcon />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target (IP/Domain)"
                  value={toolForms.nmap.target}
                  onChange={(e) => updateToolForm('nmap', 'target', e.target.value)}
                  placeholder="192.168.1.1"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Options"
                  value={toolForms.nmap.options}
                  onChange={(e) => updateToolForm('nmap', 'options', e.target.value)}
                  placeholder="-sV -O"
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={() => handleToolSubmit('nmap')}
                  disabled={nmapMutation.isLoading}
                >
                  Run Nmap
                </Button>
              </Grid>
            </Grid>
          </ToolCard>

          {/* Nikto Tool */}
          <ToolCard
            tool="nikto"
            title="Nikto"
            description="Web vulnerability scanner"
            icon={<SecurityIcon />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target URL"
                  value={toolForms.nikto.target}
                  onChange={(e) => updateToolForm('nikto', 'target', e.target.value)}
                  placeholder="http://192.168.1.1"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Options"
                  value={toolForms.nikto.options}
                  onChange={(e) => updateToolForm('nikto', 'options', e.target.value)}
                  placeholder=""
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={() => handleToolSubmit('nikto')}
                  disabled={niktoMutation.isLoading}
                >
                  Run Nikto
                </Button>
              </Grid>
            </Grid>
          </ToolCard>

          {/* Hydra Tool */}
          <ToolCard
            tool="hydra"
            title="Hydra"
            description="Brute force attack tool"
            icon={<BuildIcon />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target (IP)"
                  value={toolForms.hydra.target}
                  onChange={(e) => updateToolForm('hydra', 'target', e.target.value)}
                  placeholder="192.168.1.1"
                />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Service</InputLabel>
                  <Select
                    value={toolForms.hydra.service}
                    label="Service"
                    onChange={(e) => updateToolForm('hydra', 'service', e.target.value)}
                  >
                    <MenuItem value="ssh">SSH</MenuItem>
                    <MenuItem value="ftp">FTP</MenuItem>
                    <MenuItem value="http-post-form">HTTP POST</MenuItem>
                    <MenuItem value="mysql">MySQL</MenuItem>
                    <MenuItem value="telnet">Telnet</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Username"
                  value={toolForms.hydra.username}
                  onChange={(e) => updateToolForm('hydra', 'username', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Password List"
                  value={toolForms.hydra.password_list}
                  onChange={(e) => updateToolForm('hydra', 'password_list', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={() => handleToolSubmit('hydra')}
                  disabled={hydraMutation.isLoading}
                >
                  Run Hydra
                </Button>
              </Grid>
            </Grid>
          </ToolCard>
        </Grid>

        <Grid item xs={12} md={6}>
          {/* SQLMap Tool */}
          <ToolCard
            tool="sqlmap"
            title="SQLMap"
            description="SQL injection testing tool"
            icon={<SecurityIcon />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target URL"
                  value={toolForms.sqlmap.target}
                  onChange={(e) => updateToolForm('sqlmap', 'target', e.target.value)}
                  placeholder="http://192.168.1.1/login.php"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Options"
                  value={toolForms.sqlmap.options}
                  onChange={(e) => updateToolForm('sqlmap', 'options', e.target.value)}
                  placeholder="--forms --batch"
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={() => handleToolSubmit('sqlmap')}
                  disabled={sqlmapMutation.isLoading}
                >
                  Run SQLMap
                </Button>
              </Grid>
            </Grid>
          </ToolCard>

          {/* Gobuster Tool */}
          <ToolCard
            tool="gobuster"
            title="Gobuster"
            description="Directory/file brute forcer"
            icon={<AssessmentIcon />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target URL"
                  value={toolForms.gobuster.target}
                  onChange={(e) => updateToolForm('gobuster', 'target', e.target.value)}
                  placeholder="http://192.168.1.1"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Wordlist"
                  value={toolForms.gobuster.wordlist}
                  onChange={(e) => updateToolForm('gobuster', 'wordlist', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={() => handleToolSubmit('gobuster')}
                  disabled={gobusterMutation.isLoading}
                >
                  Run Gobuster
                </Button>
              </Grid>
            </Grid>
          </ToolCard>
        </Grid>
      </Grid>

      {/* Results Section */}
      {results.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Tool Results
          </Typography>
          {results.map((result, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    {result.tool.toUpperCase()} - {result.command}
                  </Typography>
                  <Chip
                    label={result.status}
                    color={
                      result.status === 'completed'
                        ? 'success'
                        : result.status === 'failed'
                        ? 'error'
                        : 'default'
                    }
                  />
                </Box>
                {result.output && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Output:
                    </Typography>
                    <Box
                      component="pre"
                      sx={{
                        backgroundColor: '#f5f5f5',
                        p: 2,
                        borderRadius: 1,
                        overflow: 'auto',
                        maxHeight: 300,
                        fontSize: '0.875rem',
                      }}
                    >
                      {result.output}
                    </Box>
                  </Box>
                )}
                {result.error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {result.error}
                  </Alert>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

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
