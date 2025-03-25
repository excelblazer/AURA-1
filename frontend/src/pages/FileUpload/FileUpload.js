import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckCircleIcon,
  Description as DescriptionIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

const steps = ['Upload Files', 'Validation', 'Processing'];

function FileUpload() {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [files, setFiles] = useState({
    payroll: null,
    feedback: null
  });
  const [jobId, setJobId] = useState(null);

  const onDropPayroll = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      setFiles(prev => ({
        ...prev,
        payroll: acceptedFiles[0]
      }));
    }
  }, []);

  const onDropFeedback = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      setFiles(prev => ({
        ...prev,
        feedback: acceptedFiles[0]
      }));
    }
  }, []);

  const { getRootProps: getPayrollRootProps, getInputProps: getPayrollInputProps, isDragActive: isPayrollDragActive } = useDropzone({
    onDrop: onDropPayroll,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1
  });

  const { getRootProps: getFeedbackRootProps, getInputProps: getFeedbackInputProps, isDragActive: isFeedbackDragActive } = useDropzone({
    onDrop: onDropFeedback,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!files.payroll || !files.feedback) {
      setError('Please upload both payroll and feedback files.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Create form data
      const formData = new FormData();
      formData.append('payroll_file', files.payroll);
      formData.append('feedback_file', files.feedback);

      // Upload files
      const response = await axios.post('/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Set job ID and move to next step
      setJobId(response.data.job_id);
      setActiveStep(1);

      // Navigate to validation page
      navigate(`/validation/${response.data.job_id}`);

    } catch (err) {
      console.error('Error uploading files:', err);
      setError(err.response?.data?.detail || 'Failed to upload files. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFile = (fileType) => {
    setFiles(prev => ({
      ...prev,
      [fileType]: null
    }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        File Upload
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
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
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Payroll File
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Upload the payroll Excel file containing hours worked by tutors.
            </Typography>

            {files.payroll ? (
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <DescriptionIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="body1" sx={{ flexGrow: 1 }}>
                      {files.payroll.name}
                    </Typography>
                    <Button 
                      color="error" 
                      size="small"
                      onClick={() => handleRemoveFile('payroll')}
                    >
                      Remove
                    </Button>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Size: {(files.payroll.size / 1024).toFixed(2)} KB
                  </Typography>
                </CardContent>
              </Card>
            ) : (
              <Box 
                {...getPayrollRootProps()} 
                className={`dropzone ${isPayrollDragActive ? 'active-dropzone' : ''}`}
                sx={{ 
                  border: '2px dashed #cccccc', 
                  borderRadius: 1, 
                  p: 3, 
                  textAlign: 'center',
                  cursor: 'pointer',
                  mb: 2,
                  '&:hover': {
                    borderColor: 'primary.main',
                  },
                  ...(isPayrollDragActive && {
                    borderColor: 'primary.main',
                    bgcolor: 'rgba(25, 118, 210, 0.05)',
                  }),
                }}
              >
                <input {...getPayrollInputProps()} />
                <UploadIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="body1" gutterBottom>
                  Drag & drop payroll file here, or click to select
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Accepted formats: .xlsx, .xls
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Feedback File
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Upload the feedback Excel file containing student attendance and progress data.
            </Typography>

            {files.feedback ? (
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <DescriptionIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="body1" sx={{ flexGrow: 1 }}>
                      {files.feedback.name}
                    </Typography>
                    <Button 
                      color="error" 
                      size="small"
                      onClick={() => handleRemoveFile('feedback')}
                    >
                      Remove
                    </Button>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Size: {(files.feedback.size / 1024).toFixed(2)} KB
                  </Typography>
                </CardContent>
              </Card>
            ) : (
              <Box 
                {...getFeedbackRootProps()} 
                className={`dropzone ${isFeedbackDragActive ? 'active-dropzone' : ''}`}
                sx={{ 
                  border: '2px dashed #cccccc', 
                  borderRadius: 1, 
                  p: 3, 
                  textAlign: 'center',
                  cursor: 'pointer',
                  mb: 2,
                  '&:hover': {
                    borderColor: 'primary.main',
                  },
                  ...(isFeedbackDragActive && {
                    borderColor: 'primary.main',
                    bgcolor: 'rgba(25, 118, 210, 0.05)',
                  }),
                }}
              >
                <input {...getFeedbackInputProps()} />
                <UploadIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="body1" gutterBottom>
                  Drag & drop feedback file here, or click to select
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Accepted formats: .xlsx, .xls
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              File Requirements
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Payroll File
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircleIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Must contain tutor names and hours worked" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircleIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Should include dates and times of sessions" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircleIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Excel format (.xlsx or .xls)" />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Feedback File
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircleIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Must contain student attendance records" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircleIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Should include progress notes and feedback" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircleIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Excel format (.xlsx or .xls)" />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AssignmentIcon />}
              onClick={handleUpload}
              disabled={!files.payroll || !files.feedback || loading}
              sx={{ minWidth: 150 }}
            >
              {loading ? 'Uploading...' : 'Upload Files'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}

export default FileUpload;
