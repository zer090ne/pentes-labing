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
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { reportApi, scanApi } from '../services/api';
import { format } from 'date-fns';

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');

  const [reportForm, setReportForm] = useState({
    scan_id: '',
    report_type: 'html',
    title: '',
  });

  const queryClient = useQueryClient();

  // Fetch reports
  const { data: reports, isLoading } = useQuery(
    'reports',
    () => reportApi.getAll({ limit: 100 }),
    {
      select: (response) => response.data,
    }
  );

  // Fetch scans for dropdown
  const { data: scans } = useQuery(
    'scans',
    () => scanApi.getAll({ limit: 100 }),
    {
      select: (response) => response.data,
    }
  );

  // Fetch report details
  const { data: reportDetails } = useQuery(
    ['report', selectedReport?.id],
    () => reportApi.getById(selectedReport.id),
    {
      enabled: !!selectedReport,
      select: (response) => response.data,
    }
  );

  // Create report mutation
  const createReportMutation = useMutation(reportApi.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('reports');
      setCreateDialogOpen(false);
      setReportForm({ scan_id: '', report_type: 'html', title: '' });
      showMessage('Report created successfully!', 'success');
    },
    onError: () => {
      showMessage('Failed to create report', 'error');
    },
  });

  // Delete report mutation
  const deleteReportMutation = useMutation(reportApi.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('reports');
      setDeleteDialogOpen(false);
      setSelectedReport(null);
      showMessage('Report deleted successfully!', 'success');
    },
    onError: () => {
      showMessage('Failed to delete report', 'error');
    },
  });

  const showMessage = (message: string, severity: 'success' | 'error' | 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setShowSnackbar(true);
  };

  const handleCreateReport = () => {
    if (!reportForm.scan_id || !reportForm.title) {
      showMessage('Please fill in all required fields', 'error');
      return;
    }
    createReportMutation.mutate(reportForm);
  };

  const handleDeleteReport = (reportId: number) => {
    deleteReportMutation.mutate(reportId);
  };

  const handleViewReport = (report: any) => {
    setSelectedReport(report);
    setViewDialogOpen(true);
  };

  const handleDownloadReport = async (reportId: number) => {
    try {
      const response = await reportApi.download(reportId);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportId}.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showMessage('Report downloaded successfully!', 'success');
    } catch (error) {
      showMessage('Failed to download report', 'error');
    }
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'title', headerName: 'Title', width: 200 },
    { field: 'scan_id', headerName: 'Scan ID', width: 100 },
    {
      field: 'report_type',
      headerName: 'Type',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value.toUpperCase()}
          color="primary"
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
          onClick={() => handleViewReport(params.row)}
        />,
        <GridActionsCellItem
          icon={<DownloadIcon />}
          label="Download"
          onClick={() => handleDownloadReport(params.row.id)}
        />,
        <GridActionsCellItem
          icon={<DeleteIcon />}
          label="Delete"
          onClick={() => {
            setSelectedReport(params.row);
            setDeleteDialogOpen(true);
          }}
        />,
      ],
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Reports</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Generate Report
        </Button>
      </Box>

      <Card>
        <CardContent>
          <DataGrid
            rows={reports || []}
            columns={columns}
            loading={isLoading}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            disableSelectionOnClick
            autoHeight
          />
        </CardContent>
      </Card>

      {/* Create Report Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate New Report</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Select Scan</InputLabel>
                <Select
                  value={reportForm.scan_id}
                  label="Select Scan"
                  onChange={(e) => setReportForm({ ...reportForm, scan_id: e.target.value })}
                >
                  {scans?.map((scan: any) => (
                    <MenuItem key={scan.id} value={scan.id}>
                      {scan.name} - {scan.target} ({scan.status})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Report Title"
                value={reportForm.title}
                onChange={(e) => setReportForm({ ...reportForm, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Report Type</InputLabel>
                <Select
                  value={reportForm.report_type}
                  label="Report Type"
                  onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}
                >
                  <MenuItem value="html">HTML</MenuItem>
                  <MenuItem value="json">JSON</MenuItem>
                  <MenuItem value="xml">XML</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateReport}
            variant="contained"
            disabled={createReportMutation.isLoading}
          >
            Generate Report
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Report Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Report Details</DialogTitle>
        <DialogContent>
          {reportDetails && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Title</Typography>
                <Typography variant="body1">{reportDetails.title}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Type</Typography>
                <Chip
                  label={reportDetails.report_type.toUpperCase()}
                  color="primary"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Scan ID</Typography>
                <Typography variant="body1">{reportDetails.scan_id}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Created</Typography>
                <Typography variant="body1">
                  {format(new Date(reportDetails.created_at), 'MMM dd, yyyy HH:mm')}
                </Typography>
              </Grid>
              {reportDetails.content && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Content Preview:
                  </Typography>
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
                    {reportDetails.content.substring(0, 1000)}
                    {reportDetails.content.length > 1000 && '...'}
                  </Box>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          {selectedReport && (
            <Button
              onClick={() => handleDownloadReport(selectedReport.id)}
              variant="contained"
              startIcon={<DownloadIcon />}
            >
              Download
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Report</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the report "{selectedReport?.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => handleDeleteReport(selectedReport.id)}
            color="error"
            variant="contained"
            disabled={deleteReportMutation.isLoading}
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
