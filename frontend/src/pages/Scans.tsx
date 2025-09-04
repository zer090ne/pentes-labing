import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { scanApi } from '../services/api';
import { format } from 'date-fns';
import AIAnalysis from '../components/AIAnalysis';

export default function Scans() {
  const [selectedScan, setSelectedScan] = useState<any>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');

  const [scanForm, setScanForm] = useState({
    name: '',
    target: '',
    scan_type: 'nmap',
    description: '',
  });

  const queryClient = useQueryClient();

  // Fetch scans
  const { data: scans, isLoading } = useQuery(
    'scans',
    () => scanApi.getAll({ limit: 100 }),
    {
      select: (response) => response.data,
    }
  );

  // Fetch scan details
  const { data: scanDetails } = useQuery(
    ['scan', selectedScan?.id],
    () => scanApi.getById(selectedScan.id),
    {
      enabled: !!selectedScan,
      select: (response) => response.data,
    }
  );

  // Create scan mutation
  const createScanMutation = useMutation(scanApi.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('scans');
      setCreateDialogOpen(false);
      setScanForm({ name: '', target: '', scan_type: 'nmap', description: '' });
      showMessage('Scan created successfully!', 'success');
    },
    onError: () => {
      showMessage('Failed to create scan', 'error');
    },
  });

  // Stop scan mutation
  const stopScanMutation = useMutation(scanApi.stop, {
    onSuccess: () => {
      queryClient.invalidateQueries('scans');
      showMessage('Scan stopped successfully!', 'success');
    },
    onError: () => {
      showMessage('Failed to stop scan', 'error');
    },
  });

  // Delete scan mutation
  const deleteScanMutation = useMutation(scanApi.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('scans');
      setDeleteDialogOpen(false);
      setSelectedScan(null);
      showMessage('Scan deleted successfully!', 'success');
    },
    onError: () => {
      showMessage('Failed to delete scan', 'error');
    },
  });

  const showMessage = (message: string, severity: 'success' | 'error' | 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setShowSnackbar(true);
  };

  const handleCreateScan = () => {
    if (!scanForm.name || !scanForm.target) {
      showMessage('Please fill in all required fields', 'error');
      return;
    }
    createScanMutation.mutate(scanForm);
  };

  const handleStopScan = (scanId: number) => {
    stopScanMutation.mutate(scanId);
  };

  const handleDeleteScan = (scanId: number) => {
    deleteScanMutation.mutate(scanId);
  };

  const handleViewScan = (scan: any) => {
    setSelectedScan(scan);
    setViewDialogOpen(true);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: 'Name', width: 200 },
    { field: 'target', headerName: 'Target', width: 150 },
    { field: 'scan_type', headerName: 'Type', width: 120 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={
            params.value === 'completed'
              ? 'success'
              : params.value === 'running'
              ? 'warning'
              : params.value === 'failed'
              ? 'error'
              : 'default'
          }
          size="small"
        />
      ),
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      renderCell: (params) => format(new Date(params.value), 'MMM dd, yyyy HH:mm'),
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 150,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<ViewIcon />}
          label="View"
          onClick={() => handleViewScan(params.row)}
        />,
        ...(params.row.status === 'running'
          ? [
              <GridActionsCellItem
                icon={<StopIcon />}
                label="Stop"
                onClick={() => handleStopScan(params.row.id)}
              />,
            ]
          : []),
        <GridActionsCellItem
          icon={<DeleteIcon />}
          label="Delete"
          onClick={() => {
            setSelectedScan(params.row);
            setDeleteDialogOpen(true);
          }}
        />,
      ],
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Scans</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          New Scan
        </Button>
      </Box>

      <Card>
        <CardContent>
          <DataGrid
            rows={scans || []}
            columns={columns}
            loading={isLoading}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            disableSelectionOnClick
            autoHeight
          />
        </CardContent>
      </Card>

      {/* Create Scan Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Scan</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scan Name"
                value={scanForm.name}
                onChange={(e) => setScanForm({ ...scanForm, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target (IP/Domain)"
                value={scanForm.target}
                onChange={(e) => setScanForm({ ...scanForm, target: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Scan Type</InputLabel>
                <Select
                  value={scanForm.scan_type}
                  label="Scan Type"
                  onChange={(e) => setScanForm({ ...scanForm, scan_type: e.target.value })}
                >
                  <MenuItem value="nmap">Nmap (Port Scan)</MenuItem>
                  <MenuItem value="nikto">Nikto (Web Vulnerability)</MenuItem>
                  <MenuItem value="comprehensive">Comprehensive</MenuItem>
                  <MenuItem value="hydra">Hydra (Brute Force)</MenuItem>
                  <MenuItem value="sqlmap">SQLMap (SQL Injection)</MenuItem>
                  <MenuItem value="gobuster">Gobuster (Directory Enum)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={scanForm.description}
                onChange={(e) => setScanForm({ ...scanForm, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateScan}
            variant="contained"
            disabled={createScanMutation.isLoading}
          >
            Create Scan
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Scan Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Scan Details</DialogTitle>
        <DialogContent>
          {scanDetails && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Name</Typography>
                <Typography variant="body1">{scanDetails.name}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Target</Typography>
                <Typography variant="body1">{scanDetails.target}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Type</Typography>
                <Typography variant="body1">{scanDetails.scan_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Status</Typography>
                <Chip
                  label={scanDetails.status}
                  color={
                    scanDetails.status === 'completed'
                      ? 'success'
                      : scanDetails.status === 'running'
                      ? 'warning'
                      : scanDetails.status === 'failed'
                      ? 'error'
                      : 'default'
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Created</Typography>
                <Typography variant="body1">
                  {format(new Date(scanDetails.created_at), 'MMM dd, yyyy HH:mm')}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Completed</Typography>
                <Typography variant="body1">
                  {scanDetails.completed_at
                    ? format(new Date(scanDetails.completed_at), 'MMM dd, yyyy HH:mm')
                    : 'N/A'}
                </Typography>
              </Grid>
            </Grid>
            
            {/* AI Analysis Section */}
            {scanDetails.status === 'completed' && (
              <Box sx={{ mt: 3 }}>
                <AIAnalysis scanId={scanDetails.id} />
              </Box>
            )}
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Scan</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the scan "{selectedScan?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => handleDeleteScan(selectedScan.id)}
            color="error"
            variant="contained"
            disabled={deleteScanMutation.isLoading}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

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
