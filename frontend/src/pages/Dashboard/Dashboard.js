import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as TemplateIcon,
  Assignment as JobIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Pending as PendingIcon
} from '@mui/icons-material';

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    recentJobs: [],
    pendingValidations: 0,
    completedJobs: 0,
    templates: 0
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch dashboard data from API
        const response = await axios.get('/api/dashboard');
        setStats(response.data);
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusChip = (status) => {
    switch (status) {
      case 'completed':
        return <Chip icon={<SuccessIcon />} label="Completed" color="success" size="small" />;
      case 'pending':
        return <Chip icon={<PendingIcon />} label="Pending" color="warning" size="small" />;
      case 'failed':
        return <Chip icon={<ErrorIcon />} label="Failed" color="error" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<UploadIcon />}
                  onClick={() => navigate('/upload')}
                >
                  Upload Files
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<TemplateIcon />}
                  onClick={() => navigate('/templates')}
                >
                  Manage Templates
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<JobIcon />}
                  onClick={() => navigate('/documents')}
                >
                  View Documents
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        {/* Stats */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Pending Validations
                  </Typography>
                  <Typography variant="h3" component="div">
                    {stats.pendingValidations}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" onClick={() => navigate('/validation')}>
                    View All
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Completed Jobs
                  </Typography>
                  <Typography variant="h3" component="div">
                    {stats.completedJobs}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" onClick={() => navigate('/documents')}>
                    View Documents
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Templates
                  </Typography>
                  <Typography variant="h3" component="div">
                    {stats.templates}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" onClick={() => navigate('/templates')}>
                    Manage Templates
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
          
          {/* Recent Jobs */}
          <Paper sx={{ p: 2, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Jobs
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {stats.recentJobs.length > 0 ? (
              <List>
                {stats.recentJobs.map((job) => (
                  <ListItem
                    key={job.id}
                    button
                    onClick={() => navigate(`/documents/${job.id}`)}
                    secondaryAction={getStatusChip(job.status)}
                  >
                    <ListItemIcon>
                      <JobIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={job.name}
                      secondary={`Created: ${new Date(job.created_at).toLocaleString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary" align="center">
                No recent jobs found. Start by uploading files.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
