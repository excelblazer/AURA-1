import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  TextField
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Assignment as AssignmentIcon,
  Edit as EditIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';

const steps = ['Upload Files', 'Validation', 'Processing'];

function Validation() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validationData, setValidationData] = useState({
    issues: [],
    job_status: 'pending',
    files: {
      payroll: null,
      feedback: null
    }
  });
  const [editingIssue, setEditingIssue] = useState(null);
  const [resolution, setResolution] = useState('');
  const [processingJob, setProcessingJob] = useState(false);

  useEffect(() => {
    const fetchValidationData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch validation data
        const response = await axios.get(`/api/validation/${jobId}`);
        setValidationData(response.data);
        
      } catch (err) {
        console.error('Error fetching validation data:', err);
        setError(err.response?.data?.detail || 'Failed to load validation data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchValidationData();
    
    // Poll for updates every 5 seconds if job is still processing
    const intervalId = setInterval(() => {
      if (validationData.job_status === 'processing') {
        fetchValidationData();
      }
    }, 5000);

    return () => clearInterval(intervalId);
  }, [jobId, validationData.job_status]);

  const handleResolveIssue = (issue) => {
    setEditingIssue(issue);
    setResolution('');
  };

  const handleCloseDialog = () => {
    setEditingIssue(null);
    setResolution('');
  };

  const handleSaveResolution = async () => {
    if (!resolution.trim()) {
      return;
    }

    try {
      setLoading(true);
      
      // Save resolution
      await axios.post(`/api/validation/resolve/${editingIssue.id}`, {
        resolution: resolution
      });
      
      // Refresh validation data
      const response = await axios.get(`/api/validation/${jobId}`);
      setValidationData(response.data);
      
      // Close dialog
      setEditingIssue(null);
      setResolution('');
      
    } catch (err) {
      console.error('Error resolving issue:', err);
      setError(err.response?.data?.detail || 'Failed to resolve issue. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleProceed = async () => {
    try {
      setProcessingJob(true);
      setError(null);
      
      // Start processing job
      const response = await axios.post(`/api/processing/start/${jobId}`);
      
      // Navigate to documents page
      navigate(`/documents/${jobId}`);
      
    } catch (err) {
      console.error('Error starting processing job:', err);
      setError(err.response?.data?.detail || 'Failed to start processing. Please try again.');
      setProcessingJob(false);
    }
  };

  const getIssueIcon = (severity) => {
    switch (severity) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <WarningIcon color="info" />;
    }
  };

  const getSeverityChip = (severity) => {
    switch (severity) {
      case 'error':
        return <Chip label="Error" color="error" size="small" />;
      case 'warning':
        return <Chip label="Warning" color="warning" size="small" />;
      default:
        return <Chip label={severity} size="small" />;
    }
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'resolved':
        return <Chip icon={<CheckCircleIcon />} label="Resolved" color="success" size="small" />;
      case 'pending':
        return <Chip label="Pending" color="warning" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  if (loading && !validationData.issues.length) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const hasUnresolvedErrors = validationData.issues.some(
    issue => issue.severity === 'error' && issue.status !== 'resolved'
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Validation
      </Typography>

      <Stepper activeStep={1} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Validation Issues
              </Typography>
              <Box>
                <Chip 
                  label={`Job ID: ${jobId}`} 
                  variant="outlined" 
                  sx={{ mr: 1 }} 
                />
                <Chip 
                  label={`Status: ${validationData.job_status}`} 
                  color={validationData.job_status === 'completed' ? 'success' : 'warning'} 
                />
              </Box>
            </Box>
            <Divider sx={{ mb: 3 }} />

            {validationData.issues.length === 0 ? (
              <Alert severity="success" sx={{ mb: 3 }}>
                No validation issues found. You can proceed to document generation.
              </Alert>
            ) : (
              <List>
                {validationData.issues.map((issue) => (
                  <Card 
                    key={issue.id} 
                    variant="outlined" 
                    sx={{ 
                      mb: 2,
                      borderLeft: '4px solid',
                      borderLeftColor: issue.status === 'resolved' 
                        ? 'success.main' 
                        : (issue.severity === 'error' ? 'error.main' : 'warning.main')
                    }}
                  >
                    <CardHeader
                      avatar={issue.status === 'resolved' ? <CheckCircleIcon color="success" /> : getIssueIcon(issue.severity)}
                      title={issue.message}
                      subheader={`${issue.location} | ${issue.category}`}
                      action={
                        <Box>
                          {getSeverityChip(issue.severity)}
                          {' '}
                          {getStatusChip(issue.status)}
                        </Box>
                      }
                    />
                    <CardContent>
                      <Typography variant="body2" color="textSecondary">
                        {issue.description}
                      </Typography>
                      
                      {issue.resolution && (
                        <Box sx={{ mt: 2, p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
                          <Typography variant="subtitle2">Resolution:</Typography>
                          <Typography variant="body2">{issue.resolution}</Typography>
                        </Box>
                      )}
                    </CardContent>
                    
                    {issue.status !== 'resolved' && (
                      <CardActions>
                        <Button 
                          size="small" 
                          startIcon={<EditIcon />}
                          onClick={() => handleResolveIssue(issue)}
                        >
                          Resolve
                        </Button>
                      </CardActions>
                    )}
                  </Card>
                ))}
              </List>
            )}

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
              <Button
                variant="outlined"
                color="secondary"
                sx={{ mr: 2 }}
                onClick={() => navigate('/upload')}
              >
                Back to Upload
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={processingJob ? <CircularProgress size={20} color="inherit" /> : <AssignmentIcon />}
                onClick={handleProceed}
                disabled={hasUnresolvedErrors || processingJob}
              >
                {processingJob ? 'Processing...' : 'Generate Documents'}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Resolution Dialog */}
      <Dialog open={!!editingIssue} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Resolve Issue
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            {editingIssue?.message}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="resolution"
            label="Resolution"
            type="text"
            fullWidth
            multiline
            rows={4}
            value={resolution}
            onChange={(e) => setResolution(e.target.value)}
            placeholder="Describe how you resolved this issue..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button 
            onClick={handleSaveResolution} 
            variant="contained" 
            color="primary"
            disabled={!resolution.trim()}
            startIcon={<CheckCircleIcon />}
          >
            Save Resolution
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Validation;
