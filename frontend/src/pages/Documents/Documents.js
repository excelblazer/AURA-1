import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  CircularProgress,
  Alert,
  Chip,
  Tabs,
  Tab,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Assignment as AssignmentIcon,
  AssignmentTurnedIn as AssignmentTurnedInIcon,
  AssignmentLate as AssignmentLateIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`documents-tabpanel-${index}`}
      aria-labelledby={`documents-tab-${index}`}
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

function Documents() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJob, setSelectedJob] = useState(jobId || null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
  }, [selectedJob]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch jobs
      const jobsResponse = await axios.get('/api/processing/jobs');
      setJobs(jobsResponse.data);
      
      // If no job is selected, select the most recent one
      if (!selectedJob && jobsResponse.data.length > 0) {
        setSelectedJob(jobsResponse.data[0].id);
      }
      
      // Fetch documents for selected job
      if (selectedJob) {
        const documentsResponse = await axios.get(`/api/processing/documents/${selectedJob}`);
        setDocuments(documentsResponse.data);
      } else {
        setDocuments([]);
      }
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.response?.data?.detail || 'Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const handleDownload = async (documentId) => {
    try {
      // Get document download URL
      const response = await axios.get(`/api/processing/documents/${selectedJob}/${documentId}/download`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get document info to set filename
      const document = documents.find(doc => doc.id === documentId);
      link.setAttribute('download', document.filename || 'document.docx');
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      
    } catch (err) {
      console.error('Error downloading document:', err);
      setError('Failed to download document. Please try again.');
    }
  };

  const handlePreview = async (documentId) => {
    try {
      // Open document preview in new tab
      window.open(`/api/processing/documents/${selectedJob}/${documentId}/preview`, '_blank');
    } catch (err) {
      console.error('Error previewing document:', err);
      setError('Failed to preview document. Please try again.');
    }
  };

  const getJobStatusChip = (status) => {
    switch (status) {
      case 'completed':
        return <Chip icon={<AssignmentTurnedInIcon />} label="Completed" color="success" size="small" />;
      case 'processing':
        return <Chip icon={<AssignmentIcon />} label="Processing" color="warning" size="small" />;
      case 'failed':
        return <Chip icon={<AssignmentLateIcon />} label="Failed" color="error" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const getDocumentTypeIcon = (type) => {
    switch (type) {
      case 'attendance_record':
        return <DescriptionIcon color="primary" />;
      case 'progress_report':
        return <DescriptionIcon color="secondary" />;
      case 'invoice':
        return <DescriptionIcon color="info" />;
      case 'service_log':
        return <DescriptionIcon color="success" />;
      default:
        return <DescriptionIcon />;
    }
  };

  const filteredDocuments = documents.filter(doc => 
    doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const documentsByType = {
    attendance_record: filteredDocuments.filter(doc => doc.type === 'attendance_record'),
    progress_report: filteredDocuments.filter(doc => doc.type === 'progress_report'),
    invoice: filteredDocuments.filter(doc => doc.type === 'invoice'),
    service_log: filteredDocuments.filter(doc => doc.type === 'service_log')
  };

  if (loading && !refreshing && documents.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Documents
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? <CircularProgress size={24} /> : 'Refresh'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ mb: 3 }}>
            <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                Processing Jobs
              </Typography>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => navigate('/upload')}
              >
                New Upload
              </Button>
            </Box>
            <Divider />
            <List sx={{ maxHeight: '300px', overflow: 'auto' }}>
              {jobs.length === 0 ? (
                <ListItem>
                  <ListItemText
                    primary="No processing jobs found"
                    secondary="Upload files to start processing"
                  />
                </ListItem>
              ) : (
                jobs.map((job) => (
                  <ListItem
                    key={job.id}
                    button
                    selected={selectedJob === job.id}
                    onClick={() => setSelectedJob(job.id)}
                  >
                    <ListItemIcon>
                      <AssignmentIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={`Job #${job.id}`}
                      secondary={`Created: ${new Date(job.created_at).toLocaleString()}`}
                    />
                    <ListItemSecondaryAction>
                      {getJobStatusChip(job.status)}
                    </ListItemSecondaryAction>
                  </ListItem>
                ))
              )}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                indicatorColor="primary"
                textColor="primary"
              >
                <Tab label="All Documents" />
                <Tab label="Attendance Records" />
                <Tab label="Progress Reports" />
                <Tab label="Invoices" />
                <Tab label="Service Logs" />
              </Tabs>
            </Box>

            <Box sx={{ p: 2 }}>
              <TextField
                fullWidth
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>

            <TabPanel value={tabValue} index={0}>
              <DocumentList 
                documents={filteredDocuments} 
                onDownload={handleDownload} 
                onPreview={handlePreview}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={1}>
              <DocumentList 
                documents={documentsByType.attendance_record} 
                onDownload={handleDownload} 
                onPreview={handlePreview}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={2}>
              <DocumentList 
                documents={documentsByType.progress_report} 
                onDownload={handleDownload} 
                onPreview={handlePreview}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={3}>
              <DocumentList 
                documents={documentsByType.invoice} 
                onDownload={handleDownload} 
                onPreview={handlePreview}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={4}>
              <DocumentList 
                documents={documentsByType.service_log} 
                onDownload={handleDownload} 
                onPreview={handlePreview}
              />
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function DocumentList({ documents, onDownload, onPreview }) {
  if (documents.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <DescriptionIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="textSecondary" gutterBottom>
          No Documents Found
        </Typography>
        <Typography variant="body2" color="textSecondary">
          No documents match your search criteria.
        </Typography>
      </Box>
    );
  }

  const getDocumentTypeChip = (type) => {
    switch (type) {
      case 'attendance_record':
        return <Chip label="Attendance Record" color="primary" size="small" />;
      case 'progress_report':
        return <Chip label="Progress Report" color="secondary" size="small" />;
      case 'invoice':
        return <Chip label="Invoice" color="info" size="small" />;
      case 'service_log':
        return <Chip label="Service Log" color="success" size="small" />;
      default:
        return <Chip label={type} size="small" />;
    }
  };

  return (
    <Grid container spacing={2}>
      {documents.map((document) => (
        <Grid item xs={12} sm={6} md={4} key={document.id}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DescriptionIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
                  {document.name}
                </Typography>
                {getDocumentTypeChip(document.type)}
              </Box>
              <Typography variant="body2" color="textSecondary" noWrap>
                {document.filename}
              </Typography>
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Created: {new Date(document.created_at).toLocaleString()}
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => onDownload(document.id)}
              >
                Download
              </Button>
              <Button
                size="small"
                startIcon={<VisibilityIcon />}
                onClick={() => onPreview(document.id)}
              >
                Preview
              </Button>
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default Documents;
